"""settings 模块测试:免密登录有效期、账号类型管理。"""
from settings import AppSettings


def test_settings_defaults(tmp_path):
    s = AppSettings(data_dir=str(tmp_path))
    assert s.remember_password_enabled is False
    assert not s.is_remember_period_valid()


def test_remember_password_period(tmp_path):
    s = AppSettings(data_dir=str(tmp_path))
    s.remember_password_enabled = True
    s.refresh_remember_period(hours=1)
    assert s.is_remember_period_valid()
    s.clear_remember_period()
    assert not s.is_remember_period_valid()


def test_disabling_remember_clears_period(tmp_path):
    """关闭免密登录时应同时清除有效期。"""
    s = AppSettings(data_dir=str(tmp_path))
    s.remember_password_enabled = True
    s.refresh_remember_period(hours=1)
    assert s.is_remember_period_valid()
    s.remember_password_enabled = False
    assert not s.is_remember_period_valid()


def test_account_types_always_keep_others(tmp_path):
    s = AppSettings(data_dir=str(tmp_path))
    s.account_types = ["邮箱", "自定义"]
    assert "其他" in s.account_types
    assert "邮箱" in s.account_types
    assert "自定义" in s.account_types


def test_account_types_persist(tmp_path):
    s = AppSettings(data_dir=str(tmp_path))
    s.account_types = ["邮箱", "自定义"]
    s2 = AppSettings(data_dir=str(tmp_path))
    assert "自定义" in s2.account_types
    assert "其他" in s2.account_types


def test_account_types_strip_blanks(tmp_path):
    s = AppSettings(data_dir=str(tmp_path))
    s.account_types = ["  邮箱  ", "", "论坛"]
    assert "邮箱" in s.account_types
    assert "" not in s.account_types
    assert "其他" in s.account_types


# ---------- until 上限校验(防篡改) ----------
def test_remember_period_rejects_far_future_until(tmp_path):
    """防篡改:until 被改成很远的未来应拒绝(超出 MAX_REMEMBER_WINDOW_HOURS)。"""
    from datetime import datetime, timedelta
    from settings import MAX_REMEMBER_WINDOW_HOURS
    assert MAX_REMEMBER_WINDOW_HOURS == 48  # 锁定常量,防止误改

    s = AppSettings(data_dir=str(tmp_path))
    s.remember_password_enabled = True
    # 篡改 until 为 1 年后(远超 48h 窗口)
    far_future = datetime.now() + timedelta(days=365)
    s._data["remember_password_until"] = far_future.isoformat()
    s._save()
    assert not s.is_remember_period_valid()


def test_remember_period_accepts_normal_window(tmp_path):
    """正常 24h 续期窗口应在 48h 上限内通过。"""
    s = AppSettings(data_dir=str(tmp_path))
    s.remember_password_enabled = True
    s.refresh_remember_period(hours=24)
    assert s.is_remember_period_valid()


def test_remember_period_rejects_just_over_window(tmp_path):
    """恰好超出窗口(49h)应拒绝。"""
    from datetime import datetime, timedelta
    s = AppSettings(data_dir=str(tmp_path))
    s.remember_password_enabled = True
    until = datetime.now() + timedelta(hours=49)
    s._data["remember_password_until"] = until.isoformat()
    s._save()
    assert not s.is_remember_period_valid()
