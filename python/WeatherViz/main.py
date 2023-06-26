from PySide2.QtWidgets import QApplication, QLabel
import PySide2.QtWidgets

from .gui.mainwindow import MainWindow


def main():
    app = QApplication([])
    app.setStyle('Fusion')
    window = MainWindow()
    window.resize(1270, 850)
    window.setContentsMargins(0, 0, 0, 0)
    window.show()
    app.exec_()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
