from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout

from WeatherViz.UIRescale import UIRescale


class ArrowPad(QWidget):
    def __init__(self, parent=None):
        super(ArrowPad, self).__init__(parent)
        # Create arrow buttons
        self.up_button = QPushButton("↑")
        self.up_button.setStyleSheet("QPushButton:pressed { background-color: rgba(70, 70, 70, 200); } QPushButton { background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }")
        self.down_button = QPushButton("↓")
        self.down_button.setStyleSheet("QPushButton:pressed { background-color: rgba(70, 70, 70, 200); } QPushButton { background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }")
        self.left_button = QPushButton("←")
        self.left_button.setStyleSheet("QPushButton:pressed { background-color: rgba(70, 70, 70, 200); } QPushButton { background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }")
        self.right_button = QPushButton("→")
        self.right_button.setStyleSheet("QPushButton:pressed { background-color: rgba(70, 70, 70, 200); } QPushButton { background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }")
        self.zoom_in = QPushButton("+")
        self.zoom_in.setStyleSheet("QPushButton:pressed { background-color: rgba(70, 70, 70, 200); } QPushButton { background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }")
        self.zoom_out = QPushButton("-")
        self.zoom_out.setStyleSheet("QPushButton:pressed { background-color: rgba(70, 70, 70, 200); } QPushButton { background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }")

        button_size = 40 * UIRescale.Scale
        self.up_button.setFixedSize(button_size, button_size)
        self.down_button.setFixedSize(button_size, button_size)
        self.left_button.setFixedSize(button_size, button_size)
        self.right_button.setFixedSize(button_size, button_size)
        self.zoom_in.setFixedSize(60 * UIRescale.Scale, 35 * UIRescale.Scale)
        self.zoom_out.setFixedSize(60 * UIRescale.Scale, 35 * UIRescale.Scale)

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

        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.zoom_in)
        zoom_layout.addWidget(self.zoom_out)
        zoom_layout.setContentsMargins(0, 30 * UIRescale.Scale, 0, 0)

        layout.addLayout(zoom_layout)
        self.setLayout(layout)