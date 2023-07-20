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
        self.playButton.setStyleSheet("background-color: rgba(90, 90, 90, 255); font-weight: bold; color: white; border-radius: 3px;")
        self.playButton.setCheckable(True)
        self.playButton.setFixedSize(35 * UIRescale.Scale, 35 * UIRescale.Scale)
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
        max_value = self.slider.maximum()
        if current_value == max_value:
            self.slider.setValue(self.slider.minimum())
        else:
            self.slider.setValue(current_value + 1)