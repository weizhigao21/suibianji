"""全局搜索浮层与快速记录窗口。"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from .theme import COLORS, StyledButton, StyledInput


class GlobalSearchDialog(QDialog):
    """Ctrl+K 全局搜索:跨分类列出记录,选中后跳转到对应行。"""

    def __init__(self, entries, on_open, parent=None):
        super().__init__(parent)
        self._entries = entries
        self._on_open = on_open
        self.setWindowTitle("全局搜索")
        self.setModal(True)
        self.setFixedSize(620, 520)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_surface']}; }}")
        self._setup_ui()
        self._filter("")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        caption = QLabel("GLOBAL SEARCH")
        caption_font = QFont("Microsoft YaHei UI", 7)
        caption_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.6)
        caption.setFont(caption_font)
        caption.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(caption)

        title = QLabel("在所有记录中搜索")
        title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.DemiBold))
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)

        self.input = StyledInput()
        self.input.setPlaceholderText("输入关键词,回车打开第一条")
        self.input.textChanged.connect(self._filter)
        layout.addWidget(self.input)

        self.results = QListWidget()
        self.results.setFont(QFont("Microsoft YaHei UI", 9))
        self.results.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['bg_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 6px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-radius: 8px;
                color: {COLORS['text_dark']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent_soft']};
                color: {COLORS['primary']};
            }}
        """)
        self.results.itemActivated.connect(self._open_current)
        layout.addWidget(self.results, stretch=1)

        self.status = QLabel("")
        self.status.setFont(QFont("Microsoft YaHei UI", 8))
        self.status.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(self.status)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = StyledButton("关闭")
        close_btn.setFixedWidth(88)
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        open_shortcut = QShortcut(QKeySequence("Return"), self.results)
        open_shortcut.activated.connect(self._open_current)
        self.input.returnPressed.connect(self._open_current)

    def _filter(self, text: str):
        text = (text or "").strip().lower()
        self.results.clear()
        matched = 0
        for entry in self._entries:
            haystack = f"{entry['title']} {entry['snippet']}".lower()
            if text and text not in haystack:
                continue
            item = QListWidgetItem(f"{entry['category_name']}  ·  {entry['title'] or '(未命名)'}")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            if entry["snippet"]:
                item.setToolTip(entry["snippet"])
            self.results.addItem(item)
            matched += 1
        self.status.setText(f"匹配 {matched} 条 · 双击或回车打开")
        if matched:
            self.results.setCurrentRow(0)

    def _open_current(self):
        item = self.results.currentItem()
        if item is None:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        self._on_open(entry["category"], entry["id"])


class QuickCaptureDialog(QDialog):
    """全局热键唤起的小窗:一行文字直接存成一条想法。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快速记录")
        self.setModal(True)
        self.setFixedSize(460, 190)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_surface']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(10)

        title = QLabel("记一笔")
        title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.DemiBold))
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)

        hint = QLabel("回车保存,自动写入「想法记录」")
        hint.setFont(QFont("Microsoft YaHei UI", 8))
        hint.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(hint)

        self.input = StyledInput()
        self.input.setPlaceholderText("想起什么,写一句…")
        self.input.returnPressed.connect(self._save)
        layout.addWidget(self.input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = StyledButton("取消")
        cancel.setFixedWidth(76)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        save = StyledButton("保存", StyledButton.BUTTON_STYLE_PRIMARY)
        save.setFixedWidth(84)
        save.clicked.connect(self._save)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def _save(self):
        if self.input.text().strip():
            self.accept()

    def text(self) -> str:
        return self.input.text().strip()
