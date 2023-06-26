from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle


class CollapsiblePanel(QWidget):
    def __init__(self, title, content, parent=None):
        super(CollapsiblePanel, self).__init__(parent)
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
        self.header_background.setGeometry(self.header.rect().x(), self.header.rect().y(), self.header.rect().width()*2, self.header.rect().height())

        self.titleLabel = QLabel(self.title)
        self.titleLabel.setStyleSheet("font-weight: bold; color: white")

        self.toggleButton = QPushButton("▼")
        self.toggleButton.setFixedSize(20 * UIRescale.Scale, 20 * UIRescale.Scale)
        self.toggleButton.setCheckable(True)
        self.toggleButton.clicked.connect(self.toggleContent)

        header_layout.addWidget(self.titleLabel)
        header_layout.addStretch(1)
        header_layout.addWidget(self.toggleButton)

        self.header.setLayout(header_layout)

        layout.addWidget(self.header)
        self.content = QWidget()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setStyleSheet("background-color: rgba(90, 90, 90, 210); border-radius: 5px; font-weight: bold; color: white")
        self.content.setMaximumHeight(0)
        layout.addWidget(self.content)
        layout.addStretch(1)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)
        for item in content:
            content_layout.addWidget(item)
        self.content.setLayout(content_layout)
        self.setLayout(layout)

    def toggleContent(self):
        self.expanded = not self.expanded
        animation = QPropertyAnimation(self.content, b"maximumHeight")
        animation.setDuration(900)
        if self.expanded:
            # self.toggleButton.setText("▼")
            # self.collapseAnimation()
            animation.setStartValue(self.content.layout().sizeHint().height())
            animation.setEndValue(0)
        else:
            # self.toggleButton.setText("▲")
            animation.setStartValue(0)
            animation.setEndValue(self.content.layout().sizeHint().height())
            # self.expandAnimation()
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    def expandAnimation(self):
        self.animation = QPropertyAnimation(self.content, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(QRect(self.x(), self.y(), self.width(), 0))
        self.animation.setEndValue(QRect(self.x(), self.y(), self.width(), self.content.sizeHint().height()))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def collapseAnimation(self):
        self.animation = QPropertyAnimation(self.content, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(QRect(self.x(), self.y(), self.width(), self.content.sizeHint().height()))
        self.animation.setEndValue(QRect(self.x(), self.y(), self.width(), 0))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()