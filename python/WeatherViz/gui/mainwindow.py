import renderer
from PySide2.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QWidget, QDateEdit, QCalendarWidget, QGridLayout, QSlider, QRadioButton
from PySide2.QtGui import QPalette, QColor, QPixmap, QPainter, QIcon, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QDate, Slot, QPoint
from PySide2 import QtCore
import PySide2
import folium
from folium import plugins, features
import sys
import io
from PIL import Image

from python.WeatherViz.gui.ArrowPad import ArrowPad
from python.WeatherViz.gui.CollapsiblePanel import CollapsiblePanel
from python.WeatherViz.gui.Map import MapWidget
from python.WeatherViz.gui.TransparentRectangle import TransparentRectangle


# NOT NEEDED, JUST FOR INITIAL TESTING
class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WeatherViz")
        # self.setStyleSheet("background-color: gainsboro;")  # Change as needed

        self.map_widget = MapWidget([27.75, -83.25], 7)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.map_widget.web_map)
        self.setLayout(self.layout)
        self.rect_item = TransparentRectangle(self)
        self.rect_item.setGeometry(30*2, 30*2, 1200*2, 60*2)
        self.start_date = QPushButton(QIcon("assets/Calendar.png"), '  Start Date', self)
        self.start_date.setGeometry(60*2, 42*2, 190*2, 35*2)
        self.start_date.clicked.connect(self.show_calendar)
        self.end_date = QPushButton(QIcon("assets/Calendar.png"), '  End Date', self)
        self.end_date.setGeometry(270*2, 42*2, 190*2, 35*2)
        self.end_date.clicked.connect(self.show_calendar)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(500*2, 35*2, 600*2, 50*2)
        self.play_button = QPushButton('▶', self)
        self.play_button.setGeometry(1150*2, 42*2, 35*2, 35*2)
        interval = [
            QRadioButton("Day"),
            QRadioButton("Week"),
            QRadioButton("Month"),
        ]
        self.panel = CollapsiblePanel("Interval", interval, self)
        self.panel.setGeometry(30*2, 110*2, 450*2, 300*2)
        self.panel.show()
        self.arrow_pad = ArrowPad(self)
        self.arrow_pad.setGeometry(1070*2, 600*2, 150*2, 150*2)  # Set the position and size of the arrow pad
        self.arrow_pad.up_button.clicked.connect(self.map_widget.move_up)
        self.arrow_pad.down_button.clicked.connect(self.map_widget.move_down)
        self.arrow_pad.left_button.clicked.connect(self.map_widget.move_left)
        self.arrow_pad.right_button.clicked.connect(self.map_widget.move_right)
        self.arrow_pad.show()

    def show_calendar(self):
        calendar_widget = QCalendarWidget(self)
        calendar_widget.setWindowFlags(calendar_widget.windowFlags() | Qt.Popup)
        calendar_button = self.sender()
        button_pos = calendar_button.mapToGlobal(calendar_button.rect().bottomLeft())
        calendar_widget.move(button_pos)
        calendar_widget.show()

    def updateEndDate(self, start_date, end_date):
        end_date.setMinimumDate(start_date)

    # def keyPressEvent(self, event):
    #     if event.key() == 87:  # W
    #         self.location[0] += 1 / (2 ** (self.zoom - 8))
    #     elif event.key() == 83:  # S
    #         self.location[0] -= 1 / (2 ** (self.zoom - 8))
    #     elif event.key() == 65:  # A
    #         self.location[1] -= 1 / (2 ** (self.zoom - 8))
    #     elif event.key() == 68:  # D
    #         self.location[1] += 1 / (2 ** (self.zoom - 8))
    #     elif self.zoom > 0 and event.key() == 69:  # E
    #         self.zoom -= 1
    #     elif self.zoom < 18 and event.key() == 81:  # Q
    #         self.zoom += 1
    #     else:
    #         return
    #
    #     self.refresh()

    
    def change_opacity(self, image_path, opacity_level):
        img = Image.open(image_path).convert("RGBA")

        for x in range(img.width):
            for y in range(img.height):
                r, g, b, a = img.getpixel((x, y))
                img.putpixel((x, y), (r, g, b, int(a * opacity_level)))

        img.save(image_path)
    
    def color_overlay(self, image_path, color, opacity_level):
        img = Image.open(image_path).convert("RGBA")
        overlay = Image.new('RGBA', img.size, color)
        blended = Image.blend(img, overlay, opacity_level)  
        blended.save(image_path, 'PNG')

    def get_data(self):
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        # this code gets the data for the center of the map. TODO (for y'all): wrap
        # renderer.geocoords and get the data for all the points in a lattice based on a
        # user-specified resolution--and other user-specified values, such as:
        # renderer.get_data(lat, long, start date, end date, daily?, variable, temperature unit,
        # windspeed unit, precipitation unit, timezone)
        response = renderer.get_data(self.location[0], self.location[1], start_date, end_date,
                False, "temperature_2m", "fahrenheit", "mph", "inch", "EST")
        print(response)

