from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtGui import Qt, QFont
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class Help(QWidget):
    def __init__(self, parent=None):
        super(Help, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        controls = QWidget()
        control_layout = QHBoxLayout()
        control_layout.setSpacing(20 * UIRescale.Scale)

        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(45 * UIRescale.Scale, 45 * UIRescale.Scale)
        self.help_button.setContentsMargins(0,0,50*UIRescale.Scale,0)
        self.help_button.setStyleSheet("background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px;")
        self.help_button.clicked.connect(self.toggle_help_box)
        control_layout.addWidget(self.help_button, alignment=Qt.AlignLeft)

        self.close_button = QPushButton("Close")
        self.close_button.setFixedSize(100 * UIRescale.Scale, 45 * UIRescale.Scale)
        self.close_button.setContentsMargins(0, 0, 0, 0)
        self.close_button.setStyleSheet("background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px;")
        self.close_button.clicked.connect(self.close_help_box)
        control_layout.addWidget(self.close_button, alignment=Qt.AlignLeft)
        control_layout.addStretch(1)

        controls.setLayout(control_layout)

        self.help_box = QWidget()
        self.help_box.setStyleSheet("background-color: rgba(255, 255, 255, 255); border-radius: 5px;")
        help_layout = QVBoxLayout()
        help_layout.setSpacing(0)

        instructionText1 = QLabel(self)
        instructionText1.setStyleSheet("background-color: transparent;")
        instructionText1.setText("Welcome to WeatherViz!")
        instructionText1.setFont(QFont("Arial", 28, QFont.Bold))


        instructionText2 = QLabel(self)
        instructionText2.setStyleSheet("background-color: transparent;")
        instructionText2.setText("Instructions:")
        instructionText2.setFont(QFont("Arial", 18))

        instructionText3 = QLabel(self)
        instructionText3.setStyleSheet("background-color: transparent;")
        instructionText3.setText(
            "    ∙ Use the buttons in the bottom right corner to move and zoom around the map\n    "
            "∙ WASD can also be used to move plus Q to zoom in and E to zoom out\n    "
            "∙ Set the Date Range to fetch between the two dates\n    "
            "∙ The Timeline Interval lets you select between hourly and daily data\n    "
            "∙ The Heatmap Resolution decides how many points will be rendered on the map\n         "
            "◦ Higher resolutions will take longer to query\n    "
            "∙ Choose the weather statistic you want to query using the Weather Type setting\n    "
            "∙ Press the Query button to begin a query\n         "
            "◦ A progress bar will let you know how much of the query is currently completed\n    "
            "∙ When the query is completed, the heatmap will automatically appear on the map\n         "
            "◦ Press the play button in the upper-right corner to start a timelapse of the heatmap\n    "
            "∙ Press the Close button below to enable map movement and querying")

        help_layout.addWidget(instructionText1, alignment=Qt.AlignCenter)
        help_layout.addWidget(instructionText2, alignment=Qt.AlignCenter)
        help_layout.addWidget(instructionText3, alignment=Qt.AlignCenter)

        self.help_box.setLayout(help_layout)

        layout.addWidget(self.help_box)
        layout.addWidget(controls, alignment=Qt.AlignBottom)
        self.setLayout(layout)

    def toggle_help_box(self):
        self.help_box.setHidden(not self.help_box.isHidden())
        self.close_button.setHidden(not self.close_button.isHidden())

    def close_help_box(self):
        self.help_box.setHidden(True)
        self.close_button.setHidden(True)