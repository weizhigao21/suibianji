"""data_manager 模块测试:加解密往返、CRUD、备份恢复、迁移、#1 回归。"""
import json

import pytest
from cryptography.fernet import Fernet

from suibianji.core.data_manager import DataManager
from suibianji.core.models import AccountPassword, RecordManager


# ---------- 主密码设置 / 验证 ----------
def test_first_time_setup_and_verify(data_manager):
    assert data_manager.is_first_time()
    data_manager.initialize_first_time("mypassword123")
    assert not data_manager.is_first_time()
    assert data_manager.verify_password("mypassword123")
    assert not data_manager.verify_password("wrong-password")


def test_verify_password_returns_false_when_not_setup(data_manager):
    assert not data_manager.verify_password("anything")


def test_wrong_password_load_raises(data_manager):
    data_manager.initialize_first_time("correct-pw")
    dm2 = DataManager(data_dir=data_manager.data_dir)
    with pytest.raises(Exception):  # noqa: B017 故意验证"密码错误必须抛出"
        dm2.initialize_with_password("wrong-pw")


# ---------- 加解密往返 ----------
def test_save_load_roundtrip(data_manager):
    data_manager.initialize_first_time("mypassword123")
    data_manager.add_account("邮箱", "example.com", "user1", "secret123",
                              url="http://example.com", notes="my note")
    data_manager.add_idea("标题", "内容", ["tag1"])
    data_manager.add_wallet("wallet", "0xabc", "ETH")
    data_manager.add_prompt("p", "content", "分类")

    dm2 = DataManager(data_dir=data_manager.data_dir)
    dm2.initialize_with_password("mypassword123")

    acc = dm2.record_manager.accounts[0]
    assert acc.password == "secret123"
    assert acc.url == "http://example.com"
    assert acc.notes == "my note"
    assert dm2.record_manager.ideas[0].tags == ["tag1"]
    assert dm2.record_manager.wallets[0].address == "0xabc"
    assert dm2.record_manager.prompts[0].category == "分类"


# ---------- #1 回归:accounts 的 password/notes 不能丢失 ----------
def test_account_password_not_overwritten_by_url(data_manager):
    """防止 accounts 新增时 password 被错填为 url、notes 丢失(历史 Bug)。"""
    data_manager.initialize_first_time("mypassword123")
    data_manager.add_account("邮箱", "example.com", "user1", "secret123",
                              url="http://example.com", notes="my note")
    loaded = data_manager.record_manager.accounts[0]
    assert loaded.password == "secret123"
    assert loaded.url == "http://example.com"
    assert loaded.notes == "my note"


def test_account_update_preserves_password_and_notes(data_manager):
    data_manager.initialize_first_time("mypassword123")
    acc = data_manager.add_account("邮箱", "w", "u", "old_pwd", url="http://x", notes="n")
    data_manager.update_account(acc.id, password="new_pwd", notes="new note", url="http://y")
    loaded = data_manager.record_manager.accounts[0]
    assert loaded.password == "new_pwd"
    assert loaded.notes == "new note"
    assert loaded.url == "http://y"


def test_accounts_edit_fields_contains_password_and_notes():
    """UI 配置契约:accounts 的 edit_fields 必须包含 password/notes,
    防止 _add_item/_edit_item 再次用表格显示字段组装参数。"""
    try:
        from suibianji.ui.main_window import SuibianjiApp
    except ImportError:
        pytest.skip("PyQt6 不可用,跳过 UI 配置测试")

    config = SuibianjiApp.CATEGORY_CONFIG["accounts"]
    assert "password" in config["edit_fields"], "accounts edit_fields 必须包含 password"
    assert "notes" in config["edit_fields"], "accounts edit_fields 必须包含 notes"
    # password 不应出现在表格显示字段(避免界面泄露)
    display_fields = [f[0] for f in config["fields"]]
    assert "password" not in display_fields, "password 不应在表格显示字段中"


# ---------- CRUD ----------
def test_crud_account(data_manager):
    data_manager.initialize_first_time("pw123456")
    acc = data_manager.add_account("邮箱", "w", "u", "p")
    assert len(data_manager.record_manager.accounts) == 1
    data_manager.update_account(acc.id, website="new")
    assert data_manager.record_manager.accounts[0].website == "new"
    assert data_manager.delete_account(acc.id)
    assert len(data_manager.record_manager.accounts) == 0


def test_crud_idea_wallet_prompt(data_manager):
    data_manager.initialize_first_time("pw123456")
    idea = data_manager.add_idea("t", "c", ["tag"])
    wallet = data_manager.add_wallet("n", "0x", "ETH")
    prompt = data_manager.add_prompt("t", "c", "cat")

    data_manager.update_idea(idea.id, title="new")
    data_manager.update_wallet(wallet.id, address="0xnew")
    data_manager.update_prompt(prompt.id, category="new-cat")

    assert data_manager.record_manager.ideas[0].title == "new"
    assert data_manager.record_manager.wallets[0].address == "0xnew"
    assert data_manager.record_manager.prompts[0].category == "new-cat"


def test_delete_nonexistent_returns_false(data_manager):
    data_manager.initialize_first_time("pw123456")
    assert not data_manager.delete_account("nonexistent-id")


def test_update_nonexistent_returns_none(data_manager):
    data_manager.initialize_first_time("pw123456")
    assert data_manager.update_account("nonexistent", website="x") is None


# ---------- 备份恢复 ----------
def test_backup_recovery_on_corrupt_main(data_manager):
    """主文件损坏时,应能从备份恢复(备份是上一次成功写入的状态)。"""
    data_manager.initialize_first_time("pw123456")
    data_manager.add_account("邮箱", "w1", "u1", "p1")
    data_manager.add_account("邮箱", "w2", "u2", "p2")
    # 此刻 data_file 含 2 accounts, .bak 含第一次 add 后的状态(1 account: u1/p1)
    data_manager.data_file.write_bytes(b"corrupt-data")

    dm2 = DataManager(data_dir=data_manager.data_dir)
    dm2.initialize_with_password("pw123456")
    assert len(dm2.record_manager.accounts) == 1
    assert dm2.record_manager.accounts[0].username == "u1"
    assert dm2.record_manager.accounts[0].password == "p1"


# ---------- 旧版 .key 密钥格式兼容 ----------
def test_legacy_key_mode_keeps_format(data_manager):
    """旧版 .key 数据应能免密打开,写回后仍保持 .key 格式。"""
    legacy_key = Fernet.generate_key()
    data_manager._atomic_write(data_manager.legacy_key_file, legacy_key)
    legacy_cipher = Fernet(legacy_key)

    rm = RecordManager()
    rm.accounts.append(AccountPassword(
        id="1", website="w", username="u", password="legacy_pw"))
    payload = json.dumps(rm.to_dict(), ensure_ascii=False).encode("utf-8")
    data_manager._atomic_write(data_manager.data_file, legacy_cipher.encrypt(payload))

    assert data_manager.has_legacy_key()
    data_manager.initialize_with_legacy_key()
    assert data_manager.record_manager.accounts[0].password == "legacy_pw"

    # 写入后仍是旧版可读的格式:保留 .key,不生成 salt
    data_manager.add_idea("新想法", "内容")
    assert data_manager.legacy_key_file.exists()
    assert not data_manager.salt_file.exists()
    saved = json.loads(legacy_cipher.decrypt(data_manager.data_file.read_bytes()).decode("utf-8"))
    assert saved["ideas"][0]["title"] == "新想法"


def test_import_legacy_data(data_manager, tmp_path):
    """首次启动应能把旧目录的 .key + records.enc 导入本地 data。"""
    source = tmp_path / "old_data"
    source.mkdir()
    key = Fernet.generate_key()
    (source / ".key").write_bytes(key)
    payload = json.dumps({
        "accounts": [],
        "ideas": [{"id": "1", "title": "旧想法", "content": "c", "tags": [],
                   "created_at": "", "updated_at": ""}],
        "wallets": [],
        "prompts": [],
    }, ensure_ascii=False).encode("utf-8")
    (source / "records.enc").write_bytes(Fernet(key).encrypt(payload))

    assert data_manager.is_first_time()
    assert data_manager.import_legacy_data(source)
    assert data_manager.has_legacy_key()

    data_manager.initialize_with_legacy_key()
    assert data_manager.record_manager.ideas[0].title == "旧想法"

    # 已初始化后不再重复导入
    assert not data_manager.import_legacy_data(source)


def test_import_legacy_data_replaces_with_backup(data_manager, tmp_path):
    """已有主密码数据时导入旧数据,应先把旧文件移到 backup 目录。"""
    data_manager.initialize_first_time("mypassword123")
    data_manager.add_account("工作", "site", "user", "pw")

    source = tmp_path / "old_data"
    source.mkdir()
    key = Fernet.generate_key()
    (source / ".key").write_bytes(key)
    (source / "records.enc").write_bytes(Fernet(key).encrypt(b'{"accounts": [], "ideas": [], "wallets": [], "prompts": []}'))

    assert data_manager.import_legacy_data(source, replace=True)
    assert data_manager.has_legacy_key()
    assert not data_manager.salt_file.exists()

    backups = list(data_manager.data_dir.glob("backup-*"))
    assert backups and (backups[0] / "records.enc").exists()


# ---------- 滚动备份 ----------
def test_rolling_backup_keeps_latest_copies(data_manager):
    """每次保存都应生成一份时间戳备份,且数量被限制在 BACKUP_KEEP。"""
    from suibianji.core.data_manager import BACKUP_KEEP

    data_manager.initialize_first_time("pw123456")
    for i in range(BACKUP_KEEP + 5):
        data_manager.add_idea(f"标题{i}", f"内容{i}")

    backups = sorted((data_manager.data_dir / "backups").glob("records-*.enc"))
    assert len(backups) == BACKUP_KEEP

    # 最新两份备份之间:后一份记录数应不少于前一份
    dm2 = DataManager(data_dir=data_manager.data_dir)
    dm2.initialize_with_password("pw123456")
    assert len(dm2.record_manager.ideas) == BACKUP_KEEP + 5


def test_recovery_from_rotating_backup_when_main_and_bak_corrupt(data_manager):
    """主文件与 .bak 同时损坏时,应能从滚动备份恢复。"""
    data_manager.initialize_first_time("pw123456")
    data_manager.add_account("邮箱", "w1", "u1", "p1")
    data_manager.add_account("邮箱", "w2", "u2", "p2")

    data_manager.data_file.write_bytes(b"corrupt")
    data_manager.backup_file.write_bytes(b"corrupt")

    dm2 = DataManager(data_dir=data_manager.data_dir)
    dm2.initialize_with_password("pw123456")
    # 最新的滚动备份是第二次写入前的状态(1 条)
    assert len(dm2.record_manager.accounts) == 1
    assert dm2.record_manager.accounts[0].username == "u1"


# ---------- 修改主密码 ----------
def test_change_password_roundtrip(data_manager):
    data_manager.initialize_first_time("old-password")
    data_manager.add_account("邮箱", "w", "u", "keepme")

    assert data_manager.change_password("old-password", "new-password-2026")
    assert not data_manager.verify_password("old-password")

    dm2 = DataManager(data_dir=data_manager.data_dir)
    dm2.initialize_with_password("new-password-2026")
    assert dm2.record_manager.accounts[0].password == "keepme"


def test_change_password_rejects_wrong_old(data_manager):
    data_manager.initialize_first_time("old-password")
    assert not data_manager.change_password("wrong", "another-password")
    assert data_manager.verify_password("old-password")


def test_change_password_rejects_short_new(data_manager):
    data_manager.initialize_first_time("old-password")
    with pytest.raises(ValueError):
        data_manager.change_password("old-password", "short")


def test_change_password_rolls_back_on_failure(data_manager, monkeypatch):
    """写文件失败时必须回滚,旧密码仍能打开原数据。"""
    data_manager.initialize_first_time("old-password")
    data_manager.add_account("邮箱", "w", "u", "keepme")

    failing = {"armed": True}
    original = DataManager._atomic_write

    def flaky(self, path, payload):
        if failing["armed"] and path == self.salt_file:
            raise OSError("disk full")
        return original(self, path, payload)

    monkeypatch.setattr(DataManager, "_atomic_write", flaky)
    with pytest.raises(OSError):
        data_manager.change_password("old-password", "new-password-2026")

    failing["armed"] = False
    dm2 = DataManager(data_dir=data_manager.data_dir)
    dm2.initialize_with_password("old-password")
    assert dm2.record_manager.accounts[0].password == "keepme"


def test_interrupted_password_change_is_rolled_back(data_manager):
    """journal 残留(改密中途崩溃)时,启动阶段应回滚到改密前状态。"""
    data_manager.initialize_first_time("old-password")
    data_manager.add_account("邮箱", "w", "u", "keepme")

    snapshot = data_manager.data_dir / "backup-20260101-000000"
    snapshot.mkdir()
    for path in (data_manager.salt_file, data_manager.verify_file, data_manager.data_file):
        (snapshot / path.name).write_bytes(path.read_bytes())

    journal = data_manager.data_dir / ".password-change"
    journal.write_text(json.dumps({"backup": snapshot.name}), encoding="utf-8")
    # 模拟写到一半:主文件被破坏
    data_manager.data_file.write_bytes(b"half-written")

    dm2 = DataManager(data_dir=data_manager.data_dir)
    assert not journal.exists()
    dm2.initialize_with_password("old-password")
    assert dm2.record_manager.accounts[0].password == "keepme"


# ---------- 手动备份与恢复 ----------
def test_manual_backup_then_restore(data_manager):
    data_manager.initialize_first_time("pw123456")
    data_manager.add_account("邮箱", "w1", "u1", "p1")

    backup = data_manager.create_backup()
    assert backup is not None and backup.exists()

    data_manager.add_account("邮箱", "w2", "u2", "p2")
    assert len(data_manager.record_manager.accounts) == 2

    assert data_manager.restore_backup(backup)
    assert len(data_manager.record_manager.accounts) == 1
    assert data_manager.record_manager.accounts[0].username == "u1"


def test_restore_rejects_corrupt_backup(data_manager):
    data_manager.initialize_first_time("pw123456")
    data_manager.add_account("邮箱", "w1", "u1", "p1")
    backup = data_manager.create_backup()

    backup.write_bytes(b"not-a-valid-token")
    with pytest.raises(ValueError):
        data_manager.restore_backup(backup)
    # 原数据不受影响
    assert len(data_manager.record_manager.accounts) == 1


def test_restore_keeps_current_state_copy(data_manager):
    data_manager.initialize_first_time("pw123456")
    data_manager.add_account("邮箱", "w1", "u1", "p1")
    backup = data_manager.create_backup()
    data_manager.add_account("邮箱", "w2", "u2", "p2")

    assert data_manager.restore_backup(backup)
    backups = list(data_manager.data_dir.glob("backup-*"))
    assert backups, "恢复前应把当前状态另存一份"
    assert any((b / "records.enc").exists() for b in backups)
