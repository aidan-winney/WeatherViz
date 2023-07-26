import numpy as np
from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect, QEvent, QCoreApplication, QSize, QTimer
from PySide2.QtGui import Qt, QFont, QResizeEvent, QPixmap, QImage, QPainter, QPainterPath, QWindow, QBrush, QColor
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QSizePolicy, \
    QApplication, QGraphicsBlurEffect, QGraphicsScene, QGraphicsView

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

from WeatherViz.gui.ScrollableContent import ScrollableContent


class Help(QWidget):
    def __init__(self, widget, parent=None):
        super(Help, self).__init__(parent)
        self.widget = widget
        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        controls = QWidget()
        controls.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(20 * UIRescale.Scale)

        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(45 * UIRescale.Scale, 45 * UIRescale.Scale)
        self.help_button.setContentsMargins(0,0,50*UIRescale.Scale,0)
        self.help_button.setStyleSheet("""
                QPushButton:pressed { 
                    background-color: rgba(80, 80, 80, 200); 
                }
                QPushButton:disabled {
                    background-color: rgba(70, 70, 70, 255); 
                }
                QPushButton { 
                    background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }""")
        self.help_button.clicked.connect(self.toggle_help_box)
        control_layout.addWidget(self.help_button, alignment=Qt.AlignLeft)

        self.close_button = QPushButton("Close")
        self.close_button.setFixedSize(100 * UIRescale.Scale, 45 * UIRescale.Scale)
        self.close_button.setContentsMargins(0, 0, 0, 0)
        self.close_button.setStyleSheet("""
                QPushButton:pressed { 
                    background-color: rgba(80, 80, 80, 200); 
                } 
                QPushButton { 
                    background-color: rgba(90, 90, 90, 200); font-weight: bold; color: white; border-radius: 3px }""")
        self.close_button.clicked.connect(self.close_help_box)
        self.close_button.setHidden(True)
        control_layout.addWidget(self.close_button, alignment=Qt.AlignLeft)
        control_layout.addStretch(1)

        controls.setLayout(control_layout)

        instructionText1 = QLabel(self)
        instructionText1.setStyleSheet("background-color: transparent;")
        instructionText1.setText("Welcome to WeatherViz!")
        instructionText1.setAlignment(Qt.AlignCenter)
        instructionText1.setFont(QFont("Arial", 28, QFont.Bold))

        instructionText2 = QLabel(self)
        instructionText2.setStyleSheet("background-color: transparent;")
        instructionText2.setText("Instructions:")
        instructionText2.setAlignment(Qt.AlignCenter)
        instructionText2.setFont(QFont("Arial", 18))

        instructionText3 = QLabel(self)
        instructionText3.setStyleSheet("background-color: transparent;")
        instructionText3.setText(
            "Map Navigation:\n"
            "    ∙ Use the buttons in the bottom right corner to move and zoom around the map\n    "
            "∙ WASD can also be used to move plus Q to zoom in and E to zoom out\n\n"
            "Query Navigation: \n    "
            "∙ Set the Date Range to fetch between the two dates\n        "
            "◦ Data from the past week is not available yet\n    "
            "∙ The Timeline Interval lets you select between hourly and daily data\n    "
            "∙ The Heatmap Resolution decides how many points will be sampled on the map\n         "
            "◦ Higher resolutions will take longer to query, but will be more accurate\n    "
            "∙ Choose the weather statistic you want to query using the Weather Type setting\n    "
            "∙ Press the Query button to begin a query\n         "
            "◦ A progress bar will let you know how much of the query is currently completed\n    "
            "∙ When the query is completed, the heatmap will automatically appear on the map\n         "
            "◦ Press the play button in the upper-right corner to start a timelapse of the heatmap\n    "
            "∙ Click + to open a new query tab and previous query result will remain on previous tabs\n    "
            "∙ Click the trash symbol to delete the current saved query and tab\n\n"
            "Times are based on EST timezone\n\n"
            "Press the Close button below to close this window")


        self.help_box = QWidget()
        self.help_box.setStyleSheet("background-color: rgba(240, 240, 240, 255); border-radius: 5px;")

        help_layout = QVBoxLayout(self.help_box)
        help_layout.setMargin(20 * UIRescale.Scale)
        content = ScrollableContent([instructionText1, instructionText2, instructionText3])
        content.setStyleSheet("""
            QScrollArea {
                height: 1000px;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                width: 10px;
                background-color: rgba(50, 50, 50, 255);
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: gray;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background-color: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }""")
        content.setAttribute(Qt.WA_TranslucentBackground)
        help_layout.addWidget(content)

        self.help_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.help_box.setMaximumWidth(900 * UIRescale.Scale)
        self.help_box.setMaximumHeight(300 * UIRescale.Scale)
        self.help_box.setHidden(True)

        layout.addWidget(self.help_box)
        layout.addWidget(controls, alignment=Qt.AlignBottom)
        self.setLayout(layout)

        self.toggle_help_box()

    def toggle_help_box(self):
        self.setMaximumHeight(900 * UIRescale.Scale)
        self.setMaximumWidth(1100 * UIRescale.Scale)
        resize_event = QResizeEvent(QSize(800 * UIRescale.Scale, 400 * UIRescale.Scale), QSize(800 * UIRescale.Scale, 100 * UIRescale.Scale))
        QApplication.sendEvent(self, resize_event)
        self.move(self.pos().x(), self.widget.rect().height() - self.rect().height() - 48 * UIRescale.Scale)
        self.help_box.setHidden(not self.help_box.isHidden())
        self.close_button.setHidden(not self.close_button.isHidden())
        self.help_button.setDisabled(True)

    def close_help_box(self):
        self.setMaximumHeight(100 * UIRescale.Scale)
        self.setMaximumWidth(100 * UIRescale.Scale)
        self.move(self.pos().x(), self.widget.rect().height() - self.rect().height() - 48 * UIRescale.Scale)
        self.help_box.setHidden(True)
        self.close_button.setHidden(True)
        self.help_button.setDisabled(False)

    def resizeEvent(self, event):
        self.resize(800 * UIRescale.Scale, 400 * UIRescale.Scale)
        super().resizeEvent(event)