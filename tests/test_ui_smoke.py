"""界面冒烟测试:加载、搜索、类型筛选、右键选中行、复制密码。"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QApplication, QMenu

from suibianji.core.data_manager import DataManager
from suibianji.core.settings import AppSettings
from suibianji.ui.main_window import SuibianjiApp


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def window(qapp, tmp_path):
    dm = DataManager(str(tmp_path))
    dm.initialize_first_time("pw123456")
    dm.add_account("邮箱", "example.com", "alice", "secret-a")
    dm.add_account("工作", "gitlab.com", "alice.wei", "secret-b")
    settings = AppSettings(str(tmp_path))
    win = SuibianjiApp(dm, settings, current_password="pw123456")
    win.show()
    qapp.processEvents()
    yield win
    win.close()
    win.deleteLater()
    qapp.processEvents()


def test_table_shows_all_records(qapp, window):
    assert window.table.rowCount() == 2


def test_search_filters_rows(qapp, window):
    window.search_input.setText("gitlab")
    qapp.processEvents()
    assert window.table.rowCount() == 1
    window.search_input.clear()
    qapp.processEvents()
    assert window.table.rowCount() == 2


def test_type_filter_combines_with_search(qapp, window):
    window.type_filter.setCurrentIndex(1)  # 第一类是"邮箱"
    qapp.processEvents()
    assert window.table.rowCount() == 1
    window.search_input.setText("gitlab")
    qapp.processEvents()
    assert window.table.rowCount() == 0


def test_context_menu_selects_row_under_cursor(qapp, window, monkeypatch):
    # 先选第 0 行,再在第二行上右键,确认操作对象跟随鼠标位置
    window.table.selectRow(0)
    monkeypatch.setattr(QMenu, "exec", lambda self, *args, **kwargs: None)
    rect = window.table.visualItemRect(window.table.item(1, 0))
    window._show_context_menu(QPoint(rect.center().x(), rect.center().y()))
    assert window.table.currentRow() == 1


def test_copy_password_and_auto_clear(qapp, window):
    window.table.selectRow(0)
    window._copy_field_value("password")
    assert QApplication.clipboard().text() == "secret-a"
    assert window._clipboard_token == "secret-a"
    window._clear_clipboard()
    assert QApplication.clipboard().text() == ""


def test_detail_panel_shows_selected_record(qapp, window):
    window.table.selectRow(0)
    qapp.processEvents()
    assert window.detail_panel.isVisible()
    assert "example.com" in window.detail_title.text()


def test_detail_panel_hides_after_category_switch(qapp, window):
    window.table.selectRow(0)
    qapp.processEvents()
    window._switch_category("ideas")
    qapp.processEvents()
    assert not window.detail_panel.isVisible()


def test_password_generator_fills_field(qapp, tmp_path):
    from PyQt6.QtWidgets import QLineEdit

    from suibianji.ui.main_window import ItemDialog

    dialog = ItemDialog("accounts", app_settings=AppSettings(str(tmp_path)))
    dialog._fill_generated_password()
    text = dialog._pwd_field.text()
    assert len(text) >= 20
    assert dialog._pwd_field.echoMode() == QLineEdit.EchoMode.Normal
    assert "强度" in dialog.pwd_strength_label.text()


def test_window_geometry_is_persisted(qapp, tmp_path):
    def make_window():
        dm = DataManager(str(tmp_path))
        if dm.is_first_time():
            dm.initialize_first_time("pw123456")
        return SuibianjiApp(dm, AppSettings(str(tmp_path)))

    win = make_window()
    win.setGeometry(140, 120, 1000, 700)
    win.close()
    qapp.processEvents()

    reopened = make_window()
    assert reopened.geometry().width() >= 1000
    assert reopened.geometry().height() >= 700
    reopened.close()
