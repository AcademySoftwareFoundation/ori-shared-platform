try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets


class NonHideQMenu(QtWidgets.QMenu):

    def mouseReleaseEvent(self, event):
        action = self.activeAction()
        if action and action.isEnabled():
            action.setEnabled(False)
            super(NonHideQMenu, self).mouseReleaseEvent(event)
            action.setEnabled(True)
            action.trigger()
        else:
            super(NonHideQMenu, self).mouseReleaseEvent(event)