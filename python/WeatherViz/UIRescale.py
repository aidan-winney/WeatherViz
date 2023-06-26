from screeninfo import get_monitors

class UIRescale:
    Scale = 3140 // get_monitors()[0].width

    def __init__(self):
        super().__init__()