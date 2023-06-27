from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter, QColor, QBrush, Qt
from PySide2.QtWidgets import QWidget


class TransparentRectangle(QWidget):
    def __init__(self, parent=None):
        super(TransparentRectangle, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(90, 90, 90, 255)))
        painter.drawRoundedRect(self.rect(), 5, 5)