"""锁定流程测试:.key 密钥模式不能被要求输入主密码。"""
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from cryptography.fernet import Fernet
from PyQt6.QtWidgets import QApplication

from suibianji.core.data_manager import DataManager
from suibianji.core.models import RecordManager
from suibianji.core.settings import AppSettings
from suibianji.ui.main_window import SuibianjiApp


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def legacy_window(qapp, tmp_path):
    from suibianji.core.models import AccountPassword

    key = Fernet.generate_key()
    (tmp_path / ".key").write_bytes(key)
    records = RecordManager()
    records.accounts.append(
        AccountPassword(id="a1", website="example.com", username="alice", password="pw")
    )
    (tmp_path / "records.enc").write_bytes(Fernet(key).encrypt(json.dumps(records.to_dict()).encode("utf-8")))
    dm = DataManager(str(tmp_path))
    dm.initialize_with_legacy_key()

    window = SuibianjiApp(dm, AppSettings(str(tmp_path)))
    window.show()
    qapp.processEvents()
    yield window
    window._force_quit = True
    window.close()
    window.deleteLater()
    qapp.processEvents()


def test_key_mode_lock_does_not_ask_password(qapp, legacy_window):
    window = legacy_window
    window.lock()
    qapp.processEvents()
    assert window._key_mode_locked is True
    assert window.data_manager.cipher is None
    assert window.data_manager.record_manager is None
    assert not window.isVisible()
    assert window.table.rowCount() == 0


def test_key_mode_unlock_from_tray_without_input(qapp, legacy_window):
    window = legacy_window
    window.lock()
    qapp.processEvents()
    window._show_from_tray()
    qapp.processEvents()
    assert window._key_mode_locked is False
    assert window.data_manager.record_manager is not None
    assert window.table.rowCount() == 1
    assert window.isVisible()
