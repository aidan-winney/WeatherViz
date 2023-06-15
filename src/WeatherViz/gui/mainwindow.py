from PyQt5.QtWidgets import QApplication, QLabel, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget
from PyQt5.QtGui import QPalette, QColor

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
        date_selection = QGroupBox("Date")
        date1 = QPushButton("Date 1")
        date2 = QPushButton("Date 2")
        date_layout = QVBoxLayout()
        date_layout.addWidget(date1)
        date_layout.addWidget(date2)
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
        # Right part of main page (MAP PLACEHOLDER)
        self.map = Color('blue')

