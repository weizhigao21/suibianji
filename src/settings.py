import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


DEFAULT_REMEMBER_HOURS = 24
# until 与 now 的最大允许间隔(小时),超出视为篡改或时钟错乱
# 留出 DEFAULT_REMEMBER_HOURS 续期窗口 + 时钟偏差余量
MAX_REMEMBER_WINDOW_HOURS = 48

DEFAULT_ACCOUNT_TYPES = [
    "邮箱",
    "视频",
    "论坛",
    "社交",
    "购物",
    "工作",
    "其他",
]


class AppSettings:
    """应用设置管理,持久化 JSON。"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.settings_file = self.data_dir / "settings.json"
        self._load()

    def _load(self):
        defaults = {
            "remember_password_enabled": False,
            "remember_password_until": None,
            "account_types": list(DEFAULT_ACCOUNT_TYPES),
        }
        if self.settings_file.exists():
            try:
                stored = json.loads(self.settings_file.read_text(encoding="utf-8"))
                if not isinstance(stored, dict):
                    stored = {}
            except Exception:
                stored = {}
        else:
            stored = {}
        defaults.update(stored)
        self._data = defaults

    def _save(self):
        self._atomic_write(self.settings_file, json.dumps(self._data, ensure_ascii=False, indent=2))

    @staticmethod
    def _atomic_write(path: Path, text: str):
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    # ---------- 记住密码 ----------
    @property
    def remember_password_enabled(self) -> bool:
        return bool(self._data.get("remember_password_enabled", False))

    @remember_password_enabled.setter
    def remember_password_enabled(self, value: bool):
        self._data["remember_password_enabled"] = bool(value)
        if not self._data["remember_password_enabled"]:
            # 关闭时同时清掉有效期
            self._data["remember_password_until"] = None
        self._save()

    def is_remember_period_valid(self) -> bool:
        """记住密码功能开启,且仍在有效期内,且时间戳未被异常延长。"""
        if not self.remember_password_enabled:
            return False
        until_str = self._data.get("remember_password_until")
        if not until_str:
            return False
        try:
            until = datetime.fromisoformat(until_str)
            now = datetime.now()
            # 必须未过期
            if now >= until:
                return False
            # 防篡改:until 距 now 不得超过最大窗口,否则视为篡改/时钟错乱
            if until - now > timedelta(hours=MAX_REMEMBER_WINDOW_HOURS):
                return False
            return True
        except Exception:
            return False

    def refresh_remember_period(self, hours: Optional[int] = None):
        """登录成功/开启记住密码时刷新有效期。"""
        if not self.remember_password_enabled:
            return
        hours = hours or DEFAULT_REMEMBER_HOURS
        until = datetime.now() + timedelta(hours=hours)
        self._data["remember_password_until"] = until.isoformat()
        self._save()

    def clear_remember_period(self):
        """登出/清除缓存时调用。"""
        self._data["remember_password_until"] = None
        self._save()

    # ---------- 账号类型 ----------
    @property
    def account_types(self) -> list:
        types = self._data.get("account_types")
        if not isinstance(types, list) or not types:
            return list(DEFAULT_ACCOUNT_TYPES)
        return [str(t).strip() for t in types if str(t).strip()]

    @account_types.setter
    def account_types(self, value: list):
        cleaned = [str(v).strip() for v in value if str(v).strip()]
        # 保证"其他"始终存在
        if "其他" not in cleaned:
            cleaned.append("其他")
        self._data["account_types"] = cleaned
        self._save()
