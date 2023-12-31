from PySide2.QtWidgets import QApplication

from WeatherViz.UIRescale import UIRescale
from WeatherViz.gui.mainwindow import MainWindow
import sys

def main():

    app = QApplication(sys.argv + ['--no-sandbox'])
    app.setStyle('Fusion')
    window = MainWindow()
    window.resize(1500 * UIRescale.Scale, 850 * UIRescale.Scale)
    window.setContentsMargins(0, 0, 0, 0)
    window.show()
    app.exec_()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
