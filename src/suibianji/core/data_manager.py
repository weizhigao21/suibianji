import base64
import importlib.util
import json
import logging
import os
import secrets
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .models import AccountPassword, AIPrompt, Idea, RecordManager, WalletAddress

# keyring 延迟导入:只在真正读写系统钥匙串时才加载(可省约 0.1s 启动时间)
_keyring_module = None
_keyring_state: bool | None = None


def _load_keyring():
    global _keyring_module, _keyring_state
    if _keyring_state is None:
        try:
            import keyring
            _keyring_module = keyring
            _keyring_state = True
        except Exception:
            _keyring_module = None
            _keyring_state = False
    return _keyring_module


def keyring_available() -> bool:
    """是否可用系统钥匙串;未加载前只检查模块是否存在。"""
    if _keyring_state is None:
        return importlib.util.find_spec("keyring") is not None
    return _keyring_state


logger = logging.getLogger(__name__)

# keyring 凭据标识
KEYRING_SERVICE = "suibianji"
KEYRING_USERNAME = "master_password"


# 主密码派生参数
PBKDF2_ITERATIONS = 600_000
# 滚动备份保留份数(每次保存前生成一份,超出后删除最旧的)
BACKUP_KEEP = 7
# 验证 token:用派生密钥加密此固定字符串,解密后匹配则密码正确
VERIFICATION_TOKEN = b"SUIBIANJI_VERIFICATION_TOKEN_v1"


class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "records.enc"
        self.backup_file = self.data_dir / "records.enc.bak"
        self.backups_dir = self.data_dir / "backups"
        self.salt_file = self.data_dir / ".salt"
        self.verify_file = self.data_dir / ".verify"
        self.legacy_key_file = self.data_dir / ".key"
        self.cipher: Fernet | None = None
        self.record_manager: RecordManager | None = None
        # 上次改密若在写文件中途崩溃,这里先回滚到改密前的完整状态
        self._recover_interrupted_password_change()

    # ---------- 密钥派生 ----------
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """用主密码 + salt 派生 Fernet 密钥。"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))

    def _generate_salt(self) -> bytes:
        return secrets.token_bytes(16)

    # ---------- 底层 IO ----------
    def _read_bytes(self, path: Path) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def _atomic_write(self, path: Path, data: bytes):
        """原子写入:写临时文件 + fsync + os.replace,避免崩溃导致数据损坏。"""
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    # ---------- 主密码设置 / 验证 ----------
    def _write_verification(self):
        """写入验证 token(用当前 cipher 加密)。"""
        token = self.cipher.encrypt(VERIFICATION_TOKEN)
        self._atomic_write(self.verify_file, token)

    def verify_password(self, password: str) -> bool:
        """验证主密码是否正确。"""
        if not self.salt_file.exists() or not self.verify_file.exists():
            return False
        try:
            salt = self._read_bytes(self.salt_file)
            key = self._derive_key(password, salt)
            cipher = Fernet(key)
            token = self._read_bytes(self.verify_file)
            return cipher.decrypt(token) == VERIFICATION_TOKEN
        except (InvalidToken, Exception):
            return False

    # ---------- keyring 缓存主密码 ----------
    @classmethod
    def is_keyring_available(cls) -> bool:
        return keyring_available()

    def cache_password(self, password: str) -> bool:
        """将主密码存入系统钥匙串。"""
        keyring = _load_keyring()
        if keyring is None:
            return False
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, password)
            return True
        except Exception:
            return False

    def get_cached_password(self) -> str | None:
        """从系统钥匙串读取主密码。"""
        keyring = _load_keyring()
        if keyring is None:
            return None
        try:
            return keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        except Exception:
            return None

    def clear_cached_password(self) -> bool:
        """从系统钥匙串删除主密码。"""
        keyring = _load_keyring()
        if keyring is None:
            return False
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
            return True
        except Exception:
            return False

    def _setup_new_password(self, password: str):
        """为新主密码生成 salt + 验证 token,并设置 self.cipher。"""
        salt = self._generate_salt()
        self._atomic_write(self.salt_file, salt)
        self.cipher = Fernet(self._derive_key(password, salt))
        self._write_verification()

    # ---------- 修改主密码 ----------
    def _snapshot_for_rollback(self) -> Path:
        """把当前加密文件整套复制到 backup-时间戳,改密失败/中断时用于还原。"""
        snapshot = self.data_dir / f"backup-{datetime.now():%Y%m%d-%H%M%S}"
        snapshot.mkdir(exist_ok=True)
        for path in (self.salt_file, self.verify_file, self.data_file, self.backup_file):
            if path.exists():
                shutil.copy2(path, snapshot / path.name)
        return snapshot

    def _restore_snapshot(self, snapshot: Path):
        for name in (self.salt_file.name, self.verify_file.name,
                     self.data_file.name, self.backup_file.name):
            source = snapshot / name
            if source.exists():
                shutil.copy2(source, self.data_dir / name)

    def _recover_interrupted_password_change(self):
        """启动时若发现改密中断(journal 残留),还原到改密前的状态。"""
        journal = self.data_dir / ".password-change"
        if not journal.exists():
            return
        try:
            info = json.loads(journal.read_text(encoding="utf-8"))
            snapshot = self.data_dir / info["backup"]
            if snapshot.is_dir():
                self._restore_snapshot(snapshot)
                logger.warning("检测到未完成的改密操作,已回滚到 %s", snapshot.name)
        except Exception as e:
            logger.warning("改密回滚失败,请从备份目录手动恢复: %s", e)
        finally:
            journal.unlink(missing_ok=True)

    def change_password(self, old_password: str, new_password: str) -> bool:
        """校验旧密码后更换主密码,重新加密整库;失败自动回滚。"""
        if not self.verify_password(old_password):
            return False
        if len(new_password) < 8:
            raise ValueError("新主密码至少需要 8 个字符")
        if self.record_manager is None:
            raise RuntimeError("数据尚未解锁,无法修改主密码")

        snapshot = self._snapshot_for_rollback()
        journal = self.data_dir / ".password-change"
        journal.write_text(json.dumps({"backup": snapshot.name}), encoding="utf-8")
        try:
            payload = json.dumps(self.record_manager.to_dict(),
                                 ensure_ascii=False, indent=2).encode("utf-8")
            salt = self._generate_salt()
            cipher = Fernet(self._derive_key(new_password, salt))
            encrypted = cipher.encrypt(payload)
            token = cipher.encrypt(VERIFICATION_TOKEN)
            # 先自检:新密钥必须能解回同样的数据
            if json.loads(cipher.decrypt(encrypted).decode("utf-8")) != self.record_manager.to_dict():
                raise RuntimeError("改密自检失败,已保留原数据")

            self._atomic_write(self.data_file, encrypted)
            self._atomic_write(self.verify_file, token)
            self._atomic_write(self.salt_file, salt)
            self.cipher = cipher
            journal.unlink(missing_ok=True)
            return True
        except Exception:
            self._restore_snapshot(snapshot)
            journal.unlink(missing_ok=True)
            raise

    # ---------- 启动入口 ----------
    def has_legacy_key(self) -> bool:
        """是否使用旧版 .key 密钥文件模式(无需主密码)。"""
        return self.legacy_key_file.exists() and not self.salt_file.exists()

    def is_first_time(self) -> bool:
        """是否首次使用(既无 salt 也无 legacy key)。"""
        return not self.salt_file.exists() and not self.legacy_key_file.exists()

    def initialize_with_legacy_key(self):
        """用 .key 直接解密并加载数据,写入时保持同样的密钥文件格式。"""
        key = self._read_bytes(self.legacy_key_file).strip()
        self.cipher = Fernet(key)
        self._load_data()

    def import_legacy_data(self, source_dir, replace: bool = False) -> bool:
        """把旧版 data 目录的 .key / records.enc 复制到当前目录。

        replace=True 时先把当前目录的加密数据移到 backup-时间戳 子目录,
        避免覆盖用户已有记录。
        """
        source = Path(source_dir)
        source_key = source / ".key"
        if not source_key.exists():
            return False
        if not replace and (self.salt_file.exists() or self.legacy_key_file.exists()):
            return False

        if replace and (self.salt_file.exists() or self.data_file.exists()):
            backup_dir = self.data_dir / f"backup-{datetime.now():%Y%m%d-%H%M%S}"
            backup_dir.mkdir(exist_ok=True)
            for path in (self.salt_file, self.verify_file, self.data_file, self.backup_file):
                if path.exists():
                    shutil.move(str(path), str(backup_dir / path.name))

        self._atomic_write(self.legacy_key_file, source_key.read_bytes())
        source_records = source / "records.enc"
        if source_records.exists():
            self._atomic_write(self.data_file, source_records.read_bytes())
        source_backup = source / "records.enc.bak"
        if source_backup.exists():
            self._atomic_write(self.backup_file, source_backup.read_bytes())
        return True

    def initialize_first_time(self, password: str):
        """首次使用:设置主密码并写入空记录。"""
        self._setup_new_password(password)
        self.record_manager = RecordManager()
        self._save_data()

    def initialize_with_password(self, password: str):
        """已验证密码后,加载数据。"""
        salt = self._read_bytes(self.salt_file)
        self.cipher = Fernet(self._derive_key(password, salt))
        self._load_data()

    # ---------- 数据加载/保存 ----------
    def _load_data(self):
        """按 主文件 → .bak → 滚动备份(由新到旧) 的顺序尝试解密。"""
        last_error: Exception | None = None
        for path in self._candidate_files():
            if not path.exists():
                continue
            try:
                encrypted = self._read_bytes(path)
                decrypted = self.cipher.decrypt(encrypted)
                data = json.loads(decrypted.decode("utf-8"))
                self.record_manager = RecordManager.from_dict(data)
            except Exception as e:
                last_error = e
                continue
            if path != self.data_file:
                logger.warning("主文件不可用(%s),已从 %s 恢复", last_error, path.name)
            return

        if self.data_file.exists():
            raise ValueError(f"数据解密失败:密钥不匹配或文件已损坏 ({last_error})")
        self.record_manager = RecordManager()

    def _candidate_files(self):
        """可用于恢复的文件,按优先级排列。"""
        candidates = [self.data_file, self.backup_file]
        candidates.extend(sorted(self.backups_dir.glob("records-*.enc"), reverse=True)
                          if self.backups_dir.exists() else [])
        return candidates

    def _write_rotating_backup(self, payload: bytes):
        """把当前密文另存为带时间戳的备份,并清理超出保留份数的旧备份。"""
        backups = sorted(self.backups_dir.glob("records-*.enc"), reverse=True)
        self.backups_dir.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        self._atomic_write(self.backups_dir / f"records-{stamp}.enc", payload)
        for old in backups[BACKUP_KEEP - 1:]:
            try:
                old.unlink()
            except OSError:
                pass

    def _save_data(self):
        data = self.record_manager.to_dict()
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        encrypted = self.cipher.encrypt(json_data.encode("utf-8"))
        # 先备份当前文件(.bak + 时间戳滚动备份),再原子写入新数据
        if self.data_file.exists():
            try:
                current = self._read_bytes(self.data_file)
                self._atomic_write(self.backup_file, current)
                self._write_rotating_backup(current)
            except Exception as e:
                logger.warning("写入备份失败,继续保存主文件: %s", e)
        self._atomic_write(self.data_file, encrypted)

    # ---------- 备份管理 ----------
    def list_backups(self):
        """按时间倒序列出滚动备份。"""
        if not self.backups_dir.exists():
            return []
        return sorted(self.backups_dir.glob("records-*.enc"), reverse=True)

    def create_backup(self) -> Path | None:
        """手动备份当前密文;尚无数据文件时返回 None。"""
        if not self.data_file.exists():
            return None
        self.backups_dir.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        target = self.backups_dir / f"records-{stamp}.enc"
        index = 1
        while target.exists():
            target = self.backups_dir / f"records-{stamp}-{index}.enc"
            index += 1
        shutil.copy2(self.data_file, target)
        return target

    def restore_backup(self, source) -> bool:
        """恢复到指定备份;恢复前把当前状态另存一份,失败不动原数据。"""
        source = Path(source)
        if not source.exists() or self.cipher is None:
            return False
        try:
            payload = self.cipher.decrypt(self._read_bytes(source))
            json.loads(payload.decode("utf-8"))
        except Exception as e:
            logger.warning("备份文件无法解密: %s", e)
            raise ValueError("该备份与当前主密码不匹配或已损坏") from e

        self.create_backup()
        rollback = self.data_dir / f"backup-{datetime.now():%Y%m%d-%H%M%S}"
        rollback.mkdir(exist_ok=True)
        if self.data_file.exists():
            shutil.copy2(self.data_file, rollback / self.data_file.name)

        self._atomic_write(self.data_file, self._read_bytes(source))
        self._load_data()
        return True

    # ---------- CRUD ----------
    def add_account(self, account_type: str, website: str, username: str, password: str,
                    url: str | None = None, notes: str | None = None,
                    totp_secret: str = "") -> AccountPassword:
        account = AccountPassword(
            id=str(uuid.uuid4()),
            account_type=account_type,
            website=website,
            username=username,
            password=password,
            url=url,
            notes=notes,
            totp_secret=totp_secret,
        )
        self.record_manager.accounts.append(account)
        self._save_data()
        return account

    def update_account(self, account_id: str, **kwargs) -> AccountPassword | None:
        for account in self.record_manager.accounts:
            if account.id == account_id:
                for key, value in kwargs.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                account.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return account
        return None

    def delete_account(self, account_id: str) -> bool:
        before = len(self.record_manager.accounts)
        self.record_manager.accounts = [
            acc for acc in self.record_manager.accounts if acc.id != account_id
        ]
        if len(self.record_manager.accounts) != before:
            self._save_data()
            return True
        return False

    def add_idea(self, title: str, content: str, tags: list = None) -> Idea:
        idea = Idea(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            tags=tags or []
        )
        self.record_manager.ideas.append(idea)
        self._save_data()
        return idea

    def update_idea(self, idea_id: str, **kwargs) -> Idea | None:
        for idea in self.record_manager.ideas:
            if idea.id == idea_id:
                for key, value in kwargs.items():
                    if hasattr(idea, key):
                        setattr(idea, key, value)
                idea.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return idea
        return None

    def delete_idea(self, idea_id: str) -> bool:
        before = len(self.record_manager.ideas)
        self.record_manager.ideas = [
            idea for idea in self.record_manager.ideas if idea.id != idea_id
        ]
        if len(self.record_manager.ideas) != before:
            self._save_data()
            return True
        return False

    def add_wallet(self, name: str, address: str, wallet_type: str,
                   notes: str | None = None) -> WalletAddress:
        wallet = WalletAddress(
            id=str(uuid.uuid4()),
            name=name,
            address=address,
            wallet_type=wallet_type,
            notes=notes
        )
        self.record_manager.wallets.append(wallet)
        self._save_data()
        return wallet

    def update_wallet(self, wallet_id: str, **kwargs) -> WalletAddress | None:
        for wallet in self.record_manager.wallets:
            if wallet.id == wallet_id:
                for key, value in kwargs.items():
                    if hasattr(wallet, key):
                        setattr(wallet, key, value)
                wallet.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return wallet
        return None

    def delete_wallet(self, wallet_id: str) -> bool:
        before = len(self.record_manager.wallets)
        self.record_manager.wallets = [
            wallet for wallet in self.record_manager.wallets if wallet.id != wallet_id
        ]
        if len(self.record_manager.wallets) != before:
            self._save_data()
            return True
        return False

    def add_prompt(self, title: str, content: str, category: str = "",
                   tags: list = None) -> AIPrompt:
        prompt = AIPrompt(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            category=category,
            tags=tags or []
        )
        self.record_manager.prompts.append(prompt)
        self._save_data()
        return prompt

    def update_prompt(self, prompt_id: str, **kwargs) -> AIPrompt | None:
        for prompt in self.record_manager.prompts:
            if prompt.id == prompt_id:
                for key, value in kwargs.items():
                    if hasattr(prompt, key):
                        setattr(prompt, key, value)
                prompt.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return prompt
        return None

    def delete_prompt(self, prompt_id: str) -> bool:
        before = len(self.record_manager.prompts)
        self.record_manager.prompts = [
            prompt for prompt in self.record_manager.prompts if prompt.id != prompt_id
        ]
        if len(self.record_manager.prompts) != before:
            self._save_data()
            return True
        return False
