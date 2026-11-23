"""全局热键模块的轻量测试(不实际注册系统热键)。"""
from suibianji.core.hotkey import HOTKEY_CANDIDATES, GlobalHotkeyFilter


def test_candidates_are_well_formed():
    assert HOTKEY_CANDIDATES[0][0] == "Ctrl+Alt+Space"
    for name, modifiers, vk in HOTKEY_CANDIDATES:
        assert isinstance(name, str) and name
        assert modifiers > 0 and vk > 0


def test_unregister_without_register_is_safe():
    hk = GlobalHotkeyFilter(lambda: None)
    hk.unregister()
    assert hk._registered is False
