from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout

from WeatherViz.UIRescale import UIRescale


class ArrowPad(QWidget):
    def __init__(self, parent=None):
        super(ArrowPad, self).__init__(parent)
        # Create arrow buttons
        self.up_button = QPushButton(QIcon("assets/up_icon.png"), "")
        self.down_button = QPushButton(QIcon("assets/down_icon.png"), "")
        self.left_button = QPushButton(QIcon("assets/left_icon.png"), "")
        self.right_button = QPushButton(QIcon("assets/right_icon.png"), "")

        button_size = 40 * UIRescale.Scale
        self.up_button.setFixedSize(button_size, button_size)
        self.down_button.setFixedSize(button_size, button_size)
        self.left_button.setFixedSize(button_size, button_size)
        self.right_button.setFixedSize(button_size, button_size)

        layout = QVBoxLayout()

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.left_button)

        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.up_button)
        middle_layout.addStretch(1)
        middle_layout.addWidget(self.down_button)

        h_layout.addLayout(middle_layout)
        h_layout.addWidget(self.right_button)

        layout.addLayout(h_layout)
        self.setLayout(layout)