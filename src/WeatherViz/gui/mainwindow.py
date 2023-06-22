from PySide2.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QWidget, QDateEdit, QCalendarWidget
from PySide2.QtGui import QPalette, QColor
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QDate
from PyQt5.Qt import Qt
import folium
from folium import plugins
import sys
import io


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

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.options_area, 1)
        main_layout.addWidget(self.web_map, 4)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        # main_widget.show()
        self.setCentralWidget(main_widget)
        self.main_widget = main_widget

    # Option selection area on left side
    def createOptionsArea(self):
        calendar_start = QCalendarWidget()
        calendar_start.setDateRange(QDate(1980, 1, 1), QDate.currentDate())
        start_date = QDateEdit(calendarPopup=True)
        start_date.setDate(QDate.currentDate())
        start_date.setMinimumDate(QDate(1980, 1, 1))  # Change to correct minimum date
        start_date.setMaximumDate(QDate.currentDate())
        start_date.setCalendarWidget(calendar_start)

        calendar_end = QCalendarWidget()
        calendar_end.setDateRange(QDate(1980, 1, 1), QDate.currentDate())
        end_date = QDateEdit(calendarPopup=True)
        end_date.setDate(QDate.currentDate())
        end_date.setMinimumDate(QDate(1980, 1, 1))  # Change to correct minimum date
        end_date.setMaximumDate(QDate.currentDate())
        end_date.setCalendarWidget(calendar_end)

        date_selection = QGroupBox("Date")
        date_layout = QVBoxLayout()
        date_layout.addWidget(start_date)
        date_layout.addWidget(end_date)
        date_selection.setLayout(date_layout)

        random_selection = QGroupBox("Random")
        button1 = QPushButton("Zoom In")
        # button1.clicked.connect(self.zoom_in)
        button1.setGeometry(0, 0, 100, 100)
        button2 = QPushButton("Zoom Out")
        # button2.clicked.connect(self.zoom_out)

        layout = QVBoxLayout()
        layout.addWidget(button1)
        layout.addWidget(button2)
        random_selection.setLayout(layout)

        options_layout = QVBoxLayout()
        options_layout.addWidget(date_selection)
        options_layout.addWidget(random_selection)
        self.options_area = QGroupBox("Options")
        self.options_area.setLayout(options_layout)

    def keyPressEvent(self, event):
        if event.key() == 87:  # W
            self.location[0] += 1.0
        elif event.key() == 83:  # S
            self.location[0] -= 1.0
        elif event.key() == 65:  # A
            self.location[1] -= 1.0
        elif event.key() == 68:  # D
            self.location[1] += 1.0
        elif event.key() == 69:  # E
            self.zoom -= 1
        elif event.key() == 82:  # R
            self.zoom += 1
        else:
            return

        self.refresh()

    def refresh(self):
        self.map = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                              zoom_control=False, keyboard=False)
        roundnum = "function(num) {return L.Util.formatNum(num, 5);};"
        mouse = plugins.MousePosition(position='topright', separator=' | ', prefix="Position:", lat_formatter=roundnum,
                                      lng_formatter=roundnum).add_to(self.map)
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.web_map.setHtml(data.getvalue().decode())
        self.web_map.update()

    def createMap(self):
        # Right part of main page (MAP PLACEHOLDER)
        m = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                       zoom_control=False, keyboard=False)
        # p = folium.Marker(
        # [27.994402, -81.760254], popup="FL", icon=folium.Icon(color='darkpurple', icon='')
        # ).add_to(m)
        # folium.LayerControl(collapsed=False).add_to(m)
        # m = folium.Map(location=[27.994402, -81.760254], tiles="CartoDB Positron", min_zoom=7, zoom_start=7)
        roundnum = "function(num) {return L.Util.formatNum(num, 5);};"
        mouse = plugins.MousePosition(position='topright', separator=' | ', prefix="Position:", lat_formatter=roundnum,
                                      lng_formatter=roundnum).add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)
        web_map = QWebEngineView()
        web_map.setHtml(data.getvalue().decode())
        self.web_map = web_map
