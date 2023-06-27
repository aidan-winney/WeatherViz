from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider

class DateRangeSlider(QWidget):
    def __init__(self, start_date, end_date, parent=None):
        super(DateRangeSlider, self).__init__(parent)

        self.start_date = start_date.date()
        self.end_date = end_date.date()

        date_range = self.end_date.toJulianDay() - self.start_date.toJulianDay()

        layout = QVBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, date_range)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.update_date_label)

        self.date_label = QLabel()
        # self.date_label.setMargin(0)
        # self.date_label.setContentsMargins(0, 0, 1, 0)
        self.date_label.setStyleSheet("background-color: rgba(90, 90, 90, 0); font-weight: bold; color: white")
        self.update_date_label()
        layout.addWidget(self.date_label)
        layout.addWidget(self.slider)

        self.setLayout(layout)

    def update_range(self, start_date, end_date):
        self.start_date = start_date.date()
        self.end_date = end_date.date()
        date_range = self.end_date.toJulianDay() - self.start_date.toJulianDay()
        self.slider.setRange(0, date_range)
        self.date_label.setText(f"Date: {self.start_date.toString('yyyy-MM-dd')}")

    def get_slider(self):
        return self.slider

    def update_date_label(self):
        current_date = self.start_date.addDays(self.slider.value())
        self.date_label.setText(f"Date: {current_date.toString('yyyy-MM-dd')}")