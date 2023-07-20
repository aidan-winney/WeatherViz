from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect, QDate
from PySide2.QtGui import QPalette, QColor, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QToolButton, \
    QSizePolicy, QDateEdit, QRadioButton

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.DateRangeChooser import DateRangeChooser
from WeatherViz.gui.DateRangeSlider import DateRangeSlider
from WeatherViz.gui.Panel import Panel
from WeatherViz.gui.ProgressBar import ProgressBar
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

from WeatherViz.gui.ScrollableContent import ScrollableContent


class QueryPane(QWidget):
    def __init__(self, content, parent=None):
        super(QueryPane, self).__init__(parent)
        self.content = content
        self.initUI(content)

    def initUI(self, content):
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.setMaximumWidth(450 * UIRescale.Scale)
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.tab_widget.setStyleSheet("""
                QTabBar::tab:selected { 
                        background: rgba(60, 60, 60, 255);
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                        font-weight: bold; 
                        color: white;
                        padding-left: 10px;
                        padding-right: 5px;
                        height: 80px;
                }
                QTabBar::tab:!selected { 
                        background: rgba(45, 45, 45, 255);
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                        color: white;
                        padding-left: 7px;
                        padding-right: 5px;
                        height: 80px;
                }
          """)
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.currentChanged.connect(self.tabChanged)

        layout = QVBoxLayout()
        layout.setContentsMargins(5 * UIRescale.Scale, 5 * UIRescale.Scale, 5 * UIRescale.Scale, 5 * UIRescale.Scale)

        layout.addWidget(self.tab_widget, alignment=Qt.AlignTop)
        layout.addWidget(self.createTab())
        self.setLayout(layout)
        self.addTab(content)

    def createTab(self):
        tab_widget = QWidget()

        add_tab_button = QToolButton()
        add_tab_button.setText("+")
        add_tab_button.setFixedSize(50 * UIRescale.Scale, 50 * UIRescale.Scale)
        add_tab_button.setStyleSheet("background-color: rgba(60, 60, 60, 255); border-radius: 20px; font-weight: bold; color: white")
        add_tab_button.clicked.connect(self.addTab)
        add_tab_button.setToolTip("Save query and begin a new one")

        tab_layout = QHBoxLayout()
        tab_layout.addWidget(add_tab_button)

        tab_widget.setLayout(tab_layout)
        return tab_widget

    def addTab(self, content=None):
        # start_date = QDateEdit(calendarPopup=True)
        # start_date.setDate(QDate.currentDate())
        # end_date = QDateEdit(calendarPopup=True)
        # slider = DateRangeSlider(self.start_date, end_date, self)
        # date_selector = DateRangeChooser(self.start_date, end_date, slider, self)
        # date_selector.setGeometry(45 * UIRescale.Scale, 15 * UIRescale.Scale, 425 * UIRescale.Scale, 90 * UIRescale.Scale)
        # hourly = QRadioButton("Hourly")
        # daily = QRadioButton("Daily")
        # daily.setChecked(True)
        # twobytwo = QRadioButton("2x2")
        # fourbyfour = QRadioButton("4x4")
        # fourbyfour.setChecked(True)
        # sixteenbysixteen = QRadioButton("16x16")
        # precipitation = QRadioButton("Precipitation")
        # temperature = QRadioButton("Temperature")
        # temperature.setChecked(True)
        # wind = QRadioButton("Wind")
        # progress = ProgressBar(self)
        # progress.set_progress(4, 4)
        # submit_button = QPushButton('Query', self)
        # submit_button.setFixedHeight(50 * UIRescale.Scale)
        # submit_button.setStyleSheet("background-color: rgba(90, 90, 90, 255);  border-radius: 3px;")
        #
        # new_tab = QWidget()
        # new_tab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        # new_tab.setContentsMargins(20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale)
        # new_tab.setStyleSheet("background-color: rgba(60, 60, 60, 255); border-top-left-radius: 0px; border-top-right-radius: 5px; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px; font-weight: bold; color: white")
        # content_layout = QVBoxLayout()
        # content_layout.setSpacing(20 * UIRescale.Scale)
        #
        # content = [ScrollableContent([QLabel("Date Range"), date_selector,
        #                                         Panel("Timeline Interval", "Tooltip", [hourly, daily]),
        #                                         Panel("Heatmap Resolution", "Tooltip", [twobytwo, fourbyfour, sixteenbysixteen]),
        #                                         Panel("Weather Type", "Tooltip", [temperature, precipitation, wind])], self),
        #                                         submit_button, progress]
        # for item in content:
        #     item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        #     content_layout.addWidget(item)
        # new_tab.setLayout(content_layout)
        # tab_index = self.tab_widget.addTab(new_tab, "Query " + f"{self.tab_widget.count() + 1}")
        # self.tab_widget.setCurrentIndex(tab_index)



        # if content:
        #     new_tab = QWidget()
        #     new_tab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        #     new_tab.setContentsMargins(20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale)
        #     new_tab.setStyleSheet("background-color: rgba(60, 60, 60, 255); border-top-left-radius: 0px; border-top-right-radius: 5px; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px; font-weight: bold; color: white")
        #     content_layout = QVBoxLayout()
        #     content_layout.setSpacing(20 * UIRescale.Scale)
        #     # print(str(self.tab_widget.currentIndex().real))
        #
        #     # content_layout.addWidget(ScrollableContent([QLabel("Date Range")]))
        #     # new_tab.setLayout(content_layout)
        #
        #     for item in content:
        #         item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        #         content_layout.addWidget(item)
        #     new_tab.setLayout(content_layout)
        #     tab_index = self.tab_widget.addTab(new_tab, "Query " + f"{self.tab_widget.count() + 1}")
        #     self.tab_widget.setCurrentIndex(tab_index)
        #
        # if not content:
        #     current_index = self.tab_widget.currentIndex()
        #     new_tab = self.tab_widget.currentWidget()
        #     tab_index = self.tab_widget.addTab(ScrollableContent([QLabel("Date Range")]), "Query " + f"{self.tab_widget.count() + 1}")
        #     self.tab_widget.setCurrentIndex(tab_index)


        new_tab = QWidget()
        new_tab.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        new_tab.setContentsMargins(20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale, 20 * UIRescale.Scale)
        new_tab.setStyleSheet("background-color: rgba(60, 60, 60, 255); border-top-left-radius: 0px; border-top-right-radius: 5px; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px; font-weight: bold; color: white")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20 * UIRescale.Scale)
        # print(str(self.tab_widget.currentIndex().real))

        # content_layout.addWidget(ScrollableContent([QLabel("Date Range")]))
        # new_tab.setLayout(content_layout)

        for item in self.content:
            item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            content_layout.addWidget(item)
        new_tab.setLayout(content_layout)

        # tab_name = f"Tab {self.tab_widget.count() + 1}"
        # tab_content = QLabel(f"Content of {tab_name}")

        tab_index = self.tab_widget.addTab(new_tab, "Query " + f"{self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(tab_index)

    def tabChanged(self, index):
        # Create a palette with a blue color for the active tab
        palette = QPalette()
        palette.setColor(QPalette.Button, QColor("#3c3c3c"))  # Blue color for active tab

        # Set the palette for the active tab
        self.tab_widget.widget(index)