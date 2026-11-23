"""全局搜索、快速记录、排序与分类筛选的界面测试。"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication, QDialog

from suibianji.core.data_manager import DataManager
from suibianji.core.settings import AppSettings
from suibianji.ui.main_window import SuibianjiApp
from suibianji.ui.search_dialog import GlobalSearchDialog, QuickCaptureDialog


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
    dm.add_idea("灵感", "随手记下的点子", tags=["赚钱"])
    dm.add_idea("待办", "没有标签的想法")
    win = SuibianjiApp(dm, AppSettings(str(tmp_path)), current_password="pw123456")
    win.show()
    qapp.processEvents()
    yield win
    win.close()
    win.deleteLater()
    qapp.processEvents()


def test_header_click_sorts_ascending_then_descending(qapp, window):
    window._on_header_clicked(1)  # 网站列
    qapp.processEvents()
    assert window.table.item(0, 1).text() == "example.com"
    window._on_header_clicked(1)
    qapp.processEvents()
    assert window.table.item(0, 1).text() == "gitlab.com"
    assert window._sort_desc is True


def test_sort_resets_when_switching_category(qapp, window):
    window._on_header_clicked(1)
    window._switch_category("ideas")
    qapp.processEvents()
    assert window._sort_column is None
    assert not window.table.horizontalHeader().isSortIndicatorShown()


def test_idea_tag_filter_populates_and_filters(qapp, window):
    window._switch_category("ideas")
    qapp.processEvents()
    assert window.type_filter.isVisible()
    assert window.type_filter_label.text() == "标签"
    assert window.type_filter.count() == 3  # 全部标签 + 赚钱 + 无标签
    window.type_filter.setCurrentIndex(window.type_filter.findData("赚钱"))
    qapp.processEvents()
    assert window.table.rowCount() == 1
    window.type_filter.setCurrentIndex(window.type_filter.findData("__untagged__"))
    qapp.processEvents()
    assert window.table.rowCount() == 1
    assert window.table.item(0, 0).text() == "待办"


def test_empty_category_filter_only_has_placeholders(qapp, window):
    window._switch_category("prompts")
    qapp.processEvents()
    assert window.type_filter.isVisible()
    assert window.type_filter.count() == 2  # 全部分类 + 未分类
    assert window.table.rowCount() == 0


def test_global_search_dialog_filters_and_opens(qapp):
    entries = [
        {
            "category": "accounts",
            "category_name": "账号密码",
            "title": "example.com",
            "snippet": "alice",
            "id": "1",
        }
    ]
    opened = []
    dialog = GlobalSearchDialog(entries, lambda c, i: opened.append((c, i)))
    dialog.input.setText("zzz")
    assert dialog.results.count() == 0
    dialog.input.setText("alice")
    assert dialog.results.count() == 1
    dialog.results.setCurrentRow(0)
    dialog._open_current()
    assert opened == [("accounts", "1")]


def test_quick_capture_dialog_returns_text(qapp):
    dialog = QuickCaptureDialog()
    dialog.input.setText("  一条想法  ")
    dialog._save()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.text() == "一条想法"


def test_quick_capture_saves_idea(qapp, window, monkeypatch):
    monkeypatch.setattr(
        QuickCaptureDialog, "exec", lambda self: QDialog.DialogCode.Accepted
    )
    monkeypatch.setattr(QuickCaptureDialog, "text", lambda self: "热键里记下的想法")
    before = len(window.data_manager.record_manager.ideas)
    window._quick_capture()
    assert len(window.data_manager.record_manager.ideas) == before + 1
    assert window.data_manager.record_manager.ideas[-1].content == "热键里记下的想法"


def test_search_result_jumps_to_row(qapp, window):
    window._switch_category("ideas")
    target = window.data_manager.record_manager.ideas[1]
    window._open_search_result("ideas", target.id)
    qapp.processEvents()
    assert window.selected_item_id == target.id
    assert window.table.currentRow() == window.filtered_records.index(target)


def test_detail_panel_shows_live_totp_code(qapp, window):
    account = window.data_manager.add_account(
        "邮箱", "totp.example.com", "alice", "secret-c", totp_secret="JBSWY3DPEHPK3PXP"
    )
    window._load_data()
    qapp.processEvents()
    row = window.filtered_records.index(account)
    window.table.selectRow(row)
    qapp.processEvents()
    assert window._totp_label is not None
    assert "剩" in window._totp_label.text()
    assert len(window._totp_code) == 6
