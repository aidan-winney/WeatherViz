from PyQt5.QtWidgets import QApplication, QLabel
from gui.mainwindow import MainWindow
import PyQt5.QtWidgets


def main():
    app = QApplication([])
    app.setStyle('Fusion')
    window = MainWindow()
    #window.display()
    window.resize(1250, 750)
    window.show()
    app.exec()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
