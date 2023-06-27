from PySide2.QtCore import QThread, Signal

class Worker(QThread):
    updateProgress = Signal(int)
    def __init__(self, target=None):
        super().__init__()
        self.target = target

    def run(self):
        if self.target:
            self.target()