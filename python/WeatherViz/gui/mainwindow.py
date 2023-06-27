from PIL.ImageQt import ImageQt
from WeatherViz import renderer
from PySide2.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QWidget, QDateEdit, QCalendarWidget, QGridLayout, QSlider, QRadioButton
from PySide2.QtGui import QPalette, QColor, QPixmap, QPainter, QIcon, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QDate, Slot, QPoint, QThread
from PySide2 import QtCore
import PySide2
import folium
from folium import plugins, features
import sys
import io
from PIL import Image
from threading import Thread

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
        self.image = None
        self.map_widget = MapWidget([27.75, -83.25], 7)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.map_widget.web_map)
        self.setLayout(self.layout)

        self.rect_item = TransparentRectangle(self)
        self.rect_item.setGeometry(30 * UIRescale.Scale, 30 * UIRescale.Scale, 1200 * UIRescale.Scale, 60 * UIRescale.Scale)

        self.date_selector = QWidget(self)
        self.date_select_layout = QHBoxLayout(self)

        calendar_start = QCalendarWidget(self)
        calendar_start.setDateRange(QDate(1980, 1, 1), QDate.currentDate().addDays(-8))
        # calendar_start.setGeometry(60, 42, 190, 35)
        self.start_date = QDateEdit(self, calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumDate(QDate(1980, 1, 1))  # Change to correct minimum date
        self.start_date.setMaximumDate(QDate.currentDate().addDays(-8))
        self.start_date.setCalendarWidget(calendar_start)

        calendar_end = QCalendarWidget(self)
        calendar_end.setDateRange(QDate(1980, 1, 1), QDate.currentDate().addDays(-8))
        # calendar_end.setGeometry(270, 42, 190, 35)
        self.end_date = QDateEdit(self, calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumDate(QDate.currentDate())  # Change to correct minimum date
        self.end_date.setMaximumDate(QDate.currentDate().addDays(-8))
        self.end_date.setCalendarWidget(calendar_end)

        self.date_select_layout.addWidget(self.start_date)
        self.date_select_layout.stretch(1)
        self.date_select_layout.addWidget(self.end_date)

        self.start_date.dateChanged.connect(lambda: self.updateEndDate(self.start_date.date(), self.end_date))
        self.end_date.dateChanged.connect(lambda: self.slider.update_range(self.start_date, self.end_date))

        self.date_selector.setLayout(self.date_select_layout)
        self.date_selector.setGeometry(45 * UIRescale.Scale, 15 * UIRescale.Scale, 425 * UIRescale.Scale, 90 * UIRescale.Scale)
        self.date_selector.show()

        self.submit_button = QPushButton('✓', self)
        self.submit_button.setGeometry(470 * UIRescale.Scale, 42 * UIRescale.Scale, 35 * UIRescale.Scale, 35 * UIRescale.Scale)
        self.submit_button.clicked.connect(self.query)

        self.slider = DateRangeSlider(self.start_date, self.end_date, self)
        self.slider.setGeometry(550 * UIRescale.Scale, 27 * UIRescale.Scale, 550 * UIRescale.Scale, 65 * UIRescale.Scale)
        self.slider.get_slider().valueChanged.connect(self.update_overlay)
        self.play_button = PlayButton(self.slider.get_slider(), self)
        self.play_button.setGeometry(1140 * UIRescale.Scale, 30 * UIRescale.Scale, 40 * UIRescale.Scale, 60 * UIRescale.Scale)
        # pane = QWidget(self)
        # pane_layout = QVBoxLayout(self)
        # self.hourly = QRadioButton("Hourly")
        # self.daily = QRadioButton("Daily")
        # # pane_layout.setSpacing(2)
        # self.interval_panel = CollapsiblePanel("Interval", [
        #     self.hourly,
        #     self.daily
        # ], self)
        # # self.interval_panel.setGeometry(30 * UIRescale.Scale, 110 * UIRescale.Scale, 400 * UIRescale.Scale, 300 * UIRescale.Scale)
        # self.interval_panel.show()
        #
        # self.twobytwo = QRadioButton("2x2")
        # self.fourbyfour = QRadioButton("4x4")
        # self.sixteenbysixteen = QRadioButton("16x16")
        #
        # self.resolution_panel = CollapsiblePanel("Heatmap Resolution",
        #                                          [self.twobytwo, self.fourbyfour, self.sixteenbysixteen], self)
        # # self.resolution_panel.setGeometry(30 * UIRescale.Scale, 270 * UIRescale.Scale, 400 * UIRescale.Scale, 300 * UIRescale.Scale)
        # self.resolution_panel.show()
        #
        # pane_layout.addWidget(self.interval_panel)
        # pane_layout.addWidget(self.resolution_panel)
        # pane_layout.setAlignment(Qt.AlignTop)
        # pane.setLayout(pane_layout)
        # pane.setGeometry(20 * UIRescale.Scale, 110 * UIRescale.Scale, 400 * UIRescale.Scale, 350 * UIRescale.Scale)

        pane = QWidget(self)
        pane_layout = QVBoxLayout(self)
        self.hourly = QRadioButton("Hourly")
        self.daily = QRadioButton("Daily")
        # pane_layout.setSpacing(2)
        self.interval_panel = NonCollapsiblePanel("Interval", [
            self.hourly,
            self.daily
        ], self)
        # self.interval_panel.setGeometry(30 * UIRescale.Scale, 110 * UIRescale.Scale, 400 * UIRescale.Scale, 300 * UIRescale.Scale)
        self.interval_panel.show()

        self.twobytwo = QRadioButton("2x2")
        self.fourbyfour = QRadioButton("4x4")
        self.sixteenbysixteen = QRadioButton("16x16")

        self.resolution_panel = NonCollapsiblePanel("Heatmap Resolution",
                                                 [self.twobytwo, self.fourbyfour, self.sixteenbysixteen], self)
        # self.resolution_panel.setGeometry(30 * UIRescale.Scale, 270 * UIRescale.Scale, 400 * UIRescale.Scale, 300 * UIRescale.Scale)
        self.resolution_panel.show()

        pane_layout.addWidget(self.interval_panel)
        pane_layout.addWidget(self.resolution_panel)
        pane_layout.setAlignment(Qt.AlignTop)
        pane.setLayout(pane_layout)
        pane.setGeometry(20 * UIRescale.Scale, 110 * UIRescale.Scale, 400 * UIRescale.Scale, 350 * UIRescale.Scale)

        self.arrow_pad = ArrowPad(self)
        self.arrow_pad.setGeometry(1070 * UIRescale.Scale, 550 * UIRescale.Scale, 150 * UIRescale.Scale, 150 * UIRescale.Scale)  # Set the position and size of the arrow pad
        self.arrow_pad.up_button.clicked.connect(self.map_widget.move_up)
        self.arrow_pad.down_button.clicked.connect(self.map_widget.move_down)
        self.arrow_pad.left_button.clicked.connect(self.map_widget.move_left)
        self.arrow_pad.right_button.clicked.connect(self.map_widget.move_right)
        self.arrow_pad.show()

        self.progress = ProgressBar(self)
        self.progress.set_progress(4,4)
        self.progress.setGeometry(875 * UIRescale.Scale, 750 * UIRescale.Scale, 350 * UIRescale.Scale, 50 * UIRescale.Scale)
        # self.progress.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:  # W
            self.map_widget.move_up()
        elif event.key() == Qt.Key_S:  # S
            self.map_widget.move_down()
        elif event.key() == Qt.Key_A:  # A
            self.map_widget.move_left()
        elif event.key() == Qt.Key_D:  # D
            self.map_widget.move_right()
        elif self.map_widget.zoom > 0 and event.key() == Qt.Key_E:  # E
            self.map_widget.zoom -= 1
        elif self.map_widget.zoom < 18 and event.key() == Qt.Key_Q:  # Q
            self.map_widget.zoom += 1
        else:
            return
        # self.ren.render()
        self.update_overlay()


    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.map_widget.last_pos = event.pos()
    # #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() == Qt.LeftButton:
    #         diff = event.pos() - self.map_widget.last_pos
    #         self.map_widget.pan_map(diff.x(), diff.y())
    #         self.map_widget.last_pos = event.pos()

    def show_calendar(self):
        calendar_widget = QCalendarWidget(self)
        calendar_widget.setWindowFlags(calendar_widget.windowFlags() | Qt.Popup)
        calendar_button = self.sender()
        button_pos = calendar_button.mapToGlobal(calendar_button.rect().bottomLeft())
        calendar_widget.move(button_pos)
        calendar_widget.show()

    def updateEndDate(self, start_date, end_date):
        self.slider.update_range(self.start_date, self.end_date)
        end_date.setMinimumDate(start_date)

    def update_overlay(self):
        byte_array = self.ren.render(self.slider.get_slider().value(), self.map_widget.location[0], self.map_widget.location[1],
                                     self.map_widget.zoom, self.map_widget.web_map.width(),
                                     self.map_widget.web_map.height())
        image = Image.frombytes("RGBA", (self.map_widget.web_map.width(), self.map_widget.web_map.height()), byte_array)
        self.map_widget.refresh(image)



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

    def is_hourly(self):
        return self.hourly.isChecked()
    
    def is_daily(self):
        return self.daily.isChecked()

    def query(self):
        self.submit_button.setChecked(True)
        self.submit_button.setText("◷")
        self.get_data()

    def get_data(self):
        # TODO: allow user to change these (i used all caps to mark this lol)
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

        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        geocoords = renderer.geocoords(self.map_widget.web_map.width(), self.map_widget.web_map.height(), RESOLUTION,
                self.map_widget.location[0], self.map_widget.location[1], self.map_widget.zoom)
        def api_call_thread():
            # self.progress.show()
            responses = {}
            call_num = 0
            for lat, long in geocoords:
                data = json.loads(renderer.get_data(lat, long, start_date, end_date, DAILY, VARIABLE,
                    TEMPERATURE_UNIT, WINDSPEED_UNIT, PRECIPITATION_UNIT, TIMEZONE))
                key = (str(data["latitude"]), str(data["longitude"]))
                responses[key] = data["daily" if DAILY else "hourly"][VARIABLE]
                call_num = call_num + 1
                self.progress.set_progress(call_num, RESOLUTION*RESOLUTION)
                # self.progress.progress.setValue(50)
                print(responses[key])
            self.ren = Renderer()
            self.ren.set_data(responses)

            # if(self.is_hourly()):
            #     x = ((self.start_date.date().daysTo(self.end_date.date()))+1)*24
            # else:
            #     x = (self.start_date.date().daysTo(self.end_date.date()))+1

                # self.pixmaps.append(QPixmap.fromImage(ImageQt(image)))
            self.update_overlay()
            self.submit_button.setText("✓")
            # self.progress.hide()

        api_call_thread()
        # thread = QThread(target=api_call_thread)
        # thread.
        # thread.start()


