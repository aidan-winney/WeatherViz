from PySide2.QtCore import QRect
from PySide2.QtGui import Qt, QPainter, QColor
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider

class DateRangeSlider(QWidget):
    def __init__(self, start_date, end_date, parent=None):
        super(DateRangeSlider, self).__init__(parent)

        self.start_date = start_date.date()
        self.end_date = end_date.date()
        self.daily = True
        date_range = self.end_date.toJulianDay() - self.start_date.toJulianDay()

        layout = QVBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, date_range)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setStyleSheet("""
                    QSlider {
                        background: transparent;
                    }

                    QSlider::groove:horizontal {
                        background: rgba(90, 90, 90, 120);
                        height: 5px;
                        border-radius: 20px;
                    }

                    QSlider::handle:horizontal {
                        background: white;
                        width: 15px;
                        margin: -5px 0;
                        border-radius: 5px;
                    }
                    QSlider::sub-page:horizontal {
                        background: rgba(55, 159, 225, 255);
                    }
                    QSlider::add-page:horizontal {
                        background: lightgray;
                    }
                    QSlider::tick:horizontal {
                        background: green;
                        width: 5px;
                    }
                """)
        self.slider.valueChanged.connect(self.update_date_label)

        self.date_label = QLabel()
        # self.date_label.setMargin(0)
        self.date_label.setContentsMargins(0, 0, 0, 0)
        self.date_label.setStyleSheet("background-color: rgba(90, 90, 90, 0); font-weight: bold; color: white")
        self.update_date_label()
        layout.addWidget(self.date_label)
        layout.addWidget(self.slider)

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(90, 90, 90))

        # Set green color for tick marks
        painter.setBrush(Qt.NoBrush)

        if self.slider.maximum() > 0:
            tick_width = self.width() / (self.slider.maximum() - self.slider.minimum())
            for tick in range(self.slider.minimum(), self.slider.maximum() + 1):
                x = tick * tick_width
                rect = QRect(x + 15, self.height() - 10, 2, 7)
                painter.drawRoundedRect(rect, 1, 1)

        super().paintEvent(event)

    def update(self):
        self.repaint()

    def update_range(self, start_date, end_date, daily):
        self.start_date = start_date
        self.end_date = end_date
        self.daily = daily
        date_range = self.end_date.toJulianDay() - self.start_date.toJulianDay()
        if self.daily is False:
            date_range = (date_range + 1) * 24 - 1
        self.slider.setRange(0, date_range)
        self.slider.setValue(0)
        self.update_date_label()

    def get_slider(self):
        return self.slider

    def update_date_label(self):
        if self.daily:
            current_date = self.start_date.addDays(self.slider.value())
            self.date_label.setText(f"Date: {current_date.toString('yyyy-MM-dd')}")
        else:
            current_date = self.start_date.addDays(self.slider.value()//24)
            current_time = self.slider.value() % 24
            self.date_label.setText(f"Date: {current_date.toString('yyyy-MM-dd')} {current_time}:00 EST")