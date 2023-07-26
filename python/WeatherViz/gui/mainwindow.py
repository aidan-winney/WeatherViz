import threading
import time
from PIL.ImageQt import ImageQt
from WeatherViz import renderer
from PySide2.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QWidget, QDateEdit, QCalendarWidget, QGridLayout, QSlider, QRadioButton
from PySide2.QtGui import QPalette, QColor, QPixmap, QPainter, QIcon, Qt, QFont
from PySide2.QtCore import QDate, Slot, QPoint, QThread, QMetaObject, QRect, QTimer
from PySide2 import QtCore
from ast import literal_eval
import sys
import io
import random
from PIL import Image
from threading import Thread
import requests
import concurrent.futures
import sqlite3

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.ArrowPad import ArrowPad
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
from WeatherViz.gui.Help import Help

from WeatherViz.gui.MapLegend import MapLegend

import WeatherViz.assets_rc

class DotWorker(QThread):
    def run(self):
        time.sleep(5)

class TimerThread(threading.Thread):
    def __init__(self, interval, function, *args, **kwargs):
        super().__init__()
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.end_time = time.time() + self.interval
        self.stop_signal = threading.Event()

    def run(self):
        while not self.stop_signal.is_set() and time.time() < self.end_time:
            time.sleep(0.1)  # Adjust this sleep duration to control the timer accuracy

        if not self.stop_signal.is_set():
            self.function(*self.args, **self.kwargs)

    def cancel(self):
        self.stop_signal.set()

    def time_remaining(self):
        return max(0, self.end_time - time.time())

class MainWindow(QWidget):
    progress_updated = QtCore.Signal()
    def __init__(self):
        super().__init__()

        self.is_querying = False
        self.is_rendering = False
        self.last_query_time = time.time()
        self.query_times = []
        self.query_count = 0
        self.timers = []
        self.query_dict = {}

        self.setWindowTitle("WeatherViz")
        self.setStyleSheet("background-color: rgba(32, 32, 32, 255); border-radius: 5px;")  # Change as needed
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QHBoxLayout(self)

        self.image = None
        self.apicalled = False
        self.query_daily = True
        self.query_start_date = QDate.currentDate()
        self.query_end_date = QDate.currentDate()
        self.map_widget = MapWidget([27.75, -83.25], 7)
        self.progress_updated.connect(self.update_progress, QtCore.Qt.QueuedConnection)
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.end_date = QDateEdit(calendarPopup=True)
        self.slider = DateRangeSlider(self.start_date, self.end_date, self)
        self.slider.playback_speed.get_button(0).clicked.connect(lambda: self.changePlaybackSpeed("1x"))
        self.slider.playback_speed.get_button(1).clicked.connect(lambda: self.changePlaybackSpeed("2x"))
        self.slider.playback_speed.get_button(2).clicked.connect(lambda: self.changePlaybackSpeed("4x"))
        self.slider.playback_speed.get_button(3).clicked.connect(lambda: self.changePlaybackSpeed("8x"))
        self.slider.get_slider().valueChanged.connect(lambda: self.update_overlay(True))
        self.date_selector = DateRangeChooser(self.start_date, self.end_date, self.slider, self)
        # self.date_selector.setStyleSheet("background-color: rgba(90, 90, 90, 255);  border-radius: 3px;")
        self.hourly = QRadioButton("Hourly")
        # self.hourly.setStyleSheet("background-color: rgba(90, 90, 90, 255);  border-radius: 3px;")
        self.daily = QRadioButton("Daily")
        # self.daily.setStyleSheet("background-color: rgba(90, 90, 90, 255);  border-radius: 3px;")
        self.daily.setChecked(True)
        self.twobytwo = QRadioButton("2x2")
        self.fourbyfour = QRadioButton("4x4")
        self.fourbyfour.setChecked(True)
        self.sixteenbysixteen = QRadioButton("16x16")
        self.rain = QRadioButton("Rain")
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
                   Panel("Timeline Interval", "Choose whether you get a datapoint for each day, or a datapoint for each hour"
                         , [self.hourly, self.daily]),
                   Panel("Heatmap Resolution",
                         "Higher resolutions will sample more locations so it will take longer but be more accurate"
                         , [self.twobytwo, self.fourbyfour, self.sixteenbysixteen]),
                   Panel("Weather Type", "Temperature data is for 2 meters above ground\n"
                                         "Wind speed is 10 meters above ground\n"
                         "Daily:\n∙ Average temperature, total amount of rain, maximum wind speed for the day"
                                         , [self.temperature, self.rain, self.wind])], self),
                   self.submit_button, self.progress]
        # content = [ScrollableContent([QLabel("Date Range")])]
        self.queryPane = QueryPane(content, self)
        self.queryPane.switch_tab.connect(self.load_data)
        self.queryPane.delete_tab.connect(self.delete_query)
        self.layout.addWidget(self.queryPane, alignment=Qt.AlignTop)
        self.layout.addWidget(self.map_widget)

        self.dots = 0
        self.dottimer = QTimer()
        self.dottimer.timeout.connect(self.update_button_text)
        self.worker = DotWorker(self)
        self.worker.started.connect(self.startAnimating)
        self.worker.finished.connect(self.stopAnimating)
        self.submit_button.clicked.connect(self.worker.start)
        self.dottimer.setInterval(500)

        # Instruction pop-up goes here - for Aidan
        #self.trigger_instruction_panel()

        self.setLayout(self.layout)

        self.play_button = PlayButton(self.slider.get_slider(), self)
        self.start_date.dateChanged.connect(self.play_button.checkDisabled)
        self.end_date.dateChanged.connect(self.play_button.checkDisabled)
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

        self.ren = Renderer()
        colors = [self.ren.color_at(position) for position in (1.00, 0.85, 0.55, 0.00)]
        labels = ["100%", "85%", "55%", "0%"]
        title = "Legend"

        self.legend_widget = MapLegend(colors, labels, title, self)
        self.legend_widget.setGeometry(self.queryPane.rect().width() + 50 * UIRescale.Scale,
                              self.rect().height() - 400 * UIRescale.Scale,
                              400 * UIRescale.Scale,
                              150 * UIRescale.Scale)

        self.help = Help(self.map_widget, self)
        self.help.setGeometry(self.queryPane.rect().width() + 50 * UIRescale.Scale,
                              self.map_widget.rect().height() - self.help.rect().height() - 50 * UIRescale.Scale,
                              self.map_widget.rect().width() - 70 * UIRescale.Scale,
                              400 * UIRescale.Scale)

        self.initial_load()

        self.image_label = QLabel(self.map_widget)

    def changePlaybackSpeed(self, state):
        if state == "1x":
            self.play_button.speed = 1000
        elif state == "2x":
            self.play_button.speed = 500
        elif state == "4x":
            self.play_button.speed = 250
        else:
            self.play_button.speed = 125

        if self.play_button.is_checked:
            self.play_button.timer.stop()
            self.play_button.timer.start(self.play_button.speed)

    def closeEvent(self, event):
        if self.worker.isRunning():
            self.worker.quit()
            self.worker.wait() 
        for timer in self.timers:
            timer.cancel()
        event.accept()

    #Navigation Functions
    def resizeEvent(self, event):
        self.toolbar.setGeometry(self.queryPane.rect().width() + 50 * UIRescale.Scale, 30 * UIRescale.Scale, self.map_widget.rect().width() - 70 * UIRescale.Scale, 100 * UIRescale.Scale)
        self.arrow_pad.setGeometry(self.rect().width() - 200 * UIRescale.Scale, self.rect().height() - 300 * UIRescale.Scale, 150 * UIRescale.Scale, 230 * UIRescale.Scale)
        screen_geometry = QApplication.desktop().availableGeometry(self)
        self.help.setGeometry(self.queryPane.rect().width() + 50 * UIRescale.Scale,
                              self.map_widget.rect().height() - self.help.rect().height() - 50 * UIRescale.Scale, self.map_widget.rect().width() - 70 * UIRescale.Scale,
                              400 * UIRescale.Scale)
        self.legend_widget.setGeometry(self.rect().width() - 200 * UIRescale.Scale,
                                        self.toolbar.rect().height() + 75 * UIRescale.Scale,
                                       150 * UIRescale.Scale,
                                       400 * UIRescale.Scale)
        super().resizeEvent(event)

    def move_up(self):
        self.map_widget.location[0] += 1 / (2 ** (self.map_widget.zoom - 8))
        self.update_overlay(False)

    def move_down(self):
        self.map_widget.location[0] -= 1 / (2 ** (self.map_widget.zoom - 8))
        self.update_overlay(False)

    def move_left(self):
        self.map_widget.location[1] -= 1 / (2 ** (self.map_widget.zoom - 8))
        self.update_overlay(False)

    def move_right(self):
        self.map_widget.location[1] += 1 / (2 ** (self.map_widget.zoom - 8))
        self.update_overlay(False)

    def zoom_in(self):
        self.map_widget.zoom = min(self.map_widget.zoom + 1, 18)
        self.update_overlay(False)

    def zoom_out(self):
        self.map_widget.zoom = max(self.map_widget.zoom - 1, 0)
        self.update_overlay(False)

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

    @QtCore.Slot()
    def update_overlay(self, render_pixmap=False):
        if self.apicalled:
            byte_array = self.ren.render(self.slider.get_slider().value(), self.map_widget.location[0], self.map_widget.location[1],
                                         self.map_widget.zoom, self.map_widget.web_map.width(),
                                         self.map_widget.web_map.height())
            self.image = Image.frombytes("RGBA", (self.map_widget.web_map.width(), self.map_widget.web_map.height()), byte_array)
            if self.temperature.isChecked():
                self.legend_widget.title = "Temperature (F)"
            elif self.wind.isChecked():
                self.legend_widget.title = "Wind (mph)"
            elif self.rain.isChecked():
                self.legend_widget.title = "Rain (inch)"
            labels = [self.ren.value_at(position) for position in (1.00, 0.85, 0.55, 0.00)]
            self.legend_widget.labels = labels
            if render_pixmap or self.play_button.is_checked:
                if self.image_label.pixmap is not None and (self.map_widget.marker is not None or render_pixmap is False):
                    self.map_widget.refresh()

                self.image_label.setPixmap(QPixmap.fromImage(ImageQt(self.image)))
                self.image_label.setGeometry(0, 0, self.map_widget.web_map.width(), self.map_widget.web_map.height())
                self.image_label.show()

            else:
                self.image_label.setPixmap(None)
                self.image_label.hide()
                self.map_widget.refresh(self.image)
        else:
            self.map_widget.refresh()

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
        if not self.is_querying and (self.sixteenbysixteen.isChecked() == False or len(self.query_times) < 2 or time.time() - self.last_query_time >= 60):
            self.is_querying = True
            self.submit_button.setChecked(True)
            self.submit_button.setText("Querying...")
            if self.sixteenbysixteen.isChecked():
                self.query_times.append(time.time())
                self.last_query_time = time.time()
                self.timers.append(TimerThread(60, self.reset_query_count))
                self.timers[len(self.timers)-1].start()
            self.submit_button.setEnabled(False)
            threading.Thread(target=self.get_data).start()
        elif len(self.query_times) == 2 and len(self.timers) is not 0:
            if self.dottimer.isActive():
                    QMetaObject.invokeMethod(self.dottimer, "stop", Qt.QueuedConnection)
            self.submit_button.setText(f"Try again in {round(self.timers[0].time_remaining())} seconds")
    
    def reset_query_count(self):
        self.query_times.pop(0)
        self.timers.pop(0)
        self.submit_button.setText("Query")

    def update_progress(self):
        self.progress.increment_progress()

    @QtCore.Slot()
    def update_slider_range(self):
        self.play_button.togglePlay(False)
        self.slider.update_range(self.query_start_date, self.query_end_date, self.query_daily)
        self.play_button.checkDisabled()

    def get_data(self):
        try:
            #Resolution
            if self.twobytwo.isChecked():
                RESOLUTION = 2
            elif self.fourbyfour.isChecked():
                RESOLUTION = 4
            elif self.sixteenbysixteen.isChecked():
                RESOLUTION = 16
            else:
                RESOLUTION = 2

            #Time interval
            if self.is_daily():
                DAILY = True
            else:
                DAILY = False
            self.query_daily = DAILY

            if self.temperature.isChecked():
                self.legend_widget.title = "Temperature (F)"
                if DAILY:
                    VARIABLE = "temperature_2m_mean"
                else:
                    VARIABLE = "temperature_2m"
            elif self.wind.isChecked(): #TODO: Edit this for actual wind speed data
                self.legend_widget.title = "Wind (mph)"
                if DAILY:
                    VARIABLE = "windspeed_10m_max"
                else:
                    VARIABLE = "windspeed_10m"
            elif self.rain.isChecked():
                self.legend_widget.title = "Rain (inch)"
                if DAILY:
                    VARIABLE = "rain_sum"
                else:
                    VARIABLE = "rain"

            TEMPERATURE_UNIT = "fahrenheit"
            WINDSPEED_UNIT = "mph"
            PRECIPITATION_UNIT = "inch"
            TIMEZONE = "EST"
            self.progress.set_total(RESOLUTION*RESOLUTION)
            self.progress.set_progress(0, RESOLUTION*RESOLUTION)

            self.query_start_date = self.date_selector.start_date.date()
            self.query_end_date = self.date_selector.end_date.date()
            start_date = self.query_start_date.toString("yyyy-MM-dd")
            end_date = self.query_end_date.toString("yyyy-MM-dd")

            center_lat = self.map_widget.location[0]
            center_lon = self.map_widget.location[1]
            zoom = self.map_widget.zoom
            raw_geocoords = renderer.geocoords(self.map_widget.web_map.width(), self.map_widget.web_map.height(), RESOLUTION,
                                   center_lat, center_lon, zoom)
            geocoords = [renderer.saw(lat, lon) for (lat, lon) in raw_geocoords]

            session = requests.Session()

            def api_call(lat, lon):
                url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&temperature_unit={TEMPERATURE_UNIT}&windspeed_unit={WINDSPEED_UNIT}&precipitation_unit={PRECIPITATION_UNIT}&timezone={TIMEZONE}&models=best_match&cell_selection=nearest"

                if DAILY:
                    url += f"&daily={VARIABLE}"
                else:
                    url += f"&hourly={VARIABLE}"

                self.progress_updated.emit()
                res = session.get(url)

                if res.status_code == requests.codes.ok:
                    return res.json()
                else:
                    raise RuntimeError(f"The request failed w/ code {res.status_code}, text {res.text}")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(lambda coords: api_call(*coords), geocoords)

            self.submit_button.setText("Rendering...")
            self.is_rendering = True

            responses = {}
            for result, (lat, lon) in zip(results, raw_geocoords):
                key = (str(lat), str(lon))
                responses[key] = result["daily" if DAILY else "hourly"][VARIABLE]
                #print(responses[key])

            self.ren.set_data(responses)
            self.apicalled = True
            
            # Database caching
            database_connection = sqlite3.connect("queries.db")
            cur = database_connection.cursor()
            res = cur.execute("SELECT name FROM sqlite_master")
            if len(res.fetchall()) == 0:
                cur.execute(
                    "CREATE TABLE saved(id INTEGER, start_date TEXT, end_date TEXT, interval TEXT, resolution INTEGER, weather_variable TEXT, data TEXT, center_lat REAL, center_lon REAL, zoom INTEGER, PRIMARY KEY (id))")
                    #Interval saves as text '0' or '1'
            tab_text = self.queryPane.tab_widget.tabText(self.queryPane.tab_widget.currentIndex())
            if tab_text in self.query_dict:
                id = self.query_dict[tab_text]
            else:
                id = random.randint(0, 10000)
                while id in self.query_dict.values():
                    id = random.randint(0, 10000)
                self.query_dict[self.queryPane.tab_widget.tabText(self.queryPane.tab_widget.currentIndex())] = id
            data = [(id, start_date, end_date, DAILY, RESOLUTION, VARIABLE, str(responses), center_lat, center_lon, zoom),]
            if len(cur.execute("SELECT * FROM saved WHERE id = (?)", (id,)).fetchall()) != 0:
                cur.execute("DELETE FROM saved WHERE id = (?)", (id,))
            cur.executemany("INSERT INTO saved VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            database_connection.commit()
            database_connection.close()

            QMetaObject.invokeMethod(self, "update_overlay", QtCore.Qt.QueuedConnection)
            QMetaObject.invokeMethod(self, "update_slider_range", QtCore.Qt.QueuedConnection)
            QMetaObject.invokeMethod(self.dottimer, "stop", Qt.QueuedConnection)
            self.submit_button.setText("Query")
            self.submit_button.setEnabled(True)
            self.is_querying = False
            self.is_rendering = False
        except Exception as e:
            try:
                if self.dottimer.isActive():
                    QMetaObject.invokeMethod(self.dottimer, "stop", Qt.QueuedConnection)
            except Exception as e2:
                print("Failed to stop timer. Error message: ", str(e2))

            self.is_querying = False
            self.is_rendering = False
            self.submit_button.setEnabled(True)
            exception_message = str(e)
            words = exception_message.split()
            first_word = words[7] if words else ""

        finally:
            if 'executor' in locals():
                executor.shutdown()
            if 'session' in locals():
                session.close()

            if 'first_word' in locals() and (first_word == "{\"reason\":\"Daily" or first_word == "{\"error\":true,\"reason\":\"Daily"):
                self.update_button_limit_except()
            elif 'first_word' in locals() and (first_word == "{\"reason\":\"Minutely" or first_word == "\"error\":true,{\"reason\":\"Minutely"):
                self.update_button_limit_except()
            elif 'first_word' in locals() and (first_word == "{\"reason\":\"Hourly" or first_word == "\"error\":true,{\"reason\":\"Hourly"):
                self.update_button_limit_except()
            elif 'first_word' in locals():
                self.update_button_unknown_except()

    def update_button_text(self):
        self.dots = (self.dots + 1) % 4
        if self.is_querying:
            self.submit_button.setText("Querying" + "." * self.dots)
        elif self.is_rendering:
            self.submit_button.setText("Rendering" + "." * self.dots)

    def update_button_limit_except(self):
        self.submit_button.setText('Query failed (API limit reached)')
    
    def update_button_unknown_except(self):
        self.submit_button.setText('Query failed (Unknown Error)')

    def startAnimating(self):
        QMetaObject.invokeMethod(self.dottimer, "start", Qt.QueuedConnection)

    def stopAnimating(self):
        QMetaObject.invokeMethod(self.dottimer, "stop", Qt.QueuedConnection)


    def initial_load(self):
        database_connection = sqlite3.connect("queries.db")
        cur = database_connection.cursor()
        res = cur.execute("SELECT name FROM sqlite_master")
        if len(res.fetchall()) != 0:
            res = cur.execute("SELECT id FROM saved")
            id_list = res.fetchall()
            if len(id_list) > 0:
                for id in id_list:
                    self.query_dict[self.queryPane.tab_widget.tabText(self.queryPane.tab_widget.currentIndex())] = id[0]
                    self.queryPane.addTab()
                self.load_data()
        database_connection.close()

    def load_data(self):
        database_connection = sqlite3.connect("queries.db")
        cur = database_connection.cursor()
        tab_text = self.queryPane.tab_widget.tabText(self.queryPane.tab_widget.currentIndex())
        if tab_text in self.query_dict:
            id = self.query_dict[tab_text]
            res = cur.execute("SELECT * FROM saved WHERE id= (?)", (id,))
            query_info = res.fetchone()

            #Set query variables to saved ones
            self.date_selector.start_date.setDate(QDate.fromString(query_info[1], "yyyy-MM-dd"))
            self.date_selector.end_date.setDate(QDate.fromString(query_info[2], "yyyy-MM-dd"))
            self.query_start_date = self.date_selector.start_date.date()
            self.query_end_date = self.date_selector.end_date.date()
            if literal_eval(query_info[3]):
                self.daily.setChecked(True)
                self.query_daily = True
            else:
                self.hourly.setChecked(True)
                self.query_daily = False

            if query_info[4] == 2:
                self.twobytwo.setChecked(True)
            elif query_info[4] == 4:
                self.fourbyfour.setChecked(True)
            elif query_info[4] == 16:
                self.sixteenbysixteen.setChecked(True)

            if query_info[5] == "temperature_2m_mean" or query_info[5] == "temperature_2m":
                self.temperature.setChecked(True)
            elif query_info[5] == "windspeed_10m_max" or query_info[5] == "windspeed_10m":
                self.wind.setChecked(True)
            elif query_info[5] == "rain_sum" or query_info[5] == "rain":
                self.wind.setChecked(True)

            if literal_eval(query_info[6]) != None:
                self.apicalled = True
                self.ren = Renderer()
                self.ren.set_data(literal_eval(query_info[6]))

            self.map_widget.location[0] = query_info[7]
            self.map_widget.location[1] = query_info[8]
            self.map_widget.zoom = query_info[9]

            self.update_slider_range()
            self.update_overlay()
        database_connection.close()

    def delete_query(self):
        database_connection = sqlite3.connect("queries.db")
        cur = database_connection.cursor()
        tab_text = self.queryPane.tab_widget.tabText(self.queryPane.tab_widget.currentIndex())
        if tab_text in self.query_dict:
            id = self.query_dict[tab_text]
            self.query_dict.pop(self.queryPane.tab_widget.tabText(self.queryPane.tab_widget.currentIndex()))
            cur.execute("DELETE FROM saved WHERE id = (?)", (id,))
        database_connection.commit()
        database_connection.close()
        self.ren = Renderer()
        self.ren.set_data({})
        self.update_slider_range()
        self.update_overlay()



