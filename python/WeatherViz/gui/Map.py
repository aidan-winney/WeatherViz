import base64
import json

import requests
from PIL.Image import Image
from PySide2.QtCore import QRect
from PySide2.QtGui import Qt, QPixmap
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout
from folium import folium, plugins, features, Marker
import io

from WeatherViz.UIRescale import UIRescale


class MapWidget(QGraphicsView):
    def __init__(self, initial_location, initial_zoom):
        super().__init__()
        self.map = None
        self.web_map = None
        self.zoom = initial_zoom
        self.location = initial_location
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setFrameStyle(QGraphicsView.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setInteractive(True)
        self.createMap()

    def move_up(self):
        self.location[0] += 1 / (2 ** (self.zoom - 8))
        self.refresh()

    def move_down(self):
        self.location[0] -= 1 / (2 ** (self.zoom - 8))
        self.refresh()
    def move_left(self):
        self.location[1] -= 1 / (2 ** (self.zoom - 8))
        self.refresh()
    def move_right(self):
        self.location[1] += 1 / (2 ** (self.zoom - 8))
        self.refresh()


    def createMap(self):
        # Right part of main page (MAP PLACEHOLDER)
        m = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                       zoom_control=False, keyboard=False, dragging=False, doubleClickZoom=False,
                       boxZoom=False, scrollWheelZoom=False)
        roundnum = "function(num) {return L.Util.formatNum(num, 6);};"
        mouse = plugins.MousePosition(position='topright', separator=' | ', prefix="Position:", lat_formatter=roundnum,
                                      lng_formatter=roundnum).add_to(m)

        # icon = features.CustomIcon('gui\\Donpeng.png', icon_size=(50, 50))
        # marker = folium.Marker(location=[29.651634, -82.324829], icon=icon)
        # marker.add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)
        web_map = QWebEngineView()
        web_map.setHtml(data.getvalue().decode())
        self.web_map = web_map
        self.web_map.setContentsMargins(0, 0, 0, 0)
        self.web_map.setFixedSize(1270 * UIRescale.Scale, 850 * UIRescale.Scale)
        # print(self.web_map.width())
        # print(self.web_map.height())
        self.scene.clear()
        # html = QWidget()
        # layout = QVBoxLayout()
        # layout.setContentsMargins(0,0,0,0)
        # layout.addWidget(html)
        # html.setLayout(layout)
        # html.setContentsMargins(0,0,0,0)
        self.scene.addWidget(web_map)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def refresh(self, image=None):
        self.map = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                              zoom_control=False, keyboard=False, dragging=False, doubleClickZoom=False,
                              boxZoom=False, scrollWheelZoom=False)
        roundnum = "function(num) {return L.Util.formatNum(num, 5);};"
        mouse = plugins.MousePosition(position='topright', separator=' | ', prefix="Position:", lat_formatter=roundnum,
                                      lng_formatter=roundnum).add_to(self.map)
        if image != None:
            image.save('output.png')
            icon = features.CustomIcon('output.png', icon_size=(self.web_map.width(), self.web_map.height()))
            marker = Marker(location=self.location, icon=icon)
            marker.add_to(self.map)

        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.web_map.setHtml(data.getvalue().decode())
        self.web_map.update()

    def set_map(self):
        url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{self.lon},{self.lat},{self.zoom},0,0/1270x800?access_token={self.access_token}"
        response = requests.get(url)
        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.fitInView(self.scene.sceneRect())
        else:
            print("Failed to load map:", response.text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()
    #
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            diff = event.pos() - self.last_pos
            self.pan_map(diff.x(), diff.y())
            self.last_pos = event.pos()

    def pan_map(self, dx, dy):
        self.location[1] -= dx
        self.location[0] += dy
        self.refresh()
    #
    # def wheelEvent(self, event):
    #     zoom_factor = 1.25  # Zoom factor for each wheel step
    #     zoom_direction = event.angleDelta().y()
    #     zoom_direction = 1 if zoom_direction > 0 else -1
    #
    #     self.zoom *= zoom_factor ** zoom_direction
    #     self.scale(zoom_factor ** zoom_direction, zoom_factor ** zoom_direction)
    #     self.set_map()
    #
    # def keyPressEvent(self, event):
    #     step = 1
    #     if event.key() == Qt.Key_Up:
    #         self.lat += step
    #     elif event.key() == Qt.Key_Down:
    #         self.lat -= step
    #     elif event.key() == Qt.Key_Left:
    #         self.lon -= step
    #     elif event.key() == Qt.Key_Right:
    #         self.lon += step
    #     elif event.key() == Qt.Key_Plus:
    #         self.zoom += 1
    #     elif event.key() == Qt.Key_Minus:
    #         self.zoom -= 1
    #     self.set_map()
