import threading
from PIL.ImageQt import ImageQt
from WeatherViz import renderer
from PySide2.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QWidget, QDateEdit, QCalendarWidget, QGridLayout, QSlider, QRadioButton
from PySide2.QtGui import QPalette, QColor, QPixmap, QPainter, QIcon, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QDate, Slot, QPoint, QThread, QMetaObject
from PySide2 import QtCore
import PySide2
import folium
from folium import plugins, features
import sys
import io
from PIL import Image
from threading import Thread
import requests
import concurrent.futures


from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.ArrowPad import ArrowPad
from WeatherViz.gui.CollapsiblePanel import CollapsiblePanel
from WeatherViz.gui.Map import MapWidget
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

import json
from WeatherViz.renderer import Renderer

from WeatherViz.gui.DateRangeSlider import DateRangeSlider

from WeatherViz.gui.PlayButton import PlayButton

from WeatherViz.gui.ProgressBar import ProgressBar
from WeatherViz.Worker import Worker

from WeatherViz.gui.NonCollapsiblePanel import NonCollapsiblePanel

from WeatherViz.gui.DateRangeChooser import DateRangeChooser
from WeatherViz.gui.QueryPane import QueryPane

from WeatherViz.gui.Panel import Panel

from WeatherViz.gui.Toolbar import Toolbar

from WeatherViz.gui.ScrollableContent import ScrollableContent


# NOT NEEDED, JUST FOR INITIAL TESTING
class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QWidget):
    progress_updated = QtCore.Signal() 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WeatherViz")
        self.setStyleSheet("background-color: rgba(32, 32, 32, 255); border-radius: 5px;")  # Change as needed
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignBottom)

        self.image = None
        self.apicalled = False
        self.map_widget = MapWidget([27.75, -83.25], 7)
        self.progress_updated.connect(self.update_progress, QtCore.Qt.QueuedConnection)

        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.end_date = QDateEdit(calendarPopup=True)
        self.slider = DateRangeSlider(self.start_date, self.end_date, self)
        self.slider.get_slider().valueChanged.connect(self.update_overlay)
        self.date_selector = DateRangeChooser(self.start_date, self.end_date, self.slider, self)
        self.date_selector.setGeometry(45 * UIRescale.Scale, 15 * UIRescale.Scale, 425 * UIRescale.Scale, 90 * UIRescale.Scale)
        hourly = QRadioButton("Hourly")
        daily = QRadioButton("Daily")
        daily.setChecked(True)
        self.twobytwo = QRadioButton("2x2")
        self.fourbyfour = QRadioButton("4x4")
        self.fourbyfour.setChecked(True)
        self.sixteenbysixteen = QRadioButton("16x16")
        self.precipitation = QRadioButton("Precipitation")
        self.temperature = QRadioButton("Temperature")
        self.temperature.setChecked(True)
        self.wind = QRadioButton("Wind")
        self.progress = ProgressBar(self)
        self.progress.set_progress(4, 4)
        self.submit_button = QPushButton('Query', self)
        self.submit_button.setFixedHeight(50 * UIRescale.Scale)
        self.submit_button.setStyleSheet("background-color: rgba(90, 90, 90, 255);  border-radius: 3px;")

        self.submit_button.clicked.connect(self.query)
        content = [ScrollableContent([QLabel("Date Range"), self.date_selector,
                   Panel("Timeline Interval", "Tooltip", [hourly, daily]),
                   Panel("Heatmap Resolution", "Tooltip", [self.twobytwo, self.fourbyfour, self.sixteenbysixteen]),
                   Panel("Weather Type", "Tooltip", [self.temperature, self.precipitation, self.wind])], self),
                   self.submit_button, self.progress]
        # content = [ScrollableContent([QLabel("Date Range")])]
        self.queryPane = QueryPane(content, self)
        self.layout.addWidget(self.queryPane, alignment=Qt.AlignTop)
        self.layout.addWidget(self.map_widget)
        self.setLayout(self.layout)

        self.play_button = PlayButton(self.slider.get_slider(), self)
        self.toolbar = Toolbar([self.slider, self.play_button], self)
        self.toolbar.setGeometry(450 * UIRescale.Scale, 30 * UIRescale.Scale, self.map_widget.rect().width() - 70 * UIRescale.Scale, 100 * UIRescale.Scale)

        self.arrow_pad = ArrowPad(self)
        self.arrow_pad.setGeometry(1300 * UIRescale.Scale, 550 * UIRescale.Scale, 150 * UIRescale.Scale, 230 * UIRescale.Scale)  # Set the position and size of the arrow pad
        self.arrow_pad.up_button.clicked.connect(self.move_up)
        self.arrow_pad.down_button.clicked.connect(self.move_down)
        self.arrow_pad.left_button.clicked.connect(self.move_left)
        self.arrow_pad.right_button.clicked.connect(self.move_right)
        self.arrow_pad.zoom_in.clicked.connect(self.zoom_in)
        self.arrow_pad.zoom_out.clicked.connect(self.zoom_out)
        self.arrow_pad.show()

    def resizeEvent(self, event):
        self.toolbar.setGeometry(self.queryPane.rect().width() + 50 * UIRescale.Scale, 30 * UIRescale.Scale, self.map_widget.rect().width() - 70 * UIRescale.Scale, 100 * UIRescale.Scale)
        self.arrow_pad.setGeometry(self.rect().width() - 200 * UIRescale.Scale, self.rect().height() - 300 * UIRescale.Scale, 150 * UIRescale.Scale, 230 * UIRescale.Scale)
        super().resizeEvent(event)

    def move_up(self):
        self.map_widget.location[0] += 1 / (2 ** (self.map_widget.zoom - 8))
        self.map_widget.refresh()
        self.update_overlay()

    def move_down(self):
        self.map_widget.location[0] -= 1 / (2 ** (self.map_widget.zoom - 8))
        self.map_widget.refresh()
        self.update_overlay()

    def move_left(self):
        self.map_widget.location[1] -= 1 / (2 ** (self.map_widget.zoom - 8))
        self.map_widget.refresh()
        self.update_overlay()

    def move_right(self):
        self.map_widget.location[1] += 1 / (2 ** (self.map_widget.zoom - 8))
        self.map_widget.refresh()
        self.update_overlay()

    def zoom_in(self):
        self.map_widget.zoom += 1
        self.map_widget.refresh()
        self.update_overlay()

    def zoom_out(self):
        self.map_widget.zoom -= 1
        self.map_widget.refresh()
        self.update_overlay()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:  # W
            self.move_up()
        elif event.key() == Qt.Key_S:  # S
            self.move_down()
        elif event.key() == Qt.Key_A:  # A
            self.move_left()
        elif event.key() == Qt.Key_D:  # D
            self.move_right()
        elif self.map_widget.zoom > 0 and event.key() == Qt.Key_E:  # E
            self.zoom_out()
        elif self.map_widget.zoom < 18 and event.key() == Qt.Key_Q:  # Q
            self.zoom_in()

    def update_overlay(self):
        if self.apicalled:
            byte_array = self.ren.render(self.slider.get_slider().value(), self.map_widget.location[0], self.map_widget.location[1],
                                         self.map_widget.zoom, self.map_widget.web_map.width(),
                                         self.map_widget.web_map.height())
            image = Image.frombytes("RGBA", (self.map_widget.web_map.width(), self.map_widget.web_map.height()), byte_array)
            self.map_widget.refresh(image)
    
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

    def is_hourly(self):
        return self.hourly.isChecked()
    
    def is_daily(self):
        return self.daily.isChecked()

    def query(self):
        self.submit_button.setChecked(True)
        # self.submit_button.setText("◷")
        self.submit_button.setText("Query...")
        threading.Thread(target=self.get_data).start()

    def update_progress(self):
        self.progress.increment_progress()

    def get_data(self):
        self.is_hourly()
        if self.twobytwo.isChecked():
            RESOLUTION = 2
        elif self.fourbyfour.isChecked():
            RESOLUTION = 4
        elif self.sixteenbysixteen.isChecked():
            RESOLUTION = 16
        else:
            RESOLUTION = 2
        DAILY = False
        VARIABLE = "temperature_2m"
        TEMPERATURE_UNIT = "fahrenheit"
        WINDSPEED_UNIT = "mph"
        PRECIPITATION_UNIT = "inch"
        TIMEZONE = "EST"
        self.progress.set_total(RESOLUTION*RESOLUTION)
        self.progress.set_progress(0, RESOLUTION*RESOLUTION)

        start_date = self.date_selector.start_date.date().toString("yyyy-MM-dd")
        end_date = self.date_selector.end_date.date().toString("yyyy-MM-dd")
        geocoords = renderer.geocoords(self.map_widget.web_map.width(), self.map_widget.web_map.height(), RESOLUTION,
                                   self.map_widget.location[0], self.map_widget.location[1], self.map_widget.zoom)

        def api_call(lat, lon):
            url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&temperature_unit={TEMPERATURE_UNIT}&windspeed_unit={WINDSPEED_UNIT}&precipitation_unit={PRECIPITATION_UNIT}&timezone={TIMEZONE}&models=best_match&cell_selection=nearest"

            if DAILY:
                url += f"&daily={VARIABLE}"
            else:
                url += f"&hourly={VARIABLE}"

            self.progress_updated.emit()
            res = requests.get(url)

            if res.status_code == requests.codes.ok:
                return res.json()
            else:
                raise RuntimeError(f"The request failed w/ code {res.status_code}, text {res.text}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(lambda coords: api_call(*coords), geocoords)

        responses = {}
        for result, (lat, lon) in zip(results, geocoords):
            key = (str(lat), str(lon))
            responses[key] = result["daily" if DAILY else "hourly"][VARIABLE]
            print(responses[key])

        self.ren = Renderer()
        self.ren.set_data(responses)
        self.apicalled = True
        QMetaObject.invokeMethod(self, "update_overlay", QtCore.Qt.QueuedConnection)
        self.submit_button.setText("Query")


