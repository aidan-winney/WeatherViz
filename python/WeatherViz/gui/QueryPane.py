import copy

from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect, QDate
from PySide2.QtGui import QPalette, QColor, Qt, QIcon
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QToolButton, \
    QSizePolicy, QDateEdit, QRadioButton
from PySide2 import QtCore

from WeatherViz.UIRescale import UIRescale
import sqlite3
from WeatherViz.gui.DateRangeChooser import DateRangeChooser
from WeatherViz.gui.DateRangeSlider import DateRangeSlider
from WeatherViz.gui.Panel import Panel
from WeatherViz.gui.ProgressBar import ProgressBar
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

from WeatherViz.gui.ScrollableContent import ScrollableContent


class QueryPane(QWidget):
    switch_tab = QtCore.Signal()
    delete_tab = QtCore.Signal()
    def __init__(self, content, parent=None):
        super(QueryPane, self).__init__(parent)
        self.tab_widget = None
        self.count = 0
        self.initUI(content)

    def initUI(self, content):
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.setMaximumWidth(450 * UIRescale.Scale)
        self.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.tab_widget.setContentsMargins(0, 0, 0, 0)
        height = UIRescale.Scale * 95
        padding_left = UIRescale.Scale * 12
        padding_right = UIRescale.Scale * 10
        border_radius = UIRescale.Scale * 6
        self.tab_widget.tabBar().setStyleSheet(f"""
                QTabBar::tab:selected {{
                        background: rgba(60, 60, 60, 255);
                        border-top-left-radius: {border_radius}px;
                        border-bottom-left-radius: {border_radius}px;
                        font-weight: bold; 
                        color: white;
                        padding-left: {padding_left}px;
                        padding-right: {padding_right}px;
                        height: {height}px;
                }}
                QTabBar::tab:!selected {{
                        background: rgba(45, 45, 45, 255);
                        border-top-left-radius: {border_radius}px;
                        border-bottom-left-radius: {border_radius}px;
                        color: white;
                        padding-left: {padding_left}px;
                        padding-right: {padding_right}px;
                        height: {height}px;
                }}
          """)
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.currentChanged.connect(self.tabChanged)

        layout = QVBoxLayout()
        layout.setContentsMargins(5 * UIRescale.Scale, 5 * UIRescale.Scale, 5 * UIRescale.Scale, 5 * UIRescale.Scale)
        layout.setSpacing(0)

        tabbed_panel = QWidget()
        panel_layout = QHBoxLayout()
        panel_layout.setSpacing(0)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        panel.setContentsMargins(20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale)
        panel.setStyleSheet("background-color: rgba(60, 60, 60, 255); border-top-left-radius: 0px; border-top-right-radius: 5px; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px; font-weight: bold; color: white")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20 * UIRescale.Scale)
        for item in content:
            item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            content_layout.addWidget(item)
        panel.setLayout(content_layout)

        self.tab_widget.tabBar().setMaximumHeight(500 * UIRescale.Scale)
        self.tab_widget.tabBar().setMinimumHeight(100 * UIRescale.Scale)
        panel_layout.addWidget(self.tab_widget.tabBar(), alignment=Qt.AlignTop)
        panel_layout.addWidget(panel, alignment=Qt.AlignTop)
        tabbed_panel.setLayout(panel_layout)
        tabbed_panel.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(tabbed_panel, alignment=Qt.AlignTop)
        layout.addWidget(self.tabControls())
        self.setLayout(layout)
        self.addTab()

    def tabControls(self):
        tab_widget = QWidget()

        add_tab_button = QToolButton()
        add_tab_button.setText("+")
        add_tab_button.setFixedSize(60 * UIRescale.Scale, 60 * UIRescale.Scale)
        border_radius = UIRescale.Scale * 30
        add_tab_button.setStyleSheet(f"""
                QToolButton:pressed {{ 
                    background-color: rgba(50, 50, 50, 255); 
                }} 
                QToolButton {{ 
                    background-color: rgba(60, 60, 60, 255); border-radius: {border_radius}px; font-weight: bold; color: white }}""")
        add_tab_button.clicked.connect(self.addTab)
        add_tab_button.setToolTip("Save query and begin a new one")

        self.delete_tab_button = QToolButton()
        self.delete_tab_button.setIcon(QIcon("WeatherViz/python/WeatherViz/assets/trash.png"))
        self.delete_tab_button.setFixedSize(60 * UIRescale.Scale, 60 * UIRescale.Scale)
        border_radius = UIRescale.Scale * 30
        self.delete_tab_button.setStyleSheet(f"""
                QToolButton:pressed {{ 
                    background-color: rgba(58, 20, 20, 255); 
                }} 
                QToolButton:disabled {{
                    background-color: rgba(40, 40, 40, 255); 
                }} 
                QToolButton {{ 
                    background-color: rgba(68, 30, 30, 255); border-radius: {border_radius}px; font-weight: bold; color: white }}""")
        self.delete_tab_button.clicked.connect(self.deleteTab)
        self.delete_tab_button.setToolTip("Delete currently opened query")

        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(100 * UIRescale.Scale, 25 * UIRescale.Scale, 70 * UIRescale.Scale, 0)
        tab_layout.addWidget(add_tab_button)
        tab_layout.addWidget(self.delete_tab_button)

        tab_widget.setLayout(tab_layout)
        return tab_widget


    def addTab(self):
        tab_index = self.tab_widget.addTab(QWidget(), "Query " + f"{self.count + 1}")
        self.tab_widget.setCurrentIndex(tab_index)
        self.count = self.count + 1

    def deleteTab(self):
        index = self.tab_widget.currentIndex()
        if index >= 1:
            self.delete_tab.emit()
            self.tab_widget.removeTab(index)

    def tabChanged(self, index):
        self.delete_tab_button.setEnabled(index >= 1)
        self.switch_tab.emit()