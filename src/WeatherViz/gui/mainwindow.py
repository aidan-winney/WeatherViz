from PyQt5.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QDateEdit, QCalendarWidget
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QDate
import folium
from folium import plugins
import sys
import io
import pandas as pd
import plotly.express as px

#NOT NEEDED, JUST FOR INITIAL TESTING
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
        self.setWindowTitle("WeatherViz")
        self.setStyleSheet("background-color: gainsboro;")  # Change as needed

        self.createOptionsArea()
        self.createMap()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.options_area, 1)
        main_layout.addWidget(self.map, 3)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    #Option selection area on left side
    def createOptionsArea(self):
        calendar_start = QCalendarWidget()
        calendar_start.setDateRange(QDate(1980, 1, 1), QDate.currentDate())
        start_date = QDateEdit(calendarPopup=True)
        start_date.setDate(QDate.currentDate())
        start_date.setMinimumDate(QDate(1980, 1, 1)) # Change to correct minimum date
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
        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")

        layout = QVBoxLayout()
        layout.addWidget(button1)
        layout.addWidget(button2)
        random_selection.setLayout(layout)

        options_layout = QVBoxLayout()
        options_layout.addWidget(date_selection)
        options_layout.addWidget(random_selection)
        self.options_area = QGroupBox("Options")
        self.options_area.setLayout(options_layout)

    def createMap(self):

        #fl_counties = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/florida_county_data.geojson")

        fig = px.choropleth_mapbox([], geojson = "https://raw.githubusercontent.com/plotly/datasets/master/florida_county_data.geojson",
                                color_discrete_sequence=["fuchsia"], zoom=3, height=300)
        #fig.update_geos(fitbounds="locations", visible=False)
        fig.update_geos(
            center=dict(lon=27.75, lat=-83.25),
            projection_rotation=dict(lon=30, lat=30, roll=30),
            lataxis_range=[-90, -40], lonaxis_range=[0, 50]
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.show()


        # fig = px.choropleth_mapbox(
        #     soybean,  # soybean database
        #     locations= “Estado”,  # define the limits on the map/geography
        # geojson = "https://raw.githubusercontent.com/plotly/datasets/master/florida_county_data.geojson",
        # color = "Produção",  # defining the color of the scale through the database
        # hover_name = “Estado”,  # the information in the box
        # hover_data = ["Produção", "Longitude", "Latitude"],
        # title = "Produtivida da soja (Toneladas)",  # title of the map
        # mapbox_style = "carto-positron",  # defining a new map style
        # center = {"lat": -14, "lon": -55},  # define the limits that will be plotted
        # zoom = 3,  # map view size
        # opacity = 0.5,  # opacity of the map color, to appear the background
        # animation_frame = “ano”  # creating the application based on the year
        # fig.show()


        #Right part of main page (MAP PLACEHOLDER)
        m = folium.Map(location=[27.75, -83.25], tiles="CartoDB Positron", min_zoom=7, zoom_start=7)
        p = folium.Marker(
            [27.994402, -81.760254], popup="FL", icon=folium.Icon(color='darkpurple', icon='')
        ).add_to(m)
        # folium.LayerControl(collapsed=False).add_to(m)
        #  m = folium.Map(location=[27.994402, -81.760254], tiles="CartoDB Positron", min_zoom=7, zoom_start=7)

        data = io.BytesIO()
        m.save(data, close_file=False)
        web_map = QWebEngineView()
        web_map.setHtml(data.getvalue().decode())
        self.map = web_map

