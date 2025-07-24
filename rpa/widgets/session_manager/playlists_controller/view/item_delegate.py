try:
    from PySide2 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtGui, QtCore


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

    def paint(self, painter, option, index):
        # if option.state & QtWidgets.QStyle.State_Selected:
        #     painter.fillRect(option.rect, option.palette.highlight())

        is_fg = index.model().get_fg_index() == index
        is_bg = index.model().get_bg_index() == index
        is_selected = index in option.widget.get_selected_mindexes()
        if is_selected:
            painter.fillRect(option.rect, option.palette.highlight())
        # Create a small margin for the items on the left,
        # and remove the margin on the right edge so the
        # "playlist" color bleeds into the dark gray of the
        # splitter.
        offset = 5 if is_fg else 0
        r = option.rect
        r.setLeft(r.left() + offset)

        # # Strip out selected and focus state when painting
        # old_state = option.state
        option.state = option.state & ~QtWidgets.QStyle.State_Selected
        option.state = option.state & ~QtWidgets.QStyle.State_HasFocus

        super().paint(painter, option, index)

        # option.state = old_state

        painter.save()
        try:
            # Draw an outline to make it look tab-like.
            if is_fg:
                painter.setPen(QtGui.QPen(
                    QtGui.QBrush(QtGui.QColor(200, 150, 150, 255)), 2))
            elif is_bg:
                painter.setPen(QtGui.QPen(
                    QtGui.QBrush(QtGui.QColor(100, 150, 250, 255)), 2))
            else:
                painter.setPen(QtGui.QPen(option.palette.shadow().color(), 1))

            painter.drawLine(r.topLeft(), r.topRight())

            painter.drawLine(
                r.bottomLeft() + QtCore.QPoint(0, 1),
                r.bottomRight() + QtCore.QPoint(0, 1))

            painter.drawLine(
                r.bottomLeft() + QtCore.QPoint(-1, 0),
                r.topLeft() + QtCore.QPoint(-1, 1))

            if not is_fg:
                painter.drawLine(r.bottomRight(), r.topRight())

            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))

            painter.drawLine(
                r.bottomLeft() + QtCore.QPoint(2, 2),
                r.bottomRight() + QtCore.QPoint(0, 2))

        finally:
            painter.restore()
