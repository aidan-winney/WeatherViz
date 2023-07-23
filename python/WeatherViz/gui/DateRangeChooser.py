from PySide2.QtCore import QPropertyAnimation, QEasingCurve, QRect, QDate
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCalendarWidget, QDateEdit

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.TransparentRectangle import TransparentRectangle

class DateRangeChooser(QWidget):
    def __init__(self, start_date, end_date, slider, parent=None):
        super(DateRangeChooser, self).__init__(parent)
        self.slider = slider
        self.start_date = start_date
        self.end_date = end_date
        self.initUI(start_date, end_date)

    def initUI(self, start_date, end_date):
        layout = QVBoxLayout()
        layout.setContentsMargins(20 * UIRescale.Scale, 10 * UIRescale.Scale, 30 * UIRescale.Scale, 10 * UIRescale.Scale)

        start_date_selector = QWidget()
        start_date_layout = QHBoxLayout()
        start_date_label = QLabel()
        start_date_label.setMargin(0)
        start_date_label.setContentsMargins(0, 0, 5 * UIRescale.Scale, 0)
        start_date_label.setText("From:")
        start_date_label.setStyleSheet("background-color: rgba(90, 90, 90, 0); font-weight: bold; color: white")
        start_date_layout.addWidget(start_date_label)
        start_date_layout.addStretch(1)

        calendar_start = QCalendarWidget(self)
        calendar_start.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                border-radius: 10px;
                background-color: rgba(70, 70, 70, 100);
                color: rgba(200, 200, 200, 255);
                alternate-background-color: rgba(120, 120, 120, 255);
                selection-background-color: rgba(55, 159, 225, 255);
                selection-color: white;
                font-size: 14px;
            }

            QCalendarWidget QAbstractItemView:enabled:hover {
                background-color: rgba(60, 60, 60, 255);
            }
            """)
        calendar_start.setDateRange(QDate(1980, 1, 1), QDate.currentDate().addDays(-9))
        self.start_date.setStyleSheet("""
                    QDateEdit::down-arrow {
                        image: url(WeatherViz/python/WeatherViz/assets/down_arrow.png);
                    }
                    
                    QDateEdit::drop-down {
                        background-color: rgba(70, 70, 70, 255);
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 20px;
                        border-left-width: 1px;
                        border-left-color: darkgray;
                        border-left-style: solid;
                        border-top-right-radius: 3px;
                        border-bottom-right-radius: 3px;
                    }
                    QDateEdit { background-color: rgba(55, 55, 55, 255);  border-radius: 3px; }""")
        self.start_date.setFixedSize(150 * UIRescale.Scale, 30 * UIRescale.Scale)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumDate(QDate(1980, 1, 1))  # Change to correct minimum date
        self.start_date.setMaximumDate(QDate.currentDate().addDays(-9))
        self.start_date.setCalendarWidget(calendar_start)
        start_date_layout.addWidget(self.start_date)
        start_date_selector.setLayout(start_date_layout)

        end_date_selector = QWidget()
        end_date_layout = QHBoxLayout()
        end_date_label = QLabel()
        end_date_label.setMargin(0)
        end_date_label.setContentsMargins(0, 0, 5 * UIRescale.Scale, 0)
        end_date_label.setText("To:")
        end_date_label.setStyleSheet("background-color: rgba(90, 90, 90, 0); font-weight: bold; color: white")
        end_date_layout.addWidget(end_date_label)
        end_date_layout.addStretch(1)

        calendar_end = QCalendarWidget(self)
        calendar_end.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                border-radius: 10px;
                background-color: rgba(70, 70, 70, 100);
                color: rgba(200, 200, 200, 255);
                alternate-background-color: rgba(120, 120, 120, 255);
                selection-background-color: rgba(55, 159, 225, 255);
                selection-color: white;
                font-size: 14px;
            }

            QCalendarWidget QAbstractItemView:enabled:hover {
                background-color: rgba(60, 60, 60, 255);
            }
            """)
        calendar_end.setDateRange(QDate(1980, 1, 1), QDate.currentDate().addDays(-9))
        # calendar_end.setGeometry(270, 42, 190, 35)
        # self.end_date = QDateEdit(self, calendarPopup=True)
        self.end_date.setStyleSheet("""
                    QDateEdit::down-arrow {
                        image: url(WeatherViz/python/WeatherViz/assets/down_arrow.png);
                    }
                    
                    QDateEdit::drop-down {
                        background-color: rgba(70, 70, 70, 255);
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 20px;
                        border-left-width: 1px;
                        border-left-color: darkgray;
                        border-left-style: solid;
                        border-top-right-radius: 3px;
                        border-bottom-right-radius: 3px;
                    }
                    QDateEdit { background-color: rgba(55, 55, 55, 255);  border-radius: 3px; }""")
        self.end_date.setFixedSize(150 * UIRescale.Scale, 30 * UIRescale.Scale)
        self.end_date.setContentsMargins(0, 0, 20, 0)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumDate(QDate.currentDate())  # Change to correct minimum date
        self.end_date.setMaximumDate(QDate.currentDate().addDays(-9))
        self.end_date.setCalendarWidget(calendar_end)
        end_date_layout.addWidget(self.end_date)
        end_date_selector.setLayout(end_date_layout)

        layout.addWidget(start_date_selector)
        layout.addWidget(end_date_selector)

        self.start_date.dateChanged.connect(lambda: self.updateEndDate(self.start_date, self.end_date))
        self.setLayout(layout)

    def show_calendar(self):
        calendar_widget = QCalendarWidget(self)
        calendar_widget.setWindowFlags(calendar_widget.windowFlags() | Qt.Popup)
        calendar_button = self.sender()
        button_pos = calendar_button.mapToGlobal(calendar_button.rect().bottomLeft())
        calendar_widget.move(button_pos)
        calendar_widget.show()

    def updateEndDate(self, start_date, end_date):
        end_date.setMinimumDate(start_date.date())