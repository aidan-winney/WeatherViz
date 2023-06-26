from PySide2.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QWidget, QDateEdit, QCalendarWidget, QGridLayout
from PySide2.QtGui import QPalette, QColor, QPixmap, QPainter
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QDate, Slot, QPoint
from PySide2 import QtCore
import PySide2
import folium
from folium import plugins, features
import sys
import io
from WeatherViz import renderer
from PIL import Image

# NOT NEEDED, JUST FOR INITIAL TESTING
class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.map = None
        self.web_map = None
        self.zoom = 7
        self.location = [27.75, -83.25]
        self.setWindowTitle("WeatherViz")
        self.setStyleSheet("background-color: gainsboro;")  # Change as needed

        self.createOptionsArea()
        self.createMap()

        main_widget = QWidget()
        main_widget.setWindowFlag(QtCore.Qt.WindowStaysOnBottomHint)

        #temp = QPixmap("gui\\Donpeng.jpg")
        #donpeng_pix = QPixmap(temp.size())
        #donpeng_pix.fill(QtCore.Qt.transparent)
        #painter = QPainter(donpeng_pix)
        #painter.setOpacity(0.2)
        #painter.drawPixmap(QtCore.QPoint(), temp)
        #painter.end()

        #img_widget = QWidget(parent=main_widget)
        #img_widget.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        #self.donpeng_img = QLabel(img_widget)
        #self.donpeng_img.setPixmap(donpeng_pix)
        #self.donpeng_img.setFixedSize(donpeng_pix.size())
        #point = self.geometry().bottomRight() - self.donpeng_img.geometry().bottomRight() - QPoint(100, 100)
        #self.donpeng_img.move(point)

        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.options_area, 0, 0, 1, 1)
        main_layout.addWidget(self.web_map, 0, 1, 1, 3)
        main_layout.setRowStretch(0, 3)

        #img_widget.show()
        #img_widget.raise_()

        main_widget.setLayout(main_layout)
        self.main_widget = main_widget
        self.setCentralWidget(main_widget)

    # Option selection area on left side
    def createOptionsArea(self):
        calendar_start = QCalendarWidget()
        calendar_start.setDateRange(QDate(1980, 1, 1), QDate.currentDate())
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumDate(QDate(1980, 1, 1))  # Change to correct minimum date
        self.start_date.setMaximumDate(QDate.currentDate())
        self.start_date.setCalendarWidget(calendar_start)

        calendar_end = QCalendarWidget()
        calendar_end.setDateRange(QDate(1980, 1, 1), QDate.currentDate())
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumDate(QDate.currentDate())  # Change to correct minimum date
        self.end_date.setMaximumDate(QDate.currentDate())
        self.end_date.setCalendarWidget(calendar_end)

        self.start_date.dateChanged.connect(lambda: self.updateEndDate(self.start_date.date(), self.end_date))

        date_selection = QGroupBox("Date")
        date_layout = QVBoxLayout()
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.end_date)
        date_selection.setLayout(date_layout)

        random_selection = QGroupBox("Random")
        # button1 = QPushButton("Zoom In")
        # button1.clicked.connect(self.zoom_in)
        # button1.setGeometry(0, 0, 100, 100)
        # button2 = QPushButton("Zoom Out")
        # button2.clicked.connect(self.zoom_out)
        button = QPushButton("Get Data")
        button.clicked.connect(self.get_data)
        layout = QVBoxLayout()
        layout.addWidget(button)
        # layout.addWidget(button1)
        # layout.addWidget(button2)
        random_selection.setLayout(layout)

        options_layout = QVBoxLayout()
        options_layout.addWidget(date_selection)
        options_layout.addWidget(random_selection)
        self.options_area = QGroupBox("Options")
        self.options_area.setLayout(options_layout)

    def updateEndDate(self, start_date, end_date):
        end_date.setMinimumDate(start_date)

    def keyPressEvent(self, event):
        if event.key() == 87:  # W
            self.location[0] += 1 / (2 ** (self.zoom - 8))
        elif event.key() == 83:  # S
            self.location[0] -= 1 / (2 ** (self.zoom - 8))
        elif event.key() == 65:  # A
            self.location[1] -= 1 / (2 ** (self.zoom - 8))
        elif event.key() == 68:  # D
            self.location[1] += 1 / (2 ** (self.zoom - 8))
        elif self.zoom > 0 and event.key() == 69:  # E
            self.zoom -= 1
        elif self.zoom < 18 and event.key() == 81:  # Q
            self.zoom += 1
        else:
            return

        self.refresh()

    
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


    def refresh(self):
        self.map = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                              zoom_control=False, keyboard=False, dragging=False, doubleClickZoom=False,
                              boxZoom=False, scrollWheelZoom=False)
        roundnum = "function(num) {return L.Util.formatNum(num, 5);};"
        mouse = plugins.MousePosition(position='topright', separator=' | ', prefix="Position:", lat_formatter=roundnum,
                                      lng_formatter=roundnum).add_to(self.map)

        icon = features.CustomIcon('gui\\Donpeng.png', icon_size=(50, 50))
        marker = folium.Marker(location=[29.651634, -82.324829], icon=icon)
        marker.add_to(self.map)

        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.web_map.setHtml(data.getvalue().decode())
        self.web_map.update()


    def createMap(self):
        # Right part of main page (MAP PLACEHOLDER)
        m = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                       zoom_control=False, keyboard=False, dragging=False, doubleClickZoom=False,
                       boxZoom=False, scrollWheelZoom=False)
        roundnum = "function(num) {return L.Util.formatNum(num, 6);};"
        mouse = plugins.MousePosition(position='topright', separator=' | ', prefix="Position:", lat_formatter=roundnum,
                                      lng_formatter=roundnum).add_to(m)

        icon = features.CustomIcon('gui\\Donpeng.png', icon_size=(50, 50))
        marker = folium.Marker(location=[29.651634, -82.324829], icon=icon)
        marker.add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)
        web_map = QWebEngineView()
        web_map.setHtml(data.getvalue().decode())
        self.web_map = web_map

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

