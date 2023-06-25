import requests
from PySide2.QtGui import Qt, QPixmap
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene


class MapWidget(QGraphicsView):
    def __init__(self, access_token, initial_lat, initial_lon, initial_zoom):
        super().__init__()
        self.access_token = access_token
        self.lat = initial_lat
        self.lon = initial_lon
        self.zoom = initial_zoom
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

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            diff = event.pos() - self.last_pos
            self.pan_map(diff.x()/7, diff.y()/7)
            self.last_pos = event.pos()

    def pan_map(self, dx, dy):
        self.lon -= dx
        self.lat += dy
        self.set_map()

    def wheelEvent(self, event):
        zoom_factor = 1.25  # Zoom factor for each wheel step
        zoom_direction = event.angleDelta().y()
        zoom_direction = 1 if zoom_direction > 0 else -1

        self.zoom *= zoom_factor ** zoom_direction
        self.scale(zoom_factor ** zoom_direction, zoom_factor ** zoom_direction)
        self.set_map()

    def keyPressEvent(self, event):
        step = 1
        if event.key() == Qt.Key_Up:
            self.lat += step
        elif event.key() == Qt.Key_Down:
            self.lat -= step
        elif event.key() == Qt.Key_Left:
            self.lon -= step
        elif event.key() == Qt.Key_Right:
            self.lon += step
        elif event.key() == Qt.Key_Plus:
            self.zoom += 1
        elif event.key() == Qt.Key_Minus:
            self.zoom -= 1
        self.set_map()
