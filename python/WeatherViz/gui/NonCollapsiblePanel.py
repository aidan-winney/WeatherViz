from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class NonCollapsiblePanel(QWidget):
    def __init__(self, title, content, parent=None):
        super(NonCollapsiblePanel, self).__init__(parent)
        self.title = title
        self.expanded = False
        self.content = content
        self.initUI(title, content)

    def initUI(self, title, content):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.header = QWidget()
        header_layout = QHBoxLayout()
        self.header.setMaximumHeight(40 * UIRescale.Scale)
        self.header_background = TransparentRectangle(self)
        self.header_background.setGeometry(self.header.rect().x(), self.header.rect().y() - 3, self.header.rect().width(), self.header.rect().height())

        self.titleLabel = QLabel(self.title)
        self.titleLabel.setStyleSheet("font-weight: bold; color: white")

        header_layout.addWidget(self.titleLabel)
        header_layout.addStretch(1)

        self.header.setLayout(header_layout)

        layout.addWidget(self.header)
        self.content = QWidget()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setStyleSheet("background-color: rgba(90, 90, 90, 255); border-radius: 5px; font-weight: bold; color: white")
        self.content.setMaximumHeight(150 * UIRescale.Scale)
        layout.addWidget(self.content)
        layout.addStretch(1)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(20 * UIRescale.Scale)
        for item in content:
            content_layout.addWidget(item)
        self.content.setLayout(content_layout)
        self.setLayout(layout)
