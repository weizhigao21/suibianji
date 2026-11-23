"""主题、配色与自绘控件(纸间 · Paperlight)。"""

from PyQt6.QtCore import QLineF, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QTextEdit,
)

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


