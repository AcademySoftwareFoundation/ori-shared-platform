from PySide2 import QtCore, QtGui, QtWidgets


class SuppressEscMixin(object):
    def event(self, e):
        if e.type() == QtCore.QEvent.ShortcutOverride:
            if e.key() == QtCore.Qt.Key_Escape:
                # yes, override accel, escape should cancel edit
                e.accept()
                return True

        return super(SuppressEscMixin, self).event(e)


class SuppressEscLineEdit(SuppressEscMixin, QtWidgets.QLineEdit):
    pass


class TimelineLineEdit(SuppressEscLineEdit):
    def __init__(self, context_menu_actions, cancelf, *args):
        SuppressEscLineEdit.__init__(self, *args)
        self.__context_menu_actions = context_menu_actions
        self.__cancelf = cancelf

    def set_width_mode(self, display_text):
        self.setMaximumWidth(self.fontMetrics().horizontalAdvance(display_text))

    def set_tool_tip_mode(self, tool_tip_text):
        self.setToolTip('{} {}'.format(self.toolTip().split(' ')[0], tool_tip_text))


    def contextMenuEvent(self, event):
        """Prepend to the top of the standard context menu the
        requested actions, separated with a separator.

        """
        menu = self.createStandardContextMenu()

        # Handle the menu not having any visible actions.
        if menu.isEmpty():
            first_standard_action = None
        else:
            first_standard_action = menu.actions()[0]
        for action in self.__context_menu_actions:
            if action == 'separator':
                menu.insertSeparator(first_standard_action)
            else:
                menu.insertAction(first_standard_action, action)
        if first_standard_action:
            menu.insertSeparator(first_standard_action)

        # While 'menu' at the C++ level has 'self' as its parent,
        # unless the parent it set again at the Python level, the menu
        # will be GCed at the end of this method.
        menu.setParent(self)
        menu.popup(event.globalPos())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            event.accept()
            if self.__cancelf is not None:
                self.__cancelf()
            return
        super(TimelineLineEdit, self).keyPressEvent(event)
