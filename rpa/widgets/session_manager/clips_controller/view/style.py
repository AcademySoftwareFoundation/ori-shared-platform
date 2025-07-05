try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets

class Style(QtWidgets.QProxyStyle):
    def __init__(self):
        super().__init__()

    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QtWidgets.QStyle.PrimitiveElement.PE_IndicatorItemViewItemDrop and widget:
            table_view = widget
            mindex = table_view.indexAt(option.rect.topLeft())
            rect = table_view.visualRect(mindex)
            rect.setLeft(table_view.viewport().rect().left())
            rect_width = sum(table_view.columnWidth(col) for \
                         col in range(table_view.model().columnCount()))
            rect.setRight(rect_width)

            last_rect = table_view.visualRect(
                table_view.model().index(table_view.model().rowCount() - 1, 0))
            last_rect.setLeft(table_view.viewport().rect().left())
            last_rect.setRight(rect_width)

            selected_indexes = sorted(table_view.get_selected_indexes())
            moved_index = table_view.get_mindex_at_pos().row()

            offset = 0
            if selected_indexes:
                offset = moved_index - selected_indexes[0]

            painter.save()

            try:
                painter.setPen(table_view.get_drop_indicator_pen())
                if moved_index == -1:
                    painter.drawLine(last_rect.bottomLeft(), last_rect.bottomRight())
                elif offset < 0:
                    painter.drawLine(rect.topLeft(), rect.topRight())
                elif offset > 0:
                    painter.drawLine(rect.bottomLeft(), rect.bottomRight())
            finally:
                painter.restore()

        else:
            super().drawPrimitive(element, option, painter, widget)
