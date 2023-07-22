from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class ScrollableContent(QScrollArea):
    def __init__(self, content, parent=None):
        super(ScrollableContent, self).__init__(parent)
        self.content = content
        self.initUI(content)

    def initUI(self, content):
        self.setWidgetResizable(True)
        self.adjustSize()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setMinimumHeight(600 * UIRescale.Scale)
        # self.setMaximumHeight(1000 * UIRescale.Scale)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.setStyleSheet(
            """
            QScrollArea {
                height: 1000px;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                width: 10px;
                background-color: rgba(50, 50, 50, 255);
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: gray;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background-color: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
            """
        )

        self.content = QWidget(self)
        self.content.setContentsMargins(0, 0, 0, 0)

        content_layout = QVBoxLayout(self)
        for item in content:
            content_layout.addWidget(item, alignment=Qt.AlignTop)
        self.content.setLayout(content_layout)

        self.setWidget(self.content)
