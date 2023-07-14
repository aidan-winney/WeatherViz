from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtGui import QPainter, Qt, QBrush, QColor
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class Toolbar(QWidget):
    def __init__(self, content, parent=None):
        super(Toolbar, self).__init__(parent)
        self.initUI(content)

    def initUI(self, content):
        self.setMaximumHeight(80 * UIRescale.Scale)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20 * UIRescale.Scale, 10 * UIRescale.Scale, 20 * UIRescale.Scale, 10 * UIRescale.Scale)
        content_layout.setSpacing(20 * UIRescale.Scale)
        for item in content:
            content_layout.addWidget(item)
        self.setLayout(content_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(90, 90, 90, 120)))
        painter.drawRoundedRect(self.rect(), 5, 5)
