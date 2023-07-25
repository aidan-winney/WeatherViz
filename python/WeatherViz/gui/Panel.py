from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class Panel(QWidget):
    def __init__(self, title, tooltip, content, parent=None):
        super(Panel, self).__init__(parent)
        self.title = title
        self.expanded = False
        self.content = content
        self.initUI(title, tooltip, content)
        self.content.setContentsMargins(0, 0, 0, 10 * UIRescale.Scale)

    def initUI(self, title, tooltip, content):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.header = QWidget()
        header_layout = QHBoxLayout()
        self.header.setMaximumHeight(40 * UIRescale.Scale)

        self.titleLabel = QLabel(self.title)
        self.titleLabel.setStyleSheet("font-weight: bold; color: white")
        header_layout.addWidget(self.titleLabel)
        info_icon = QIcon("WeatherViz/python/WeatherViz/assets/tooltip.png")
        self.info_label = QLabel()
        self.info_label.setPixmap(info_icon.pixmap(16 * UIRescale.Scale, 16 * UIRescale.Scale))
        self.info_label.setToolTip(tooltip)
        self.info_label.setWindowFlag(Qt.ToolTip)
        self.info_label.setToolTipDuration(5000)
        self.info_label.setStyleSheet("""QToolTip {
                    background-color: rgba(100, 100, 100, 255);
                    color: white;
                    font-weight: bold;
                    border-radius: 10px
                }""")
        self.info_label.setContentsMargins(10 * UIRescale.Scale, 0, 0, 0)
        header_layout.addWidget(self.info_label)
        header_layout.addStretch(1)

        self.header.setLayout(header_layout)

        layout.addWidget(self.header)
        self.content = QWidget()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setMaximumHeight(150 * UIRescale.Scale)
        layout.addWidget(self.content)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(20 * UIRescale.Scale)
        for item in content:
            content_layout.addWidget(item)
        self.content.setLayout(content_layout)
        self.setLayout(layout)
