from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout


class ArrowPad(QWidget):
    def __init__(self, parent=None):
        super(ArrowPad, self).__init__(parent)
        # Create arrow buttons
        up_button = QPushButton(QIcon("assets/up_icon.png"), "")
        down_button = QPushButton(QIcon("assets/down_icon.png"), "")
        left_button = QPushButton(QIcon("assets/left_icon.png"), "")
        right_button = QPushButton(QIcon("assets/right_icon.png"), "")

        button_size = 40
        up_button.setFixedSize(button_size, button_size)
        down_button.setFixedSize(button_size, button_size)
        left_button.setFixedSize(button_size, button_size)
        right_button.setFixedSize(button_size, button_size)

        layout = QVBoxLayout()

        h_layout = QHBoxLayout()
        h_layout.addWidget(left_button)

        middle_layout = QVBoxLayout()
        middle_layout.addWidget(up_button)
        middle_layout.addStretch(1)
        middle_layout.addWidget(down_button)

        h_layout.addLayout(middle_layout)
        h_layout.addWidget(right_button)

        layout.addLayout(h_layout)
        self.setLayout(layout)