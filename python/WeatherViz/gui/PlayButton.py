from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout

from WeatherViz.UIRescale import UIRescale


class PlayButton(QWidget):
    def __init__(self, slider, parent=None):
        super(PlayButton, self).__init__(parent)
        self.speed = 1000
        self.is_checked = False
        self.slider = slider

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setMargin(0)
        self.playButton = QPushButton("▶")
        self.playButton.setStyleSheet("""
                QPushButton:pressed {
                    background-color: rgba(70, 70, 70, 255); 
                }
                QPushButton:checked {
                    background-color: rgba(80, 80, 80, 255); 
                }
                QPushButton {
                    background-color: rgba(90, 90, 90, 255); font-weight: bold; color: white; border-radius: 3px }""")
        self.playButton.setCheckable(True)
        self.playButton.setFixedSize(35 * UIRescale.Scale, 35 * UIRescale.Scale)
        if not self.slider.isEnabled():
            self.playButton.setFixedWidth(0)
        self.playButton.toggled.connect(lambda: self.togglePlay(~self.is_checked))
        layout.addWidget(self.playButton)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.incrementSlider)

    def togglePlay(self, checked=True):
        self.is_checked = checked
        if self.is_checked and self.slider.isEnabled():
            self.playButton.setText("▢")
            self.timer.start(self.speed)
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

    def checkDisabled(self):
        if not self.slider.isEnabled():
            self.playButton.setFixedWidth(0)
        else:
            self.playButton.setFixedWidth(35 * UIRescale.Scale)