"""程序图标:全部用 QPainter 矢量绘制,无需外部图片资源。"""

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)

CANVAS = 256.0


def _paint(painter: QPainter):
    """在 256x256 的坐标系里绘制图标:墨绿圆角底 + 折角便签纸。"""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # 圆角墨绿底
    tile = QPainterPath()
    tile.addRoundedRect(QRectF(4, 4, 248, 248), 58, 58)
    background = QLinearGradient(0, 0, 0, 256)
    background.setColorAt(0, QColor("#3A7062"))
    background.setColorAt(1, QColor("#24483D"))
    painter.fillPath(tile, background)

    # 顶部柔光
    sheen = QLinearGradient(0, 0, 0, 150)
    sheen.setColorAt(0, QColor(255, 255, 255, 30))
    sheen.setColorAt(1, QColor(255, 255, 255, 0))
    painter.fillPath(tile, sheen)

    # 便签纸投影
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(18, 36, 30, 55))
    painter.drawRoundedRect(QRectF(64, 58, 128, 156), 20, 20)

    # 便签纸(右上折角)
    x, y, w, h, r, cut = 64.0, 52.0, 128.0, 156.0, 20.0, 30.0
    paper = QPainterPath()
    paper.moveTo(x + r, y)
    paper.lineTo(x + w - cut, y)
    paper.lineTo(x + w, y + cut)
    paper.lineTo(x + w, y + h - r)
    paper.quadTo(x + w, y + h, x + w - r, y + h)
    paper.lineTo(x + r, y + h)
    paper.quadTo(x, y + h, x, y + h - r)
    paper.lineTo(x, y + r)
    paper.quadTo(x, y, x + r, y)
    paper.closeSubpath()
    painter.fillPath(paper, QColor("#F8F5EC"))

    # 折角阴影面
    fold = QPainterPath()
    fold.moveTo(x + w - cut, y)
    fold.lineTo(x + w, y + cut)
    fold.lineTo(x + w - cut, y + cut)
    fold.closeSubpath()
    painter.fillPath(fold, QColor("#E3DAC5"))

    # 正文线条
    painter.setBrush(QColor("#2F5D50"))
    for line_y, line_w in ((104, 62), (132, 76), (160, 44)):
        painter.drawRoundedRect(QRectF(88, line_y, line_w, 10), 5, 5)

    # 底部墨绿小标记,呼应“记录”意象
    painter.setBrush(QColor("#2F5D50"))
    painter.drawEllipse(QRectF(88, 184, 9, 9))


def render_pixmap(size: int, dpr: int = 4) -> QPixmap:
    """按目标逻辑尺寸渲染图标,默认 4 倍超采样保证高分屏清晰。"""
    pixmap = QPixmap(size * dpr, size * dpr)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.scale(size * dpr / CANVAS, size * dpr / CANVAS)
    _paint(painter)
    painter.end()
    pixmap.setDevicePixelRatio(dpr)
    return pixmap


def app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(render_pixmap(size))
    return icon
