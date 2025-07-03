from PySide2 import QtCore, QtGui, QtWidgets


class Style(QtWidgets.QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QtWidgets.QStyle.PrimitiveElement.PE_IndicatorItemViewItemDrop and widget:

            # drag and drop indicator to add clips to playlist
            mime_data_formats = widget.get_mime_data_formats()
            drop_position = widget.dropIndicatorPosition()
            if not mime_data_formats or mime_data_formats[0] != "rpa/playlists":
                if drop_position and drop_position in \
                    (QtWidgets.QAbstractItemView.AboveItem,
                     QtWidgets.QAbstractItemView.BelowItem):
                    return
                super().drawPrimitive(element, option, painter, widget)
                return

            # drag and drop indicator to move playlists within
            list_view = widget
            selected_index = list_view.get_selected_indexes()[0]
            moved_index = list_view.get_mindex_at_pos().row()
            if moved_index == -1:
                moved_index = list_view.model().rowCount() - 1
            offset = moved_index - selected_index

            viewport_pos = \
                list_view.viewport().mapFromGlobal(QtGui.QCursor.pos())

            prev_rect, next_rect = list_view.get_prev_next_rect()
            curr_rect = list_view.visualRect(list_view.get_mindex_at_pos())
            last_rect = list_view.visualRect(
                list_view.model().index(list_view.model().rowCount() - 1, 0))

            painter.save()
            try:
                pen = list_view.get_drop_indicator_pen()
                painter.setPen(pen)

                if next_rect.x() == 0 and next_rect.y() == 0:
                    painter.drawLine(
                        last_rect.bottomLeft(), last_rect.bottomRight())
                elif offset > 0 and \
                    (viewport_pos.y() >= next_rect.y() - 5) and \
                    (viewport_pos.y() < next_rect.y() + 5):
                    painter.drawLine(
                        next_rect.bottomLeft(), next_rect.bottomRight())
                elif offset > 0 and \
                    (viewport_pos.y() >= curr_rect.y()) and \
                    (viewport_pos.y() < curr_rect.y() + 5):
                    painter.drawLine(
                        curr_rect.bottomLeft(), curr_rect.bottomRight())
                elif offset > 0:
                    painter.drawLine(
                        option.rect.bottomLeft(), option.rect.bottomRight())
                elif offset < 0 and \
                    (viewport_pos.y() >= prev_rect.y() - 5) and \
                    (viewport_pos.y() < prev_rect.y() + 5):
                    painter.drawLine(
                        prev_rect.topLeft(), prev_rect.topRight())
                elif offset < 0:
                    painter.drawLine(
                        option.rect.topLeft(), option.rect.topRight())

            finally:
                painter.restore()

        else:
            super().drawPrimitive(element, option, painter, widget)
