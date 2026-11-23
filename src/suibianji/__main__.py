"""应用入口:日志、旧数据导入、登录流程与主窗口启动。"""

import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# 尽量贴近进程启动的时刻,用于统计导入 + 建窗耗时
_BOOT_T0 = time.perf_counter()

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from .core.data_manager import DataManager
from .core.paths import resolve_data_dir
from .core.settings import AppSettings
from .core.single_instance import SingleInstanceGuard, socket_name
from .ui.app_icon import app_icon
from .ui.main_window import PasswordDialog, SuibianjiApp

# 旧版密钥文件数据目录:启动时自动导入,保持 .key + records.enc 格式兼容
LEGACY_DATA_DIR = Path(r"C:\DIY\suibinaji\data")


def _try_auto_login(data_manager: DataManager, app_settings: "AppSettings") -> str | None:
    """若开启记住密码且仍在有效期内,尝试从 keyring 自动登录。"""
    if not app_settings.remember_password_enabled:
        return None
    if not app_settings.is_remember_period_valid():
        return None
    cached = data_manager.get_cached_password()
    if cached and data_manager.verify_password(cached):
        try:
            data_manager.initialize_with_password(cached)
            app_settings.refresh_remember_period()
            return cached
        except Exception:
            return None
    return None


def _prompt_and_login(data_manager: DataManager, app_settings: "AppSettings",
                      mode: str = PasswordDialog.MODE_VERIFY) -> str | None:
    """弹出密码对话框,登录成功后按设置决定是否缓存密码。"""
    dialog = PasswordDialog(mode, data_manager)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    password = dialog.get_password()
    try:
        if mode == PasswordDialog.MODE_SETUP and data_manager.is_first_time():
            data_manager.initialize_first_time(password)
        else:
            data_manager.initialize_with_password(password)
    except Exception as e:
        QMessageBox.critical(None, "加载失败", f"数据加载失败: {e}")
        sys.exit(1)

    if app_settings.remember_password_enabled:
        data_manager.cache_password(password)
        app_settings.refresh_remember_period()
    return password


def _setup_logging(log_dir: Path | None = None):
    """配置日志:输出到数据目录下的 suibianji.log(打包后仍可见)和 stderr。"""
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    try:
        log_dir = Path(log_dir) if log_dir else Path("data")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "suibianji.log", maxBytes=512 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except Exception:
        pass  # 日志文件不可写时静默,不影响启动
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    root.addHandler(stream_handler)


def _import_legacy_if_needed(data_manager: DataManager):
    """兼容旧版 .key 数据:本地未初始化时自动导入,已有数据时询问一次。"""
    if not (LEGACY_DATA_DIR / ".key").exists():
        return
    if data_manager.has_legacy_key():
        return
    if data_manager.is_first_time():
        data_manager.import_legacy_data(LEGACY_DATA_DIR)
        return

    skipped_marker = data_manager.data_dir / ".legacy-import-skipped"
    if skipped_marker.exists():
        return

    answer = QMessageBox.question(
        None, "导入旧版数据",
        "检测到旧版密钥格式数据:\n"
        f"{LEGACY_DATA_DIR}\n\n"
        "是否导入到当前 data 目录?导入后将沿用 .key 密钥文件格式,无需主密码。\n"
        "当前主密码加密的数据会先备份到 data\\backup-时间戳,可随时找回。",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    if answer == QMessageBox.StandardButton.Yes:
        data_manager.import_legacy_data(LEGACY_DATA_DIR, replace=True)
    else:
        skipped_marker.write_text("skipped", encoding="utf-8")


def main():
    started = _BOOT_T0
    data_dir = resolve_data_dir()
    _setup_logging(data_dir)
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setWindowIcon(app_icon())
    log = logging.getLogger("suibianji.startup")
    log.info("启动阶段: imports+Qt %d ms", int((time.perf_counter() - started) * 1000))
    # 密码解锁/旧数据导入耗时
    boot_after_qt = time.perf_counter()

    # 单实例:第二个进程唤醒第一个后直接退出,避免两个进程互相覆盖数据
    window_holder: dict[str, Any] = {}

    def _activate_existing():
        window = window_holder.get("window")
        if window is None:
            return
        if window.isMinimized():
            window.showNormal()
        window.activate_from_instance()

    guard = SingleInstanceGuard(socket_name(data_dir), _activate_existing)
    if not guard.acquire():
        return 0

    data_manager = DataManager(str(data_dir))
    app_settings = AppSettings(str(data_dir))

    # 旧版 .key 数据兼容
    _import_legacy_if_needed(data_manager)

    # 启动密码流程:密钥文件模式 / 首次设置 / 验证(优先自动登录)
    # 登录成功后保留主密码到内存,供"设置中开启免密登录"立即缓存到 keyring
    if data_manager.has_legacy_key():
        try:
            data_manager.initialize_with_legacy_key()
        except Exception as e:
            QMessageBox.critical(None, "加载失败", f"旧版数据解密失败: {e}")
            sys.exit(1)
        password = None
    elif data_manager.is_first_time():
        password = _prompt_and_login(data_manager, app_settings, PasswordDialog.MODE_SETUP)
    else:
        password = _try_auto_login(data_manager, app_settings)
        if password is None:
            password = _prompt_and_login(data_manager, app_settings, PasswordDialog.MODE_VERIFY)

    # 用户取消或关闭密码对话框时必须退出,未解锁不允许进入主界面
    if not data_manager.cipher:
        sys.exit(0)

    window = SuibianjiApp(data_manager, app_settings, current_password=password)
    window_holder["window"] = window
    unlock_ms = int((time.perf_counter() - boot_after_qt) * 1000)
    log.info(
        "启动阶段: 解锁+数据+建窗 %d ms, 合计 %d ms",
        unlock_ms,
        int((time.perf_counter() - started) * 1000),
    )
    window.show()
    log.info("启动阶段: 窗口显示 %d ms", int((time.perf_counter() - started) * 1000))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
