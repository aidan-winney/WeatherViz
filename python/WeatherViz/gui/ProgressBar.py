from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QProgressBar


class ProgressBar(QWidget):
    def __init__(self, parent=None):
        super(ProgressBar, self).__init__(parent)

        layout = QVBoxLayout()

        self.progress = QProgressBar(self)
        self.setContentsMargins(1,1,1,1)
        self.setStyleSheet("background-color: rgba(90, 90, 90, 255); border-radius: 5px; font-weight: bold; color: white")

        layout.addWidget(self.progress)

        self.setLayout(layout)

    def set_progress(self, progress, total):
        self.progress.setValue((progress // total) * 100)