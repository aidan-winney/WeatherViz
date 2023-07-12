from PySide2.QtGui import Qt, QPainter, QColor, QBrush
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QProgressBar

from WeatherViz.gui.TransparentRectangle import TransparentRectangle


class ProgressBar(QWidget):
    progress_value = 0
    total = 1
    def __init__(self, parent=None):
        super(ProgressBar, self).__init__(parent)

        layout = QVBoxLayout()
        # layout.setSpacing(5)
        # layout.setMargin(5)
        # layout.setContentsMargins(5,5,5,5)
        self.progress = QProgressBar(self)
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("font-weight: bold")

        layout.addWidget(self.progress)

        self.setLayout(layout)
        #
        # self.background = TransparentRectangle(self)
        # self.background.setGeometry(self.rect().x(), self.rect().y(), self.progress.rect().width(), self.progress.rect().height())
        # self.progress.show()
    def set_progress(self, progress, total):
        self.progress_value = progress
        self.total = total
        self.progress.setValue((progress / total) * 100)

    def set_total(self, total):
        self.total = total

    def increment_progress(self):
        self.progress_value+=1
        print(self.progress_value)
        self.progress.setValue((self.progress_value / self.total) * 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(90, 90, 90, 255)))
        painter.drawRoundedRect(self.rect(), 5, 5)