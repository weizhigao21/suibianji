"""全局热键(Windows 优先,其他平台自动降级为无热键)。

使用 RegisterHotKey + QAbstractNativeEventFilter,不依赖第三方库。
"""

import ctypes
import logging
import sys

from PyQt6.QtCore import QAbstractNativeEventFilter

logger = logging.getLogger(__name__)

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
VK_SPACE = 0x20

DEFAULT_MODIFIERS = MOD_CONTROL | MOD_ALT
DEFAULT_VK = VK_SPACE

VK_J = 0x4A

# 依次尝试的候选组合:部分机器上 Ctrl+Alt+Space 会被输入法/其他工具占用
HOTKEY_CANDIDATES = (
    ("Ctrl+Alt+Space", MOD_CONTROL | MOD_ALT, VK_SPACE),
    ("Ctrl+Shift+Space", MOD_CONTROL | MOD_SHIFT, VK_SPACE),
    ("Ctrl+Alt+J", MOD_CONTROL | MOD_ALT, VK_J),
)


if sys.platform == "win32":
    class _POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    class _MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd", ctypes.c_void_p),
            ("message", ctypes.c_uint),
            ("wParam", ctypes.c_void_p),
            ("lParam", ctypes.c_void_p),
            ("time", ctypes.c_uint),
            ("pt", _POINT),
        ]


class GlobalHotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback
        self._registered = False
        self._hotkey_id = 1

    def register(self, modifiers: int = DEFAULT_MODIFIERS, vk: int = DEFAULT_VK) -> bool:
        if sys.platform != "win32":
            return False
        try:
            ok = ctypes.windll.user32.RegisterHotKey(None, self._hotkey_id, modifiers, vk)
        except OSError as e:
            logger.warning("注册全局热键失败: %s", e)
            return False
        self._registered = bool(ok)
        if not self._registered:
            logger.warning("全局热键已被其他程序占用(Ctrl+Alt+Space)")
        return self._registered

    def register_candidates(self) -> str | None:
        """按候选列表依次尝试注册,返回成功的组合名。"""
        for name, modifiers, vk in HOTKEY_CANDIDATES:
            if self.register(modifiers, vk):
                logger.info("全局热键已注册: %s", name)
                return name
        logger.warning("所有候选全局热键均被占用,仅保留托盘入口")
        return None

    def unregister(self):
        if sys.platform == "win32" and self._registered:
            try:
                ctypes.windll.user32.UnregisterHotKey(None, self._hotkey_id)
            except OSError:
                pass
            self._registered = False

    def nativeEventFilter(self, event_type, message):
        if sys.platform != "win32":
            return False, 0
        if event_type not in (b"windows_generic_MSG", b"windows_dispatcher_MSG"):
            return False, 0
        try:
            msg = _MSG.from_address(int(message))
        except (TypeError, ValueError):
            return False, 0
        if msg.message == WM_HOTKEY and msg.wParam == self._hotkey_id:
            self._callback()
            return True, 0
        return False, 0
