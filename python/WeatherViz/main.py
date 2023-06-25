from PySide2.QtWidgets import QApplication, QLabel
from .gui.mainwindow import MainWindow
import PySide2.QtWidgets


def main():
    app = QApplication([])
    app.setStyle('Fusion')
    window = MainWindow()
    #window.display()
    window.resize(1250, 750)
    window.show()
    app.exec_()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
