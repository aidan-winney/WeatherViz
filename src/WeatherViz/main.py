import sys
import requests
from PySide2.QtGui import QPixmap, QPainter, QColor, QBrush, QIcon, Qt, QPainterPath
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout, QPushButton, QSlider, \
    QCalendarWidget, QApplication, QHBoxLayout, QLabel, QFrame, QRadioButton

from gui.ArrowPad import ArrowPad
from gui.CollapsiblePanel import CollapsiblePanel
from gui.Map import MapWidget
from gui.TransparentRectangle import TransparentRectangle

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.access_token = "pk.eyJ1IjoibG9yZW1pcHN1bTEiLCJhIjoiY2xqNWo1OTBrMDRqMTNkbXhocXkycmlvbiJ9.9WR3Ze-tcCfz7MQf_egtQA"
        self.setWindowTitle("WeatherViz")
        self.setContentsMargins(0, 0, 0, 0)
        self.map_widget = MapWidget(self.access_token, 0, 0, 1)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.map_widget)
        self.setLayout(self.layout)
        self.rect_item = TransparentRectangle(self)
        self.rect_item.setGeometry(30,30,1200,60)
        self.start_date = QPushButton(QIcon("assets/Calendar.png"), '  Start Date', self)
        self.start_date.setGeometry(60, 42, 190, 35)
        self.start_date.clicked.connect(self.show_calendar)
        self.end_date = QPushButton(QIcon("assets/Calendar.png"), '  End Date', self)
        self.end_date.setGeometry(270, 42, 190, 35)
        self.end_date.clicked.connect(self.show_calendar)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(500, 35, 600, 50)
        self.play_button = QPushButton('▶', self)
        self.play_button.setGeometry(1150, 42, 35, 35)
        interval = [
            QRadioButton("Day"),
            QRadioButton("Week"),
            QRadioButton("Month")
        ]
        self.panel = CollapsiblePanel("Interval", interval, self)
        self.panel.setGeometry(30, 110, 450, 300)
        self.panel.show()
        self.arrow_pad = ArrowPad(self)
        self.arrow_pad.setGeometry(1070, 600, 150, 150)  # Set the position and size of the arrow pad
        self.arrow_pad.show()

    def show_calendar(self):
        calendar_widget = QCalendarWidget(self)
        calendar_widget.setWindowFlags(calendar_widget.windowFlags() | Qt.Popup)
        calendar_button = self.sender()
        button_pos = calendar_button.mapToGlobal(calendar_button.rect().bottomLeft())
        calendar_widget.move(button_pos)
        calendar_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 1270, 800)
    window.setContentsMargins(0, 0, 0, 0)
    window.show()
    window.map_widget.set_map()
    sys.exit(app.exec_())
