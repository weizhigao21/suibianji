"""数据目录解析。

优先级:
1. 环境变量 SUIBIANJI_DATA_DIR(便于测试、多库切换)
2. 程序所在目录旁的 data/(便携模式,兼容已有安装)
3. %APPDATA%/Suibianji/data(安装目录不可写的场景,如 Program Files)

绝不再依赖当前工作目录(CWD),避免从快捷方式、任务栏或其他目录启动时
把数据写到一个没人知道的角落。
"""

import os
import sys
from pathlib import Path

APP_NAME = "Suibianji"
DATA_DIRNAME = "data"
ENV_OVERRIDE = "SUIBIANJI_DATA_DIR"


def app_dir() -> Path:
    """程序所在目录:打包后是 exe 所在目录,源码运行时是项目根目录。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _is_writable(directory: Path) -> bool:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def resolve_data_dir() -> Path:
    override = os.environ.get(ENV_OVERRIDE)
    if override:
        target = Path(override).expanduser()
        target.mkdir(parents=True, exist_ok=True)
        return target

    portable = app_dir() / DATA_DIRNAME
    # 已有数据目录:沿用,保证老用户升级后原样打开自己的库
    if portable.is_dir() and any(portable.iterdir()):
        return portable
    if _is_writable(portable):
        return portable

    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / ".local" / "share"
    fallback = base / APP_NAME / DATA_DIRNAME
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback
