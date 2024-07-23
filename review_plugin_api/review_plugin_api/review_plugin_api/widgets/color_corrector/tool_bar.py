from PySide2 import QtCore, QtWidgets
from review_plugin_api.widgets.color_corrector import constants as C



class ToolBar(QtWidgets.QToolBar):

    def __init__(self, actions):
        super().__init__()
        self.__actions = actions

        self.setWindowTitle("Annotation")
        self.setObjectName("Annotation")

        self.addSeparator()

        self.addAction(self.__actions.toggle_rectangle_mode)
        self.addAction(self.__actions.toggle_ellipse_mode)
        self.addAction(self.__actions.toggle_lasso_mode)

        self.addSeparator()
