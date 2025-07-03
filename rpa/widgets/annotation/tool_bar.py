from PySide2 import QtCore, QtWidgets


class ToolBar(QtWidgets.QToolBar):
    SIG_TEXT_LINE_EDIT_VISIBILITY_CHANGED = QtCore.Signal(bool)

    def __init__(self, actions, annotation_api, pen_width, eraser_width, text_size):
        super().__init__()
        self.__actions = actions
        self.__annotation_api = annotation_api

        self.setWindowTitle("Annotation Toolbar")
        self.setObjectName(self.windowTitle())

        self.addSeparator()

        self.addAction(self.__actions.color)

        self.addSeparator()

        self.addAction(self.__actions.show_annotations)
        self.addAction(self.__actions.cut_annotations)
        self.addAction(self.__actions.copy_annotations)
        self.addAction(self.__actions.paste_annotations)

        self.addSeparator()

        self.__draw_size_menu = QtWidgets.QMenu()
        for action in self.__actions.draw_sizes.values():
            self.__draw_size_menu.addAction(action)
        self.__draw_size_button = QtWidgets.QToolButton()
        self.__draw_size_button.setToolTip("Draw Size")
        self.__draw_size_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.__draw_size_button.setMenu(self.__draw_size_menu)
        self.addWidget(self.__draw_size_button)
        self.__draw_size_button.setIcon(
            self.__actions.draw_sizes[pen_width].icon())
        self.__actions.SIG_DRAW_SIZE_CHANGED.connect(
            lambda action: self.__draw_size_button.setIcon(action.icon()))

        self.__eraser_size_menu = QtWidgets.QMenu()
        for action in self.__actions.eraser_sizes.values():
            self.__eraser_size_menu.addAction(action)
        self.__eraser_size_button = QtWidgets.QToolButton()
        self.__eraser_size_button.setToolTip("Eraser Size")
        self.__eraser_size_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.__eraser_size_button.setMenu(self.__eraser_size_menu)
        self.addWidget(self.__eraser_size_button)
        self.__eraser_size_button.setIcon(
            self.__actions.eraser_sizes[eraser_width].icon())
        self.__actions.SIG_ERASER_SIZE_CHANGED.connect(
            lambda action: self.__eraser_size_button.setIcon(action.icon()))

        self.__text_size_menu = QtWidgets.QMenu()
        for action in self.__actions.text_sizes.values():
            self.__text_size_menu.addAction(action)
        self.__text_size_button = QtWidgets.QToolButton()
        self.__text_size_button.setToolTip("Text Size")
        self.__text_size_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.__text_size_button.setMenu(self.__text_size_menu)
        self.addWidget(self.__text_size_button)
        self.__text_size_button.setIcon(
            self.__actions.text_sizes[text_size].icon())
        self.__actions.SIG_TEXT_SIZE_CHANGED.connect(
            lambda action: self.__text_size_button.setIcon(action.icon()))

        self.addSeparator()
        self.addAction(self.__actions.prev_annot_frame)
        self.addAction(self.__actions.next_annot_frame)
        self.addSeparator()
        self.addAction(self.__actions.undo)
        self.addAction(self.__actions.redo)
        self.addSeparator()
