from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class MultiButton(QWidget):
    checkedStateChanged = Signal(int)

    def __init__(self, states, height, parent=None):
        super(MultiButton, self).__init__(parent)
        self.states = states
        self.initUI(states, height)

    def initUI(self, states, height):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.button_group = QButtonGroup()
        i = 0
        for state in states:
            button = QPushButton()
            button.setCheckable(True)
            if i == 0:
                button.setChecked(True)
                button.setStyleSheet("QPushButton:checked { background-color: rgba(40, 40, 40, 255); } QPushButton:pressed { background-color: rgba(50, 50, 50, 255); } QPushButton { background-color: rgba(90, 90, 90, 255); border-top-left-radius: 3px; border-bottom-left-radius: 3px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; color: white; }")
            elif i == len(states) - 1:
                button.setStyleSheet("QPushButton:checked { background-color: rgba(40, 40, 40, 255); } QPushButton:pressed { background-color: rgba(50, 50, 50, 255); } QPushButton { background-color: rgba(90, 90, 90, 255); border-top-right-radius: 3px; border-bottom-right-radius: 3px; border-top-left-radius: 0px; border-bottom-left-radius: 0px; color: white; }")
            else:
                button.setStyleSheet("QPushButton:checked { background-color: rgba(40, 40, 40, 255); } QPushButton:pressed { background-color: rgba(50, 50, 50, 255); } QPushButton { background-color: rgba(90, 90, 90, 255); border-radius: 0px; color: white; }")
            button.setFixedSize(height * 1.5, height)
            button.setText(state)
            button.setObjectName(state)
            self.button_group.addButton(button, i)
            layout.addWidget(button)
            i = i + 1

        self.button_group.buttonClicked.connect(self.on_button_checked)

        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("border-radius: 5px;")

    def on_button_checked(self, button):
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item is not None:
                widget = item.widget()
                if isinstance(widget, QPushButton) and widget is not button:
                    widget.setChecked(False)
        button.setChecked(True)

    def get_button(self, id):
        return self.button_group.button(id)