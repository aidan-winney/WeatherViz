from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class QueryPane(QWidget):
    def __init__(self, content, parent=None):
        super(QueryPane, self).__init__(parent)
        self.content = content
        self.initUI(content)

    def initUI(self, content):
        self.setMaximumWidth(400 * UIRescale.Scale)

        layout = QVBoxLayout()
        layout.setContentsMargins(5 * UIRescale.Scale, 5 * UIRescale.Scale, 5 * UIRescale.Scale, 5 * UIRescale.Scale)

        self.content = QWidget()
        self.content.setContentsMargins(20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale)
        self.content.setStyleSheet("background-color: rgba(60, 60, 60, 255); border-radius: 5px; font-weight: bold; color: white")
        # self.content.setMaximumHeight(200 * UIRescale.Scale)
        layout.addWidget(self.content)
        layout.addStretch(1)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(20 * UIRescale.Scale)
        for item in content:
            content_layout.addWidget(item)
        self.content.setLayout(content_layout)
        self.setLayout(layout)
