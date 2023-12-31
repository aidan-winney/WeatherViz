import base64
import json

import requests
from PIL.Image import Image
from PySide2 import QtCore
from PySide2.QtCore import QRect, QRectF
from PySide2.QtGui import Qt, QPixmap, QPainter, QColor, QPainterPath, QBrush, QPen, QRegion
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout, QGraphicsRectItem, \
    QGraphicsEllipseItem, QGraphicsProxyWidget
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
        self.marker = None

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setStyleSheet("background-color: transparent; border-radius: 10px;")
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setInteractive(False)
        self.createMap()
        self.path = QPainterPath()
        self.path.addRoundedRect(QRectF(self.rect()), 15.0 * UIRescale.Scale, 15.0 * UIRescale.Scale)
        mask = QRegion(self.path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def createMap(self):
        # Right part of main page
        m = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                       zoom_control=False, keyboard=False, dragging=False, doubleClickZoom=False,
                       boxZoom=False, scrollWheelZoom=False)

        data = io.BytesIO()
        m.save(data, close_file=False)
        web_map = QWebEngineView()
        web_map.setHtml(data.getvalue().decode())
        self.web_map = web_map
        self.web_map.setGeometry(self.rect())
        self.web_map.setContentsMargins(0, 0, 0, 0)
        # self.web_map.setFixedSize(1270 * UIRescale.Scale, 850 * UIRescale.Scale)

        self.scene.clear()
        self.scene.addWidget(self.web_map)
        self.fitInView(self.rect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        # Resize the web view to fit the widget
        self.web_map.setGeometry(self.rect())
        self.path = QPainterPath()
        self.path.addRoundedRect(QRectF(self.rect()), 15.0 * UIRescale.Scale, 15.0 * UIRescale.Scale)
        mask = QRegion(self.path.toFillPolygon().toPolygon())
        self.setMask(mask)
        super().resizeEvent(event)

    def refresh(self, image=None, no_map_refresh=False):
        self.map = folium.Map(location=self.location, tiles="CartoDB Positron", zoom_start=self.zoom,
                              zoom_control=False, keyboard=False, dragging=False, doubleClickZoom=False,
                              boxZoom=False, scrollWheelZoom=False)

        if image != None:
            image.save('output.png')
            icon = features.CustomIcon('output.png', icon_size=(self.web_map.width(), self.web_map.height()))
            self.marker = Marker(location=self.location, icon=icon)
            self.marker.add_to(self.map)
        else:
            self.marker = None

        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.web_map.setHtml(data.getvalue().decode())
        self.web_map.update()