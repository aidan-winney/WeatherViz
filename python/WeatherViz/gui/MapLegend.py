import sys
from PySide2.QtCore import QRect, QSize
from PySide2.QtGui import QPainter, QPainterPath, QFont, Qt, QColor
from PySide2.QtWidgets import QWidget
from WeatherViz.UIRescale import UIRescale


class MapLegend(QWidget):
    def __init__(self, colors, labels, title, parent=None):
        super().__init__(parent)

        self.colors = colors
        self.labels = labels
        self.title = title

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        legend_height = 25 * UIRescale.Scale
        label_height = 25 * UIRescale.Scale
        title_height = 25 * UIRescale.Scale
        total_height = (len(self.labels) * label_height) + legend_height + title_height

        painter_path = QPainterPath()
        painter_path.addRoundedRect(0, 0, self.width(), total_height + 15 * UIRescale.Scale, 5, 5)
        painter.fillPath(painter_path, QColor(50, 50, 50, 120))

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(Qt.white)

        title_rect = QRect(5 * UIRescale.Scale, 10 * UIRescale.Scale, self.width() - 10 * UIRescale.Scale, title_height)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

        font.setBold(False)
        font.setPointSize(10)
        painter.setFont(font)

        for i, color in enumerate(self.colors):
            x = 20
            y = title_height + (i * label_height) + 20 * UIRescale.Scale
            color_rect = QRect(x, y, legend_height, legend_height)
            painter.fillRect(color_rect, QColor(*color))

            label_rect = QRect(x + legend_height + 5, y, self.width() - legend_height - 10 * UIRescale.Scale, label_height)
            painter.drawText(label_rect, Qt.AlignLeft, self.labels[i])

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        return QSize(200 * UIRescale.Scale, 150 * UIRescale.Scale)
