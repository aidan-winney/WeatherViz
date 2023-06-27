from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout

from WeatherViz.UIRescale import UIRescale


class PlayButton(QWidget):
    def __init__(self, slider, parent=None):
        super(PlayButton, self).__init__(parent)
        self.slider = slider

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setMargin(0)
        self.playButton = QPushButton("▶")
        self.playButton.setCheckable(True)
        button_size = 35 * UIRescale.Scale
        self.playButton.setFixedSize(button_size, button_size)
        self.playButton.toggled.connect(self.togglePlay)
        layout.addWidget(self.playButton)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.incrementSlider)

    def togglePlay(self, checked):
        if checked:
            self.playButton.setText("▢")
            self.timer.start(1000)
        else:
            self.playButton.setText("▶")
            self.timer.stop()

    def incrementSlider(self):
        current_value = self.slider.value()
        self.slider.setValue(current_value + 1)