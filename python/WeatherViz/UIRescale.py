from screeninfo import get_monitors

class UIRescale:
    Scale = get_monitors()[0].width / 1920

    def __init__(self):
        super().__init__()