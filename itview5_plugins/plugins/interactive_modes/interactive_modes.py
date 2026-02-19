from PySide2 import QtCore
from rpa.widgets.interactive_modes.interactive_modes import InteractiveModes as RpaInteractiveModes


class InteractiveModes(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__interactive_modes = RpaInteractiveModes(self.__rpa, self.__main_window)
        self.__interactive_modes.pen_mode.setToolTip("Pen (Ctrl)")
        self.__interactive_modes.line_mode.setToolTip("Line (Ctrl + Alt)")
        self.__interactive_modes.multi_line_mode.setToolTip("Multi Line (Ctrl + Meta)")
        self.__interactive_modes.hard_eraser_mode.setToolTip("Hard Eraser (Ctrl + Shift)")
