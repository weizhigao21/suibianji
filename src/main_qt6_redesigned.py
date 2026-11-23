import sys
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QFrame,
    QMessageBox,
    QSplitter,
    QScrollArea,
    QMenu,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QComboBox,
    QTabWidget,
    QInputDialog,
    QGraphicsDropShadowEffect,
    QStyledItemDelegate,
    QStyle,
)
from PyQt6.QtCore import Qt, QSize, QRectF, QLineF, QUrl, QTimer, QEvent
from PyQt6.QtGui import (
    QFont,
    QColor,
    QPalette,
    QIcon,
    QAction,
    QPixmap,
    QPainter,
    QPen,
    QPainterPath,
    QDesktopServices,
    QKeySequence,
    QShortcut,
)
from data_manager import DataManager
from settings import AppSettings
from app_icon import app_icon
from paths import resolve_data_dir
from single_instance import SingleInstanceGuard, socket_name
from typing import Optional, Dict, Any, List


# 旧版密钥文件数据目录:启动时自动导入,保持 .key + records.enc 格式兼容
LEGACY_DATA_DIR = Path(r"C:\DIY\suibinaji\data")

# 「纸间 · Paperlight」配色:米白纸面、墨绿点缀、细描边卡片
COLORS = {
    "primary": "#2F5D50",
    "primary_light": "#3B7163",
    "primary_dark": "#254A40",
    "secondary": "#7C786C",
    "accent": "#2F5D50",
    "bg_dark": "#F3F0E8",
    "bg_medium": "#EDE9DE",
    "bg_light": "#F7F4EC",
    "bg_surface": "#FFFFFF",
    "bg_app": "#FAF8F3",
    "text_white": "#FBF9F3",
    "text_dark": "#22221E",
    "text_gray": "#7C786C",
    "text_faint": "#ABA69A",
    "border": "#ECE7DA",
    "border_strong": "#E7E2D6",
    "success": "#3D5F52",
    "warning": "#B07A3C",
    "error": "#B05A45",
    "error_soft": "#F7E9E5",
    "info": "#2F5D50",
    "accent_soft": "#E7EFE9",
    "chip_bg": "#F1EEE5",
    "chip_fg": "#6E6A5E",
    "badge_bg": "#EEF2ED",
    "badge_fg": "#3D5F52",
    "row_hover": "#FBF9F4",
    "row_selected": "#F3F6F1",
}

# 闲置多久自动锁定(秒)
IDLE_LOCK_SECONDS = 10 * 60
# 复制密码后自动清空剪贴板的时长(毫秒)
CLIPBOARD_CLEAR_MS = 25_000


def line_icon(name: str, color: str, size: int = 18) -> QPixmap:
    """用 QPainter 绘制线性图标(替代彩色 emoji,统一为单色描边)。"""
    scale = 4  # 超采样,保证高分屏下边缘平滑
    pm = QPixmap(size * scale, size * scale)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.scale(size * scale / 24.0, size * scale / 24.0)
    pen = QPen(QColor(color))
    pen.setWidthF(1.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    if name == "key":
        p.drawEllipse(QRectF(5, 12, 7, 7))
        p.drawLine(11, 13, 20, 4)
        p.drawLine(17, 5, 19, 7)
        p.drawLine(QLineF(14.5, 7.5, 16.5, 9.5))
    elif name == "bulb":
        path = QPainterPath()
        path.addEllipse(QRectF(7, 3, 10, 11))
        p.drawPath(path)
        p.drawLine(9, 18, 15, 18)
        p.drawLine(10, 21, 14, 21)
    elif name == "wallet":
        p.drawRoundedRect(QRectF(3, 6, 18, 13), 3, 3)
        p.drawLine(QLineF(3, 9.5, 21, 9.5))
        p.drawLine(QLineF(16, 13.5, 18, 13.5))
    elif name == "sparkles":
        path = QPainterPath()
        path.moveTo(12, 3.5)
        path.lineTo(13.8, 9)
        path.lineTo(19.3, 10.8)
        path.lineTo(13.8, 12.6)
        path.lineTo(12, 18)
        path.lineTo(10.2, 12.6)
        path.lineTo(4.7, 10.8)
        path.lineTo(10.2, 9)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QLineF(19, 15.5, 19, 19.5))
        p.drawLine(QLineF(17, 17.5, 21, 17.5))
    elif name == "shield":
        path = QPainterPath()
        path.moveTo(12, 3)
        path.lineTo(19, 6)
        path.lineTo(19, 11)
        path.cubicTo(19, 15.4, 16.1, 18.4, 12, 20)
        path.cubicTo(7.9, 18.4, 5, 15.4, 5, 11)
        path.lineTo(5, 6)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(9, 12, 11, 14)
        p.drawLine(11, 14, 15, 10)
    elif name == "sliders":
        p.drawLine(4, 7, 13, 7)
        p.drawLine(18, 7, 20, 7)
        p.drawLine(4, 17, 8, 17)
        p.drawLine(13, 17, 20, 17)
        p.drawEllipse(QRectF(13.5, 5, 4, 4))
        p.drawEllipse(QRectF(8.5, 15, 4, 4))
    elif name == "search":
        p.drawEllipse(QRectF(4, 4, 14, 14))
        p.drawLine(QLineF(16.5, 16.5, 20, 20))
    p.end()
    pm.setDevicePixelRatio(scale)
    return pm


class StyledButton(QPushButton):
    BUTTON_STYLE_PRIMARY = "primary"
    BUTTON_STYLE_SECONDARY = "secondary"
    BUTTON_STYLE_DANGER = "danger"

    def __init__(self, text: str, style: str = BUTTON_STYLE_SECONDARY, parent=None):
        super().__init__(text, parent)
        self._button_style = style
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Microsoft YaHei UI", 10))
        self.setFixedHeight(38)
        self._update_style()

    def _update_style(self):
        styles = {
            self.BUTTON_STYLE_PRIMARY: f"""
                QPushButton {{
                    background-color: {COLORS["primary"]};
                    color: {COLORS["text_white"]};
                    border: 1px solid {COLORS["primary"]};
                    border-radius: 10px;
                    padding: 0 18px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COLORS["primary_dark"]};
                    border-color: {COLORS["primary_dark"]};
                }}
                QPushButton:pressed {{
                    background-color: #1E3B33;
                }}
            """,
            self.BUTTON_STYLE_SECONDARY: f"""
                QPushButton {{
                    background-color: {COLORS["bg_surface"]};
                    color: {COLORS["text_dark"]};
                    border: 1px solid {COLORS["border"]};
                    border-radius: 10px;
                    padding: 0 16px;
                    font-size: 12.5px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLORS["bg_light"]};
                    border-color: #D9D3C4;
                }}
                QPushButton:pressed {{
                    background-color: {COLORS["bg_medium"]};
                }}
            """,
            self.BUTTON_STYLE_DANGER: f"""
                QPushButton {{
                    background-color: {COLORS["bg_surface"]};
                    color: {COLORS["error"]};
                    border: 1px solid #EADBD5;
                    border-radius: 10px;
                    padding: 0 16px;
                    font-size: 12.5px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLORS["error_soft"]};
                    border-color: #E3CFC8;
                }}
                QPushButton:pressed {{
                    background-color: #F1DED8;
                }}
            """
        }
        self.setStyleSheet(styles.get(self._button_style, styles[self.BUTTON_STYLE_SECONDARY]))


class StyledInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Microsoft YaHei UI", 10))
        self.setFixedHeight(38)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["bg_surface"]};
                color: {COLORS["text_dark"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 10px;
                padding: 0 14px;
                selection-background-color: {COLORS["accent_soft"]};
                selection-color: {COLORS["text_dark"]};
            }}
            QLineEdit:hover {{
                border-color: #DCD6C7;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS["primary"]};
            }}
            QLineEdit::placeholder {{
                color: {COLORS["text_faint"]};
            }}
        """)


class StyledTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Microsoft YaHei UI", 10))
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS["bg_surface"]};
                color: {COLORS["text_dark"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 10px;
                padding: 10px 12px;
                selection-background-color: {COLORS["accent_soft"]};
                selection-color: {COLORS["text_dark"]};
            }}
            QTextEdit:hover {{
                border-color: #DCD6C7;
            }}
            QTextEdit:focus {{
                border: 1px solid {COLORS["primary"]};
            }}
        """)


class PaperCheckBox(QCheckBox):
    """纸间风格复选框:自绘圆角方框与墨绿对勾。"""

    BOX_SIZE = 17
    GAP = 10

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(26)
        self.setFont(QFont("Microsoft YaHei UI", 10))

    def sizeHint(self) -> QSize:
        fm = self.fontMetrics()
        return QSize(self.BOX_SIZE + self.GAP + fm.horizontalAdvance(self.text()) + 2, 26)

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        box = QRectF(0.5, (self.height() - self.BOX_SIZE) / 2, self.BOX_SIZE, self.BOX_SIZE)

        # 焦点光圈
        if self.hasFocus():
            painter.setPen(QPen(QColor(47, 93, 80, 46), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(box.adjusted(-2.5, -2.5, 2.5, 2.5), 8, 8)

        if self.isChecked():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLORS["primary"]))
            painter.drawRoundedRect(box, 5, 5)

            check_pen = QPen(QColor("#FBF9F3"))
            check_pen.setWidthF(2.0)
            check_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            check_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(check_pen)
            center = box.center()
            check = QPainterPath()
            check.moveTo(box.left() + 4.1, center.y() + 0.3)
            check.lineTo(box.left() + 7.1, center.y() + 3.2)
            check.lineTo(box.left() + 12.7, center.y() - 3.6)
            painter.strokePath(check, check_pen)
        else:
            border_color = COLORS["primary"] if self.underMouse() else "#D9D3C4"
            painter.setPen(QPen(QColor(border_color), 1.0))
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawRoundedRect(box, 5, 5)

        text_color = COLORS["text_faint"] if not self.isEnabled() else COLORS["text_dark"]
        painter.setPen(QColor(text_color))
        painter.setFont(self.font())
        text_rect = QRectF(
            self.BOX_SIZE + self.GAP, 0,
            max(0, self.width() - self.BOX_SIZE - self.GAP), self.height()
        )
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


class PaperComboBox(QComboBox):
    """纸间风格下拉框:自绘右侧箭头,让“可选择”一眼可见。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(38)
        self.setFont(QFont("Microsoft YaHei UI", 10))

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        active = self.underMouse() or self.hasFocus()
        pen = QPen(QColor(COLORS["primary"] if active else COLORS["text_gray"]))
        pen.setWidthF(1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        cx = self.width() - 21
        cy = self.height() / 2 - 1
        painter.drawLine(QLineF(cx - 4, cy - 2, cx, cy + 2))
        painter.drawLine(QLineF(cx, cy + 2, cx + 4, cy - 2))


class RowAccentDelegate(QStyledItemDelegate):
    """选中行左侧 3px 墨绿色条,呼应纸间主题的选中态。"""

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if index.column() == 0 and (option.state & QStyle.StateFlag.State_Selected):
            painter.save()
            painter.fillRect(option.rect.left(), option.rect.top(), 3, option.rect.height(),
                             QColor(COLORS["primary"]))
            painter.restore()


class ItemDialog(QDialog):
    def __init__(self, category: str, data: Dict = None, app_settings: "AppSettings" = None, parent=None):
        super().__init__(parent)
        self.category = category
        self.data = data or {}
        self.app_settings = app_settings
        self.result_data = None
        self.setModal(True)
        self.setWindowTitle("添加记录" if not data else "编辑记录")
        self.setFixedSize(640, 700)
        self.setStyleSheet(
            f"QDialog {{ background-color: {COLORS['bg_surface']}; border-radius: 18px; }}"
        )
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题区:白色纸面 + 淡灰小标题
        header = QFrame()
        header.setStyleSheet(f"background-color: {COLORS['bg_surface']};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(34, 26, 26, 18)

        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(6)

        eyebrow = QLabel("EDIT RECORD" if self.data else "NEW RECORD")
        eyebrow_font = QFont("Microsoft YaHei UI", 8)
        eyebrow_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.6)
        eyebrow.setFont(eyebrow_font)
        eyebrow.setStyleSheet(f"color: {COLORS['text_faint']};")
        title_box.addWidget(eyebrow)

        title_label = QLabel("编辑记录" if self.data else "添加记录")
        title_label.setFont(QFont("Microsoft YaHei UI", 15, QFont.Weight.DemiBold))
        title_label.setStyleSheet(f"color: {COLORS['text_dark']};")
        title_box.addWidget(title_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_faint']};
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['text_dark']};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addWidget(header)

        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_surface']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(34, 8, 34, 24)

        self.fields: List[tuple] = []  # (field_key, label_text, widget, multiline)

        if self.category == "accounts":
            self._create_account_type_field()
            self._create_fields(
                [
                    ("website", "网站", False),
                    ("username", "用户名", False),
                    ("password", "密码", True),
                    ("url", "网址", False),
                    ("notes", "备注", False, True),
                ]
            )
        elif self.category == "ideas":
            self._create_fields(
                [
                    ("title", "标题", False),
                    ("content", "内容", False, True),
                    ("tags", "标签(逗号分隔)", False),
                ]
            )
        elif self.category == "wallets":
            self._create_fields(
                [
                    ("name", "名称", False),
                    ("address", "地址", False),
                    ("wallet_type", "类型", False),
                    ("notes", "备注", False, True),
                ]
            )
        elif self.category == "prompts":
            self._create_fields(
                [
                    ("title", "标题", False),
                    ("content", "内容", False, True),
                    ("category", "分类", False),
                ]
            )

        for field_key, label_text, widget, multiline in self.fields:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(7)
            field_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(label_text)
            label.setFont(QFont("Microsoft YaHei UI", 9))
            label.setStyleSheet(f"color: {COLORS['text_gray']};")
            field_layout.addWidget(label)

            if multiline:
                widget.setMinimumHeight(96)
            field_layout.addWidget(widget)
            content_layout.addLayout(field_layout)
            content_layout.addSpacing(14)

        content_layout.addStretch()

        # 内容可滚动,避免字段过多时被裁切
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: {COLORS['bg_surface']}; }}"
            f"QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 0; }}"
            f"QScrollBar::handle:vertical {{ background: #DCD6C7; border-radius: 4px; min-height: 30px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
            f"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}"
        )
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

        btn_frame = QFrame()
        btn_frame.setStyleSheet(
            f"background-color: #FBF9F4; border-top: 1px solid {COLORS['border']};"
        )
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(34, 18, 34, 18)
        btn_layout.setSpacing(10)

        btn_layout.addStretch()

        cancel_btn = StyledButton("取消")
        cancel_btn.setFixedWidth(88)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = StyledButton("保存", StyledButton.BUTTON_STYLE_PRIMARY)
        save_btn.setFixedWidth(96)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addWidget(btn_frame)

    def _create_account_type_field(self):
        """账号分类专用:创建类型下拉选择框。"""
        combo = PaperComboBox()
        combo.setEditable(False)
        if self.app_settings:
            combo.addItems(self.app_settings.account_types)
        else:
            combo.addItems(["邮箱", "视频", "论坛", "社交", "购物", "工作", "其他"])
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_surface']};
                color: {COLORS['text_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 0 34px 0 12px;
                min-height: 36px;
            }}
            QComboBox:hover {{
                border-color: #DCD6C7;
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_surface']};
                color: {COLORS['text_dark']};
                border: 1px solid {COLORS['border']};
                selection-background-color: {COLORS['accent_soft']};
                selection-color: {COLORS['text_dark']};
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 30px;
                padding-left: 8px;
            }}
        """)
        # 弹出列表是独立窗口,单独设置样式才能确保配色生效
        combo.view().setStyleSheet(f"""
            QListView {{
                background-color: {COLORS['bg_surface']};
                color: {COLORS['text_dark']};
                border: 1px solid {COLORS['border']};
                padding: 4px;
                outline: none;
                selection-background-color: {COLORS['accent_soft']};
                selection-color: {COLORS['text_dark']};
            }}
            QListView::item {{
                min-height: 30px;
                padding-left: 8px;
            }}
            QListView::item:selected {{
                background-color: {COLORS['accent_soft']};
                color: {COLORS['text_dark']};
            }}
            QListView::item:hover {{
                background-color: {COLORS['row_hover']};
            }}
        """)
        existing = self.data.get("account_type") or ""
        if existing:
            idx = combo.findText(existing)
            if idx < 0:
                # 兼容旧数据中不在类型列表里的自定义类型
                combo.addItem(existing)
                idx = combo.count() - 1
            combo.setCurrentIndex(idx)
        else:
            # 旧数据或空类型,默认选中“其他”
            idx = combo.findText("其他")
            if idx >= 0:
                combo.setCurrentIndex(idx)
        self.fields.append(("account_type", "类型", combo, False))

    def _create_fields(self, fields_config: List):
        for config in fields_config:
            if len(config) == 3:
                field_key, label_text, is_password = config
                multiline = False
            else:
                field_key, label_text, is_password, multiline = config

            if multiline:
                widget = StyledTextEdit()
            else:
                widget = StyledInput()
                if is_password:
                    widget.setEchoMode(QLineEdit.EchoMode.Password)

            if field_key in self.data:
                value = self.data[field_key]
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(value or "")
                else:
                    widget.setText(value or "")

            self.fields.append((field_key, label_text, widget, multiline))

    def _save(self):
        self.result_data = {}
        for field_key, label_text, widget, multiline in self.fields:
            if isinstance(widget, QTextEdit):
                self.result_data[field_key] = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                self.result_data[field_key] = widget.currentText().strip()
            else:
                self.result_data[field_key] = widget.text().strip()
        self.accept()

    def get_result(self):
        return self.result_data


class PasswordDialog(QDialog):
    """主密码对话框:支持设置(首次/迁移)和验证两种模式。"""

    MODE_SETUP = "setup"
    MODE_VERIFY = "verify"

    def __init__(self, mode: str, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.data_manager = data_manager
        self.password: Optional[str] = None
        self.setModal(True)
        if mode == self.MODE_SETUP:
            self.setWindowTitle("设置主密码")
            self._info_text = "请设置主密码用于加密你的数据。\n忘记主密码将无法恢复数据,请妥善保管。"
        else:
            self.setWindowTitle("输入主密码")
            self._info_text = "请输入主密码以解锁数据。"
        self.setFixedSize(460, 360 if mode == self.MODE_SETUP else 280)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_surface']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(12)

        eyebrow = QLabel("SUIBIANJI · LOCAL VAULT")
        eyebrow_font = QFont("Microsoft YaHei UI", 7)
        eyebrow_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.4)
        eyebrow.setFont(eyebrow_font)
        eyebrow.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(eyebrow)

        title = QLabel("设置主密码" if self.mode == self.MODE_SETUP else "输入主密码")
        title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.DemiBold))
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)

        info = QLabel(self._info_text)
        info.setFont(QFont("Microsoft YaHei UI", 9))
        info.setStyleSheet(f"color: {COLORS['text_gray']};")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addSpacing(4)

        self.pwd_input = StyledInput()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("主密码")
        layout.addWidget(self.pwd_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 11px;")
        self.error_label.setFont(QFont("Microsoft YaHei UI", 9))
        self.error_label.hide()
        layout.addWidget(self.error_label)

        if self.mode == self.MODE_SETUP:
            self.confirm_input = StyledInput()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setPlaceholderText("确认主密码")
            layout.addWidget(self.confirm_input)
            self.confirm_input.returnPressed.connect(self._on_confirm)
        else:
            self.confirm_input = None

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = StyledButton("退出" if self.mode == self.MODE_VERIFY else "取消")
        cancel_btn.setFixedWidth(84)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = StyledButton("解锁" if self.mode == self.MODE_VERIFY else "确定",
                              StyledButton.BUTTON_STYLE_PRIMARY)
        ok_btn.setFixedWidth(96)
        ok_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        self.pwd_input.returnPressed.connect(self._on_confirm)

    def _set_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(bool(message))

    def _on_confirm(self):
        pwd = self.pwd_input.text()
        if not pwd:
            return
        if self.mode == self.MODE_SETUP:
            confirm = self.confirm_input.text()
            if len(pwd) < 8:
                self._set_error("主密码至少需要 8 个字符,建议包含字母、数字和符号")
                return
            if pwd != confirm:
                self._set_error("两次输入的密码不一致")
                self.confirm_input.clear()
                return
            self.password = pwd
            self.accept()
        else:
            if self.data_manager.verify_password(pwd):
                self.password = pwd
                self.accept()
            else:
                self._set_error("主密码错误,请重试")
                self.pwd_input.clear()
                self.pwd_input.setFocus()

    def get_password(self) -> Optional[str]:
        return self.password


class AccountTypeListItem(QWidget):
    """账号类型列表项:显示名称 + 编辑/删除按钮。"""

    def __init__(self, text: str, can_delete: bool, parent=None):
        super().__init__(parent)
        self._text = text
        self._can_delete = can_delete
        self._setup_ui()
        self._update_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.label = QLabel(self._text)
        self.label.setFont(QFont("Microsoft YaHei UI", 10))
        self.label.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(self.label)
        layout.addStretch()

        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setFixedSize(52, 26)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_gray']};
                border: 1px solid {COLORS['border']};
                border-radius: 7px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_surface']};
                color: {COLORS['primary']};
                border-color: #D9D3C4;
            }}
        """)
        layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setFixedSize(52, 26)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setEnabled(self._can_delete)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_gray']};
                border: 1px solid {COLORS['border']};
                border-radius: 7px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error_soft']};
                color: {COLORS['error']};
                border-color: #E3CFC8;
            }}
            QPushButton:disabled {{
                background-color: transparent;
                color: #CFCABC;
                border-color: {COLORS['border']};
            }}
        """)
        layout.addWidget(self.delete_btn)

    def _update_style(self):
        self.setStyleSheet(f"""
            AccountTypeListItem {{
                background-color: {COLORS['bg_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
            AccountTypeListItem:hover {{
                background-color: #F5F2E9;
            }}
        """)

    def text(self) -> str:
        return self._text

    def set_text(self, text: str):
        self._text = text
        self.label.setText(text)


class SettingsDialog(QDialog):
    """设置对话框:常规设置 + 账号类型管理。"""

    def __init__(self, app_settings: "AppSettings", data_manager: DataManager,
                 current_password: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self.data_manager = data_manager
        # 当前主密码(内存),用于开启免密登录时立即缓存到 keyring
        self.current_password = current_password
        self._password_changed = False
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setFixedSize(560, 480)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_surface']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(14)

        eyebrow = QLabel("PREFERENCES")
        eyebrow_font = QFont("Microsoft YaHei UI", 7)
        eyebrow_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.4)
        eyebrow.setFont(eyebrow_font)
        eyebrow.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(eyebrow)

        title = QLabel("设置")
        title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.DemiBold))
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Microsoft YaHei UI", 10))
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                border-top: 1px solid {COLORS['border']};
                background-color: {COLORS['bg_surface']};
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {COLORS['text_gray']};
                border: none;
                border-bottom: 2px solid transparent;
                padding: 10px 2px;
                margin-right: 22px;
                font-size: 12.5px;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                color: {COLORS['text_dark']};
            }}
        """)
        self.tabs.addTab(self._create_general_tab(), "常规")
        self.tabs.addTab(self._create_security_tab(), "安全")
        self.tabs.addTab(self._create_types_tab(), "类型管理")
        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = StyledButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        ok_btn = StyledButton("保存", StyledButton.BUTTON_STYLE_PRIMARY)
        ok_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _create_general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        # 开关行
        key_mode = self.data_manager.has_legacy_key()
        self.remember_checkbox = PaperCheckBox("一天内免密登录")
        if key_mode:
            self.remember_checkbox.setChecked(True)
            self.remember_checkbox.setEnabled(False)
        else:
            self.remember_checkbox.setChecked(self.app_settings.remember_password_enabled)
        layout.addWidget(self.remember_checkbox)

        desc = QLabel(
            "当前使用旧版 .key 密钥文件加密,启动时自动解锁,无需主密码。\n"
            "请妥善保管 data 目录中的 .key 与 records.enc,丢失 .key 将无法恢复数据。"
            if key_mode else
            "开启后,登录成功当天(24 小时内)会自动从系统钥匙串读取主密码,\n"
            "无需再次手动输入。关闭后会立即清除已保存的密码。"
        )
        desc.setFont(QFont("Microsoft YaHei UI", 8))
        desc.setStyleSheet(f"color: {COLORS['text_gray']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # keyring 可用性提示(密钥文件模式无需主密码,不显示)
        if not key_mode and not self.data_manager.is_keyring_available():
            warn = QLabel("⚠️ 未检测到系统钥匙串支持(keyring 未安装或不可用),此功能将不会生效。")
            warn.setFont(QFont("Microsoft YaHei UI", 8))
            warn.setStyleSheet(f"color: {COLORS['error']};")
            warn.setWordWrap(True)
            layout.addWidget(warn)

        # 数据位置:明确告诉用户记录存在哪,并提供一键打开
        data_path = QLabel("数据位置")
        data_path.setFont(QFont("Microsoft YaHei UI", 9))
        data_path.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(data_path)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self.data_dir_label = QLabel(str(Path(self.data_manager.data_dir).resolve()))
        self.data_dir_label.setFont(QFont("Microsoft YaHei UI", 9))
        self.data_dir_label.setStyleSheet(f"color: {COLORS['text_dark']};")
        self.data_dir_label.setWordWrap(True)
        self.data_dir_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        path_row.addWidget(self.data_dir_label, stretch=1)

        open_dir_btn = StyledButton("打开文件夹")
        open_dir_btn.setFixedSize(96, 32)
        open_dir_btn.clicked.connect(self._open_data_dir)
        path_row.addWidget(open_dir_btn, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(path_row)

        layout.addStretch()
        return tab

    def _open_data_dir(self):
        """在文件管理器中打开数据目录。"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.data_manager.data_dir).resolve())))

    def _create_security_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(10)

        info = QLabel("修改主密码会重新加密整个数据库。修改前会自动生成完整备份,失败时自动回滚。")
        info.setFont(QFont("Microsoft YaHei UI", 9))
        info.setStyleSheet(f"color: {COLORS['text_gray']};")
        info.setWordWrap(True)
        layout.addWidget(info)

        self.old_pwd_input = self._password_field("当前主密码")
        self.new_pwd_input = self._password_field("新主密码")
        self.confirm_new_pwd_input = self._password_field("确认新主密码")
        for field in (self.old_pwd_input, self.new_pwd_input, self.confirm_new_pwd_input):
            layout.addWidget(field)

        hint = QLabel("至少 8 个字符,建议包含字母、数字和符号。")
        hint.setFont(QFont("Microsoft YaHei UI", 8))
        hint.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(hint)

        self.pwd_error_label = QLabel("")
        self.pwd_error_label.setFont(QFont("Microsoft YaHei UI", 9))
        self.pwd_error_label.setStyleSheet(f"color: {COLORS['error']};")
        self.pwd_error_label.setWordWrap(True)
        self.pwd_error_label.hide()
        layout.addWidget(self.pwd_error_label)

        if self.data_manager.has_legacy_key():
            legacy_note = QLabel(
                "当前使用旧版 .key 密钥文件,没有主密码可修改。\n"
                "如需启用主密码加密,请先迁移数据(迁移功能将在后续版本提供)。")
            legacy_note.setFont(QFont("Microsoft YaHei UI", 8))
            legacy_note.setStyleSheet(f"color: {COLORS['warning']};")
            legacy_note.setWordWrap(True)
            layout.addWidget(legacy_note)
            for field in (self.old_pwd_input, self.new_pwd_input, self.confirm_new_pwd_input):
                field.setEnabled(False)

        layout.addStretch()
        return tab

    @staticmethod
    def _password_field(placeholder: str) -> "StyledInput":
        field = StyledInput()
        field.setEchoMode(QLineEdit.EchoMode.Password)
        field.setPlaceholderText(placeholder)
        return field

    def _set_pwd_error(self, message: str):
        self.pwd_error_label.setText(message)
        self.pwd_error_label.setVisible(bool(message))

    def _apply_password_change(self) -> bool:
        """安全页填了密码就执行改密;返回 False 表示校验失败,对话框不应关闭。"""
        old = self.old_pwd_input.text()
        new = self.new_pwd_input.text()
        confirm = self.confirm_new_pwd_input.text()
        if not (old or new or confirm):
            return True
        if self.data_manager.has_legacy_key():
            self._set_pwd_error("当前为旧版密钥文件模式,没有主密码可修改。")
            return False
        if not old:
            self._set_pwd_error("请输入当前主密码。")
            return False
        if len(new) < 8:
            self._set_pwd_error("新主密码至少需要 8 个字符。")
            return False
        if new != confirm:
            self._set_pwd_error("两次输入的新密码不一致。")
            self.confirm_new_pwd_input.clear()
            return False
        try:
            changed = self.data_manager.change_password(old, new)
        except Exception as e:
            self._set_pwd_error(f"修改失败,已回滚到原数据: {e}")
            return False
        if not changed:
            self._set_pwd_error("当前主密码不正确,请重试。")
            return False

        self.current_password = new
        self._password_changed = True
        if self.app_settings.remember_password_enabled:
            self.data_manager.cache_password(new)
            self.app_settings.refresh_remember_period()
        self._set_pwd_error("")
        for field in (self.old_pwd_input, self.new_pwd_input, self.confirm_new_pwd_input):
            field.clear()
        return True

    def _create_types_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        info = QLabel("管理账号密码分类。下方列表中的类型会出现在“添加/编辑账号”下拉框中。")
        info.setFont(QFont("Microsoft YaHei UI", 9))
        info.setStyleSheet(f"color: {COLORS['text_gray']};")
        info.setWordWrap(True)
        layout.addWidget(info)

        # 类型列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        self.types_container = QWidget()
        self.types_layout = QVBoxLayout(self.types_container)
        self.types_layout.setContentsMargins(0, 0, 0, 0)
        self.types_layout.setSpacing(8)
        self.types_layout.addStretch()
        scroll.setWidget(self.types_container)
        layout.addWidget(scroll)

        self._refresh_type_list()

        # 添加行
        add_layout = QHBoxLayout()
        self.new_type_input = StyledInput()
        self.new_type_input.setPlaceholderText("输入新类型,按回车添加")
        self.new_type_input.returnPressed.connect(self._on_add_type)
        add_layout.addWidget(self.new_type_input)

        add_btn = StyledButton("添加", StyledButton.BUTTON_STYLE_PRIMARY)
        add_btn.setFixedWidth(80)
        add_btn.clicked.connect(self._on_add_type)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        return tab

    def _refresh_type_list(self):
        # 清空现有项(保留 stretch)
        while self.types_layout.count() > 1:
            item = self.types_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        types = self.app_settings.account_types
        for t in types:
            self._add_type_item(t)

    def _add_type_item(self, text: str):
        can_delete = text != "其他"
        item = AccountTypeListItem(text, can_delete)
        item.edit_btn.clicked.connect(lambda checked, w=item: self._on_edit_type(w))
        item.delete_btn.clicked.connect(lambda checked, w=item: self._on_delete_type(w))
        # 插在 stretch 前面
        self.types_layout.insertWidget(self.types_layout.count() - 1, item)

    def _on_add_type(self):
        text = self.new_type_input.text().strip()
        if not text:
            return
        current = [t for t in self.app_settings.account_types]
        if text in current:
            QMessageBox.warning(self, "提示", f"“{text}”已存在")
            return
        self._add_type_item(text)
        self.new_type_input.clear()

    def _on_edit_type(self, item: AccountTypeListItem):
        old_text = item.text()
        new_text, ok = QInputDialog.getText(self, "编辑类型", "类型名称:", text=old_text)
        if not ok:
            return
        new_text = new_text.strip()
        if not new_text or new_text == old_text:
            return
        # 收集当前列表并替换
        texts = self._collect_type_texts()
        if new_text in texts:
            QMessageBox.warning(self, "提示", f"“{new_text}”已存在")
            return
        item.set_text(new_text)

    def _on_delete_type(self, item: AccountTypeListItem):
        text = item.text()
        if text == "其他":
            return
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除类型“{text}”吗?\n已有账号记录中的该类型不会被修改。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            item.deleteLater()
            # 删除布局中的占位
            for i in range(self.types_layout.count()):
                if self.types_layout.itemAt(i).widget() == item:
                    self.types_layout.takeAt(i)
                    break

    def _collect_type_texts(self) -> list:
        texts = []
        for i in range(self.types_layout.count()):
            w = self.types_layout.itemAt(i).widget()
            if isinstance(w, AccountTypeListItem):
                texts.append(w.text())
        return texts

    def _on_save(self):
        # 安全:改主密码(校验失败则保持对话框打开)
        if not self._apply_password_change():
            return

        # 常规(密钥文件模式无主密码,跳过免密登录逻辑)
        if not self.data_manager.has_legacy_key():
            enabled = self.remember_checkbox.isChecked()
            changed = enabled != self.app_settings.remember_password_enabled
            self.app_settings.remember_password_enabled = enabled
            if changed:
                if enabled:
                    # 立即缓存主密码 + 刷新有效期,使免密登录即时生效
                    if not self.data_manager.is_keyring_available():
                        QMessageBox.warning(
                            self, "提示",
                            "系统钥匙串不可用(keyring 未安装或不可用),免密登录未能启用。")
                    elif not self.current_password:
                        QMessageBox.warning(
                            self, "提示",
                            "无法获取当前主密码,请下次登录后再启用免密登录。")
                    else:
                        self.data_manager.cache_password(self.current_password)
                        self.app_settings.refresh_remember_period()
                else:
                    self.data_manager.clear_cached_password()
                    self.app_settings.clear_remember_period()

        # 类型管理
        new_types = self._collect_type_texts()
        # 保证"其他"在最后
        if "其他" in new_types:
            new_types.remove("其他")
        new_types.append("其他")
        if new_types != self.app_settings.account_types:
            self.app_settings.account_types = new_types

        self.accept()


class CategoryItem(QWidget):
    """侧栏分类项:线框图标 + 中文名/英文小标签 + 数量胶囊。"""

    def __init__(self, icon, title, subtitle, count, category, app, parent=None):
        super().__init__(parent)
        self.category = category
        self.app = app
        self._icon_name = icon
        self._is_hovered = False
        self._is_active = False
        self.setFixedHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(16)
        self._shadow.setOffset(0, 3)
        self._shadow.setColor(QColor(35, 40, 30, 26))
        self._shadow.setEnabled(False)
        self.setGraphicsEffect(self._shadow)
        self._setup_ui(title, subtitle, count)
        self._update_style()

    def _setup_ui(self, title, subtitle, count):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(11, 8, 11, 8)
        layout.setSpacing(11)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(34, 34)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        text_container = QVBoxLayout()
        text_container.setContentsMargins(0, 0, 0, 0)
        text_container.setSpacing(2)

        self.title_label = QLabel(title)
        title_font = QFont("Microsoft YaHei UI", 10)
        title_font.setWeight(QFont.Weight.DemiBold)
        self.title_label.setFont(title_font)
        text_container.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        sub_font = QFont("Microsoft YaHei UI", 6)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
        self.subtitle_label.setFont(sub_font)
        text_container.addWidget(self.subtitle_label)

        layout.addLayout(text_container, stretch=1)

        self.count_label = QLabel(str(count))
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setFixedHeight(20)
        self.count_label.setMinimumWidth(24)
        self.count_label.setFont(QFont("Microsoft YaHei UI", 8))
        layout.addWidget(self.count_label, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _update_style(self):
        if self._is_active:
            self.setStyleSheet(f"""
                CategoryItem {{
                    background-color: {COLORS['bg_surface']};
                    border-radius: 11px;
                }}
            """)
            self.title_label.setStyleSheet(f"color: #1E2B25; background: transparent;")
            self.subtitle_label.setStyleSheet(f"color: #7C8D84; background: transparent;")
            self.count_label.setStyleSheet(
                f"color: {COLORS['badge_fg']}; background-color: {COLORS['accent_soft']};"
                f"border-radius: 9px; padding: 0 6px;"
            )
            self._set_icon(COLORS["primary"])
        else:
            hover_bg = "#EDE9DE" if self._is_hovered else "transparent"
            self.setStyleSheet(f"""
                CategoryItem {{
                    background-color: {hover_bg};
                    border-radius: 11px;
                }}
            """)
            self.title_label.setStyleSheet(f"color: #2A2A26; background: transparent;")
            self.subtitle_label.setStyleSheet(f"color: #96917F; background: transparent;")
            self.count_label.setStyleSheet(
                f"color: #96917F; background-color: #E9E4D7;"
                f"border-radius: 9px; padding: 0 6px;"
            )
            self._set_icon("#8E8A7D")
        self._shadow.setEnabled(self._is_active)

    def _set_icon(self, color: str):
        self.icon_label.setPixmap(line_icon(self._icon_name, color, 18))

    def set_active(self, active: bool):
        self._is_active = active
        self._update_style()

    def update_count(self, count: int):
        self.count_label.setText(str(count))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.app._switch_category(self.category)

    def enterEvent(self, event):
        self._is_hovered = True
        self._update_style()

    def leaveEvent(self, event):
        self._is_hovered = False
        self._update_style()


class SuibianjiApp(QMainWindow):
    def __init__(self, data_manager: DataManager, app_settings: "AppSettings",
                 current_password: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("随便记 - 个人记录管理器")
        self.setMinimumSize(1200, 800)

        self.data_manager = data_manager
        self.app_settings = app_settings
        # 当前主密码(内存),仅用于"设置中开启免密登录"时立即缓存到 keyring。
        # 已由用户授权缓存(开启免密即代表同意存入系统钥匙串),不增加额外攻击面。
        self.current_password = current_password

        self.current_category = "accounts"
        self.selected_item_id: Optional[str] = None
        self.filtered_records: list = []

        # 剪贴板与锁定状态
        self._locking = False
        self._clipboard_token = ""
        self._clipboard_timer = QTimer(self)
        self._clipboard_timer.setSingleShot(True)
        self._clipboard_timer.timeout.connect(self._clear_clipboard)
        self._last_activity = time.monotonic()

        self._setup_ui()
        self._load_data()
        self._setup_lifecycle()

    def _setup_lifecycle(self):
        """快捷键、闲置检测、事件过滤器。"""
        self._lock_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self._lock_shortcut.activated.connect(self.lock)

        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._check_idle)
        self._idle_timer.start(60_000)

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() in (
            QEvent.Type.MouseButtonPress,
            QEvent.Type.KeyPress,
            QEvent.Type.MouseMove,
            QEvent.Type.Wheel,
        ):
            self._last_activity = time.monotonic()
        return super().eventFilter(obj, event)

    def _check_idle(self):
        if self._locking:
            return
        if time.monotonic() - self._last_activity >= IDLE_LOCK_SECONDS:
            self.lock()

    def lock(self):
        """锁定:清空内存中的记录与密码,校验通过后重新加载。"""
        if self._locking:
            return
        self._locking = True
        try:
            self.hide()
            self.table.setRowCount(0)
            self.filtered_records = []
            self.selected_item_id = None
            self.data_manager.record_manager = None
            self.data_manager.cipher = None
            self._clipboard_token = ""
            QApplication.clipboard().clear()
            self._last_activity = time.monotonic()

            while True:
                dialog = PasswordDialog(PasswordDialog.MODE_VERIFY, self.data_manager)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    QApplication.quit()
                    return
                password = dialog.get_password()
                try:
                    self.data_manager.initialize_with_password(password)
                    break
                except Exception as e:
                    QMessageBox.critical(None, "解锁失败", f"数据加载失败: {e}")

            self.current_password = password
            self._last_activity = time.monotonic()
            self._load_data()
            self.show()
            self.raise_()
            self.activateWindow()
        finally:
            self._locking = False

    def _setup_ui(self):
        # 主样式:纸面色底 + 无边框表格 + 细描边表头
        self.setStyleSheet(f"""
            * {{
                outline: none;
            }}
            QMainWindow {{
                background-color: {COLORS["bg_app"]};
            }}
            QTableWidget {{
                background-color: transparent;
                color: {COLORS["text_dark"]};
                border: none;
                gridline-color: transparent;
                font-size: 12.5px;
                selection-background-color: {COLORS["row_selected"]};
                selection-color: {COLORS["text_dark"]};
            }}
            QTableWidget::item {{
                padding: 0 14px;
                border: none;
                border-bottom: 1px solid #F4F1E8;
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS["row_hover"]};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS["row_selected"]};
                color: {COLORS["text_dark"]};
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {COLORS["text_faint"]};
                padding: 0 14px;
                border: none;
                border-bottom: 1px solid {COLORS["border"]};
                font-size: 10px;
                font-weight: 500;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 6px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: #DCD6C7;
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QScrollBar:horizontal {{
                height: 0;
            }}
            QMessageBox {{
                background-color: {COLORS["bg_surface"]};
            }}
            QMessageBox QLabel {{
                color: {COLORS["text_dark"]};
                font-size: 12.5px;
            }}
            QMessageBox QPushButton {{
                min-width: 72px;
                height: 32px;
                padding: 0 14px;
                border-radius: 8px;
                border: 1px solid {COLORS["border"]};
                background-color: {COLORS["bg_surface"]};
                color: {COLORS["text_dark"]};
                font-size: 12.5px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {COLORS["bg_light"]};
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._setup_sidebar(main_layout)
        self._setup_content(main_layout)

    def _setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(252)
        sidebar.setStyleSheet(
            f"background-color: {COLORS['bg_dark']};"
            f"border-right: 1px solid {COLORS['border_strong']};"
        )
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 26, 18, 20)
        sidebar_layout.setSpacing(0)

        # 品牌区:深绿“随”字 mark + 名称 + 英文副标题
        brand = QWidget()
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(8, 0, 8, 0)
        brand_layout.setSpacing(12)

        mark = QLabel("随")
        mark.setFixedSize(38, 38)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setStyleSheet(f"""
            background-color: {COLORS['primary']};
            color: #F8F5EC;
            border-radius: 11px;
            font-family: "Microsoft YaHei UI";
            font-size: 17px;
            font-weight: 700;
        """)
        brand_layout.addWidget(mark)

        brand_text = QVBoxLayout()
        brand_text.setContentsMargins(0, 0, 0, 0)
        brand_text.setSpacing(3)

        brand_name = QLabel("随便记")
        name_font = QFont("Microsoft YaHei UI", 13)
        name_font.setWeight(QFont.Weight.DemiBold)
        brand_name.setFont(name_font)
        brand_name.setStyleSheet("color: #2A2A26; background: transparent;")
        brand_text.addWidget(brand_name)

        brand_sub = QLabel("LOCAL VAULT")
        sub_font = QFont("Microsoft YaHei UI", 6)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.6)
        brand_sub.setFont(sub_font)
        brand_sub.setStyleSheet("color: #96917F; background: transparent;")
        brand_text.addWidget(brand_sub)

        brand_layout.addLayout(brand_text)
        brand_layout.addStretch()
        sidebar_layout.addWidget(brand)

        sidebar_layout.addSpacing(32)

        nav_label = QLabel("分类")
        nav_font = QFont("Microsoft YaHei UI", 7)
        nav_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.8)
        nav_label.setFont(nav_font)
        nav_label.setStyleSheet("color: #96917F; background: transparent; padding-left: 12px;")
        sidebar_layout.addWidget(nav_label)
        sidebar_layout.addSpacing(8)

        # 分类列表
        self.category_widgets = {}
        nav_box = QVBoxLayout()
        nav_box.setContentsMargins(0, 0, 0, 0)
        nav_box.setSpacing(2)
        for category, config in self.CATEGORY_CONFIG.items():
            count = self._get_category_count(category)
            category_item = CategoryItem(
                config["icon"], config["name"], config["en"], count, category, self, self
            )
            nav_box.addWidget(category_item)
            self.category_widgets[category] = category_item
        sidebar_layout.addLayout(nav_box)

        sidebar_layout.addStretch()

        # 底部:安全提示 + 设置 + 版本
        hint = QFrame()
        hint.setStyleSheet("background-color: #EDE9DE; border-radius: 10px;")
        hint_layout = QHBoxLayout(hint)
        hint_layout.setContentsMargins(10, 9, 10, 9)
        hint_layout.setSpacing(8)

        shield = QLabel()
        shield.setPixmap(line_icon("shield", "#7C786C", 16))
        shield.setFixedSize(16, 16)
        hint_layout.addWidget(shield, alignment=Qt.AlignmentFlag.AlignTop)

        hint_text = QLabel("AES-256 本地加密\n数据不会离开本机")
        hint_font = QFont("Microsoft YaHei UI", 8)
        hint_text.setFont(hint_font)
        hint_text.setStyleSheet("color: #7C786C; background: transparent;")
        hint_layout.addWidget(hint_text)
        hint_layout.addStretch()
        sidebar_layout.addWidget(hint)
        sidebar_layout.addSpacing(10)

        self.settings_btn = QPushButton("  设置")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setFixedHeight(38)
        self.settings_btn.setIcon(QIcon(line_icon("sliders", "#5C594F", 17)))
        self.settings_btn.setIconSize(QSize(17, 17))
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                background-color: transparent;
                color: #2A2A26;
                border: none;
                border-radius: 10px;
                padding: 0 10px;
                font-size: 12.5px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #EDE9DE;
            }}
        """)
        self.settings_btn.clicked.connect(self._show_settings)
        sidebar_layout.addWidget(self.settings_btn)

        self.lock_btn = QPushButton("  锁定")
        self.lock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_btn.setFixedHeight(38)
        self.lock_btn.setIcon(QIcon(line_icon("shield", "#5C594F", 17)))
        self.lock_btn.setIconSize(QSize(17, 17))
        self.lock_btn.setToolTip("立即锁定(Ctrl+L)")
        self.lock_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                background-color: transparent;
                color: #2A2A26;
                border: none;
                border-radius: 10px;
                padding: 0 10px;
                font-size: 12.5px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #EDE9DE;
            }}
        """)
        self.lock_btn.clicked.connect(self.lock)
        sidebar_layout.addWidget(self.lock_btn)

        version_label = QLabel("v1.0.1 · Paperlight")
        version_font = QFont("Microsoft YaHei UI", 7)
        version_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.6)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #ABA69A; background: transparent; padding-left: 12px;")
        sidebar_layout.addSpacing(8)
        sidebar_layout.addWidget(version_label)

        parent_layout.addWidget(sidebar)

    def _setup_content(self, parent_layout):
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_app']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 30, 36, 26)
        content_layout.setSpacing(0)

        # 页头:eyebrow + 大标题 + 副标题,右侧搜索与添加
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(14)

        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(6)

        self.eyebrow_label = QLabel(self.CATEGORY_CONFIG[self.current_category]["en"])
        eyebrow_font = QFont("Microsoft YaHei UI", 7)
        eyebrow_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        self.eyebrow_label.setFont(eyebrow_font)
        self.eyebrow_label.setStyleSheet(f"color: {COLORS['text_faint']};")
        title_box.addWidget(self.eyebrow_label)

        self.page_title = QLabel(self.CATEGORY_CONFIG[self.current_category]["name"])
        page_font = QFont("Microsoft YaHei UI", 21)
        page_font.setWeight(QFont.Weight.DemiBold)
        self.page_title.setFont(page_font)
        self.page_title.setStyleSheet(f"color: {COLORS['text_dark']};")
        title_box.addWidget(self.page_title)

        self.page_subtitle = QLabel()
        self.page_subtitle.setFont(QFont("Microsoft YaHei UI", 9))
        self.page_subtitle.setStyleSheet(f"color: {COLORS['text_gray']};")
        title_box.addWidget(self.page_subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.search_input = StyledInput()
        self.search_input.setFixedSize(240, 38)
        self.search_input.setPlaceholderText("搜索记录…")
        self.search_input.textChanged.connect(self._search_items)
        header_layout.addWidget(self.search_input, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.add_btn = StyledButton("+  添加记录", StyledButton.BUTTON_STYLE_PRIMARY)
        self.add_btn.setMinimumWidth(112)
        self.add_btn.clicked.connect(self._add_item)
        header_layout.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        content_layout.addWidget(header)
        content_layout.addSpacing(20)

        # 操作行:左类型筛选 + 提示,右编辑/删除
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        # 类型下拉筛选:仅"账号密码"分类出现,位置贴近表格"类型"列
        self.type_filter_label = QLabel("类型")
        self.type_filter_label.setFont(QFont("Microsoft YaHei UI", 9))
        self.type_filter_label.setStyleSheet(f"color: {COLORS['text_faint']};")
        actions_layout.addWidget(self.type_filter_label)

        self.type_filter = PaperComboBox()
        self.type_filter.setFixedSize(128, 32)
        self.type_filter.setToolTip("按类型筛选记录")
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_surface']};
                color: {COLORS['text_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 9px;
                padding: 0 28px 0 11px;
                font-size: 12px;
                min-height: 30px;
            }}
            QComboBox:hover {{
                border-color: #DCD6C7;
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 26px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }}
        """)
        self.type_filter.view().setStyleSheet(f"""
            QListView {{
                background-color: {COLORS['bg_surface']};
                color: {COLORS['text_dark']};
                border: 1px solid {COLORS['border']};
                padding: 4px;
                outline: none;
                selection-background-color: {COLORS['accent_soft']};
                selection-color: {COLORS['text_dark']};
            }}
            QListView::item {{
                min-height: 28px;
                padding-left: 8px;
            }}
            QListView::item:selected {{
                background-color: {COLORS['accent_soft']};
                color: {COLORS['text_dark']};
            }}
            QListView::item:hover {{
                background-color: {COLORS['row_hover']};
            }}
        """)
        self.type_filter.currentIndexChanged.connect(self._on_type_filter_changed)
        self._populate_type_filter()
        actions_layout.addWidget(self.type_filter, alignment=Qt.AlignmentFlag.AlignVCenter)
        actions_layout.addSpacing(6)

        action_hint = QLabel("选中一行后可编辑或删除")
        action_hint.setFont(QFont("Microsoft YaHei UI", 9))
        action_hint.setStyleSheet(f"color: {COLORS['text_faint']};")
        actions_layout.addWidget(action_hint)
        actions_layout.addStretch()

        self.edit_btn = StyledButton("编辑")
        self.edit_btn.setFixedSize(64, 34)
        self.edit_btn.clicked.connect(self._edit_item)
        actions_layout.addWidget(self.edit_btn)

        self.delete_btn = StyledButton("删除", StyledButton.BUTTON_STYLE_DANGER)
        self.delete_btn.setFixedSize(64, 34)
        self.delete_btn.clicked.connect(self._delete_item)
        actions_layout.addWidget(self.delete_btn)

        content_layout.addWidget(actions)
        content_layout.addSpacing(12)

        # 表格卡片:白纸 + 细描边 + 轻阴影
        table_container = QFrame()
        table_container.setObjectName("tableCard")
        table_container.setStyleSheet(f"""
            QFrame#tableCard {{
                background-color: {COLORS['bg_surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
            }}
        """)
        card_shadow = QGraphicsDropShadowEffect(table_container)
        card_shadow.setBlurRadius(30)
        card_shadow.setOffset(0, 10)
        card_shadow.setColor(QColor(40, 38, 30, 16))
        table_container.setGraphicsEffect(card_shadow)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)

        # 表格
        self.table = QTableWidget()
        self.table.setFont(QFont("Microsoft YaHei UI", 10))
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.viewport().setAutoFillBackground(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.horizontalHeader().setFixedHeight(38)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setItemDelegate(RowAccentDelegate(self.table))
        self.table.cellClicked.connect(self._on_row_clicked)

        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        table_layout.addWidget(self.table, stretch=1)

        self.empty_label = QLabel("还没有任何记录\n点击右上角「+ 添加记录」创建第一条")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            f"color: {COLORS['text_faint']}; font-size: 12.5px; background: transparent;"
        )
        self.empty_label.hide()
        table_layout.addWidget(self.empty_label, stretch=1)

        content_layout.addWidget(table_container, stretch=1)
        content_layout.addSpacing(12)

        footer = QLabel("右键任意记录可快速复制字段 / AES-256 加密")
        footer_font = QFont("Microsoft YaHei UI", 8)
        footer_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.4)
        footer.setFont(footer_font)
        footer.setStyleSheet(f"color: {COLORS['text_faint']};")
        content_layout.addWidget(footer)

        parent_layout.addWidget(content, stretch=1)

    # 分类配置,集中管理各分类的元数据
    # fields 元组:(field_key, label, table_mode, searchable)
    #   table_mode: "text" 原值 | "mask" 掩码 | "truncate" 截断 | "tags" join 标签
    #   searchable: 是否参与搜索匹配
    CATEGORY_CONFIG = {
        "accounts": {
            "name": "账号密码",
            "en": "ACCOUNTS",
            "icon": "key",
            "attr": "accounts",
            "add_method": "add_account",
            "update_method": "update_account",
            "delete_method": "delete_account",
            "tags_field": None,
            "fields": [
                ("account_type", "类型", "text", True),
                ("website", "网站", "text", True),
                ("username", "用户名", "text", True),
                ("url", "网址", "text", True),
            ],
            "edit_fields": [
                "account_type",
                "website",
                "username",
                "password",
                "url",
                "notes",
            ],
            "copy_fields": [
                ("username", "复制用户名"),
                ("password", "复制密码"),
            ],
        },
        "ideas": {
            "name": "想法记录",
            "en": "IDEAS",
            "icon": "bulb",
            "attr": "ideas",
            "add_method": "add_idea",
            "update_method": "update_idea",
            "delete_method": "delete_idea",
            "tags_field": "tags",
            "fields": [
                ("title", "标题", "text", True),
                ("content", "内容", "truncate", True),
                ("tags", "标签", "tags", False),
            ],
            "edit_fields": ["title", "content", "tags"],
            "copy_fields": [
                ("title", "复制标题"),
                ("content", "复制内容"),
                ("tags", "复制标签"),
            ],
        },
        "wallets": {
            "name": "钱包地址",
            "en": "WALLETS",
            "icon": "wallet",
            "attr": "wallets",
            "add_method": "add_wallet",
            "update_method": "update_wallet",
            "delete_method": "delete_wallet",
            "tags_field": None,
            "fields": [
                ("name", "名称", "text", True),
                ("address", "地址", "text", True),
                ("wallet_type", "类型", "text", False),
                ("notes", "备注", "text", False),
            ],
            "edit_fields": ["name", "address", "wallet_type", "notes"],
            "copy_fields": [
                ("address", "复制地址"),
                ("name", "复制名称"),
                ("wallet_type", "复制类型"),
                ("notes", "复制备注"),
            ],
        },
        "prompts": {
            "name": "AI提示词",
            "en": "PROMPTS",
            "icon": "sparkles",
            "attr": "prompts",
            "add_method": "add_prompt",
            "update_method": "update_prompt",
            "delete_method": "delete_prompt",
            "tags_field": None,
            "fields": [
                ("title", "标题", "text", True),
                ("content", "内容", "truncate", True),
                ("category", "分类", "text", False),
            ],
            "edit_fields": ["title", "content", "category"],
            "copy_fields": [
                ("title", "复制标题"),
                ("content", "复制内容"),
                ("category", "复制分类"),
            ],
        },
    }

    def _get_category_records(self, category: str):
        """获取指定分类的所有记录"""
        config = self.CATEGORY_CONFIG.get(category)
        if not config:
            return []
        return getattr(self.data_manager.record_manager, config["attr"], [])

    def _get_category_count(self, category: str) -> int:
        """获取指定分类的记录数量"""
        return len(self._get_category_records(category))

    def _update_category_count(self):
        for category, widget in self.category_widgets.items():
            count = self._get_category_count(category)
            widget.update_count(count)

    def _switch_category(self, category: str):
        """切换当前分类"""
        self.current_category = category
        self.selected_item_id = None
        self.table.clearSelection()
        self.search_input.clear()
        config = self.CATEGORY_CONFIG.get(category, {})
        self.eyebrow_label.setText(config.get("en", ""))
        self.page_title.setText(config.get("name", ""))
        for name, widget in self.category_widgets.items():
            widget.set_active(name == category)
        # 类型筛选只对"账号密码"有意义,切换分类时复位并显隐
        is_accounts = category == "accounts"
        self.type_filter_label.setVisible(is_accounts)
        self.type_filter.setVisible(is_accounts)
        if is_accounts:
            self.type_filter.blockSignals(True)
            self.type_filter.setCurrentIndex(0)
            self.type_filter.blockSignals(False)
        self._load_data()

    def _populate_type_filter(self):
        """重建类型下拉项:设置中的类型 + 记录里实际出现过的类型。"""
        previous = self.type_filter.currentData() if self.type_filter.count() else None
        types = list(self.app_settings.account_types)
        for record in self._get_category_records("accounts"):
            record_type = (getattr(record, "account_type", "") or "").strip()
            if record_type and record_type not in types:
                types.append(record_type)

        self.type_filter.blockSignals(True)
        self.type_filter.clear()
        self.type_filter.addItem("全部类型", None)
        for type_name in types:
            self.type_filter.addItem(type_name, type_name)
        self.type_filter.addItem("未分类", "__untagged__")
        if previous is not None:
            idx = self.type_filter.findData(previous)
            if idx >= 0:
                self.type_filter.setCurrentIndex(idx)
        self.type_filter.blockSignals(False)

    def _type_filter_active(self) -> bool:
        """当前是否处于类型筛选状态(仅账号分类有效)。"""
        if self.current_category != "accounts" or not hasattr(self, "type_filter"):
            return False
        return self.type_filter.currentIndex() > 0

    def _matches_type_filter(self, record) -> bool:
        """记录是否通过类型筛选。"""
        if self.current_category != "accounts":
            return True
        selected = self.type_filter.currentData()
        if selected is None:
            return True
        record_type = (getattr(record, "account_type", "") or "").strip()
        if selected == "__untagged__":
            return not record_type
        return record_type == selected

    def _on_type_filter_changed(self, _index: int):
        """类型下拉变化时立即重新过滤表格。"""
        self.selected_item_id = None
        self.table.clearSelection()
        self._refresh_records()

    def _sync_page_meta(self, count: int):
        """同步副标题记录数与空状态提示。"""
        filtering = bool(self.search_input.text().strip()) or self._type_filter_active()
        if filtering:
            self.page_subtitle.setText(f"找到 {count} 条记录 · 本地加密存储")
        else:
            self.page_subtitle.setText(f"{count} 条记录 · 本地加密存储")
        if count == 0 and filtering:
            self.empty_label.setText("没有匹配的记录\n换个关键词或类型试试")
        else:
            self.empty_label.setText("还没有任何记录\n点击右上角「+ 添加记录」创建第一条")
        has_rows = count > 0
        self.table.setVisible(has_rows)
        self.empty_label.setVisible(not has_rows)

    def _record_to_row_items(self, record) -> list:
        """将记录对象转换为表格行数据(配置驱动)"""
        config = self.CATEGORY_CONFIG[self.current_category]
        items = []
        for field_key, label, mode, searchable in config["fields"]:
            value = getattr(record, field_key, None)
            if mode == "mask":
                items.append("••••••••")
            elif mode == "truncate":
                text = value or ""
                items.append(text[:50] + "..." if len(text) > 50 else text)
            elif mode == "tags":
                items.append(", ".join(value) if value else "")
            else:  # text
                items.append(value or "")
        return items

    def _load_data(self):
        """加载当前分类的数据到表格(应用搜索与类型筛选)"""
        self._populate_type_filter()
        self._update_category_count()
        self._refresh_records()

    def _refresh_records(self):
        """按当前搜索关键词 + 类型筛选重建表格内容。"""
        config = self.CATEGORY_CONFIG.get(self.current_category, {})
        headers = [label for _, label, _, _ in config.get("fields", [])]
        records = self._get_category_records(self.current_category)

        text_lower = self.search_input.text().strip().lower()
        if text_lower:
            records = [r for r in records if self._record_matches_search(r, text_lower)]
        records = [r for r in records if self._matches_type_filter(r)]

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            items = self._record_to_row_items(record)
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.filtered_records = records
        self._sync_page_meta(len(records))

    def _on_row_clicked(self, row, col):
        self.selected_item_id = self._get_record_id(row)

    def _get_record_id(self, row: int) -> Optional[str]:
        """根据行号获取记录ID"""
        if 0 <= row < len(self.filtered_records):
            return self.filtered_records[row].id
        return None

    def _get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """根据ID获取记录数据字典(配置驱动)"""
        config = self.CATEGORY_CONFIG[self.current_category]
        records = self._get_category_records(self.current_category)
        # 使用 edit_fields(完整字段) 或 fields(表格字段)
        field_list = [f for f in config.get("edit_fields", [])] if "edit_fields" in config else None
        if field_list is None:
            field_list = [f[0] for f in config["fields"]]
        for record in records:
            if record.id == record_id:
                result = {"id": record.id}
                for field_key in field_list:
                    value = getattr(record, field_key, None)
                    # tags 字段特殊处理:list -> 逗号分隔字符串
                    if field_key == config.get("tags_field"):
                        result[field_key] = ", ".join(value) if value else ""
                    else:
                        result[field_key] = value
                return result
        return None

    def _add_item(self):
        dialog = ItemDialog(self.current_category, app_settings=self.app_settings, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_result()
        if not data:
            return

        config = self.CATEGORY_CONFIG[self.current_category]
        tags_field = config["tags_field"]
        # 使用 edit_fields(完整字段集)构造 add 方法的参数;
        # 不能用 fields(仅用于表格显示,可能缺少 password/notes 等敏感字段),
        # 否则会导致 accounts 的 password 被错填为 url、notes 丢失。
        edit_fields = config.get("edit_fields") or [f[0] for f in config["fields"]]
        args = []
        for field_key in edit_fields:
            if field_key == tags_field:
                args.append([t.strip() for t in data.get(field_key, "").split(",") if t.strip()])
            else:
                args.append(data.get(field_key, ""))
        new_record = getattr(self.data_manager, config["add_method"])(*args)
        # 新记录若不满足当前类型筛选,复位为"全部类型",避免刚添加就看不见
        if new_record is not None and not self._matches_type_filter(new_record):
            self.type_filter.blockSignals(True)
            self.type_filter.setCurrentIndex(0)
            self.type_filter.blockSignals(False)
        self._load_data()

    def _edit_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择要编辑的记录")
            return

        record_id = self._get_record_id(current_row)
        if not record_id:
            return

        data = self._get_record_by_id(record_id)
        dialog = ItemDialog(self.current_category, data, self.app_settings, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        new_data = dialog.get_result()
        if not new_data:
            return

        config = self.CATEGORY_CONFIG[self.current_category]
        tags_field = config["tags_field"]
        # 使用 edit_fields(完整字段集)构造 update 方法的参数,
        # 确保 password/notes 等表格中不显示的字段也能被正确更新。
        edit_fields = config.get("edit_fields") or [f[0] for f in config["fields"]]
        kwargs = {}
        for field_key in edit_fields:
            if field_key == tags_field:
                kwargs[field_key] = [t.strip() for t in new_data.get(field_key, "").split(",") if t.strip()]
            else:
                kwargs[field_key] = new_data.get(field_key, "")
        getattr(self.data_manager, config["update_method"])(record_id, **kwargs)
        self._load_data()

    def _delete_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的记录")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return
        record_id = self._get_record_id(current_row)
        if record_id:
            config = self.CATEGORY_CONFIG[self.current_category]
            getattr(self.data_manager, config["delete_method"])(record_id)
            self._load_data()

    def _copy_field_value(self, field_key: str):
        """复制当前选中记录的指定字段到剪贴板,密码类字段定时自动清空。"""
        record_id = self._get_record_id(self.table.currentRow())
        if not record_id:
            return
        data = self._get_record_by_id(record_id)
        value = data.get(field_key, "")
        text = "" if value is None else str(value)
        QApplication.clipboard().setText(text)

        if field_key == "password" and text:
            self._clipboard_token = text
            self._clipboard_timer.start(CLIPBOARD_CLEAR_MS)
            self.show_toast(f"密码已复制,{CLIPBOARD_CLEAR_MS // 1000} 秒后自动清空剪贴板")
        else:
            self.show_toast("已复制")

    def _clear_clipboard(self):
        """只清空自己写入的内容,避免清掉用户后来复制的东西。"""
        clipboard = QApplication.clipboard()
        if self._clipboard_token and clipboard.text() == self._clipboard_token:
            clipboard.clear()
        self._clipboard_token = ""

    def show_toast(self, text: str, duration: int = 1800):
        """在主窗口底部显示一条短暂提示。"""
        toast = QLabel(text, self)
        toast.setFont(QFont("Microsoft YaHei UI", 9))
        toast.setStyleSheet("""
            QLabel {
                background-color: #2A2A26;
                color: #FBF9F3;
                border-radius: 10px;
                padding: 9px 16px;
            }
        """)
        toast.adjustSize()
        rect = self.rect()
        toast.move(rect.center().x() - toast.width() // 2, rect.bottom() - 96)
        toast.show()
        toast.raise_()
        QTimer.singleShot(duration, toast.deleteLater)

    def _show_context_menu(self, pos):
        # 先选中鼠标所在的行,避免操作到上一次选中的记录
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        self.table.selectRow(index.row())
        self.table.setCurrentCell(index.row(), index.column())

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS["bg_surface"]};
                color: {COLORS["text_dark"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 10px;
                padding: 6px;
                font-size: 12.5px;
            }}
            QMenu::item {{
                padding: 7px 22px 7px 14px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS["accent_soft"]};
                color: {COLORS["primary"]};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {COLORS["border"]};
                margin: 5px 8px;
            }}
        """)

        add_action = QAction("添加", self)
        add_action.triggered.connect(self._add_item)
        menu.addAction(add_action)

        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self._edit_item)
        menu.addAction(edit_action)

        menu.addSeparator()

        # 复制字段(配置驱动)
        config = self.CATEGORY_CONFIG.get(self.current_category, {})
        for field_key, label in config.get("copy_fields", []):
            copy_action = QAction(label, self)
            copy_action.triggered.connect(lambda checked, fk=field_key: self._copy_field_value(fk))
            menu.addAction(copy_action)

        menu.addSeparator()

        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self._delete_item)
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _show_settings(self):
        """打开设置对话框。"""
        dialog = SettingsDialog(self.app_settings, self.data_manager,
                                current_password=self.current_password, parent=self)
        dialog.exec()
        # 设置里可能改了主密码,同步内存中的旧密码(用于免密缓存)
        if getattr(dialog, "_password_changed", False) and dialog.current_password:
            self.current_password = dialog.current_password
            self.show_toast("主密码已更新,下次登录请使用新密码")
        # 设置里可能增删了账号类型,重载以同步筛选项
        self._load_data()

    def _record_matches_search(self, record, text_lower: str) -> bool:
        """检查记录是否匹配搜索文本(配置驱动)"""
        config = self.CATEGORY_CONFIG[self.current_category]
        for field_key, label, mode, searchable in config["fields"]:
            if not searchable:
                continue
            value = getattr(record, field_key, None)
            if value and text_lower in str(value).lower():
                return True
        return False

    def _search_items(self, text: str):
        """搜索并显示匹配的记录(与类型筛选叠加生效)"""
        # 重置选中状态
        self.selected_item_id = None
        self.table.clearSelection()
        self._refresh_records()


def _try_auto_login(data_manager: DataManager, app_settings: "AppSettings") -> Optional[str]:
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
                      mode: str = PasswordDialog.MODE_VERIFY) -> Optional[str]:
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


def _setup_logging(log_dir: Optional[Path] = None):
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
    data_dir = resolve_data_dir()
    _setup_logging(data_dir)
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setWindowIcon(app_icon())

    # 单实例:第二个进程唤醒第一个后直接退出,避免两个进程互相覆盖数据
    window_holder: Dict[str, Any] = {}

    def _activate_existing():
        window = window_holder.get("window")
        if window is None:
            return
        if window.isMinimized():
            window.showNormal()
        window.show()
        window.raise_()
        window.activateWindow()

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
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
