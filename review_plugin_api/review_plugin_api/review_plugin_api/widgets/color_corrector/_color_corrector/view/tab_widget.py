from PySide2 import QtCore, QtGui, QtWidgets
from review_plugin_api.widgets.color_corrector._color_corrector.view.color_corrector \
    import RegionTab, ColorCorrectionAndGrading
from review_plugin_api.widgets.color_corrector._color_corrector.model import TabType


class ColorCorrectorTabWidget(QtWidgets.QTabWidget):
    SIG_REGION_CREATED = QtCore.Signal(object)
    SIG_REGION_TAB_CREATED = QtCore.Signal(object)
    SIG_REGION_TAB_CLOSED = QtCore.Signal(object)
    SIG_REORDER_REGIONS = QtCore.Signal(int, int)

    def __init__(self, parent, slider_data):
        super().__init__(parent=parent)
        self.setTabBar(ColorCorrectTabBar(self))
        self.setTabsClosable(True)

        self.__slider_attrs = slider_data
        self.__clip_tab = ColorCorrectionAndGrading(self.__slider_attrs)
        self.__frame_tab = ColorCorrectionAndGrading(self.__slider_attrs)
        self.__region_tabs = []

        self.addTab(self.__clip_tab, TabType.CLIP.value)
        self.addTab(self.__frame_tab, TabType.FRAME.value)
        self.addTab(QtWidgets.QWidget(), "+")

        # We hide the close button for the first three tabs
        for i in range(3):
            self.tabBar().setTabButton(i, QtWidgets.QTabBar.RightSide, None)

        self.currentChanged.connect(self.on_current_changed)
        self.tabCloseRequested.connect(self.on_tab_close)

        self.tabBar().SIG_TAB_MOVED.connect(self.__tab_moved)

    @property
    def clip_tab(self):
        return self.__clip_tab

    @property
    def frame_tab(self):
        return self.__frame_tab

    @property
    def current_tab_name(self):
        return str(self.tabBar().tabText(self.currentIndex()))

    @QtCore.Slot(bool)
    def mute_all_tabs(self, mute):
        for index in range(self.count()):
            if self.tabText(index) == "+":
                continue
            widget = self.widget(index)
            widget.mute_all(mute)

    @QtCore.Slot(int)
    def on_current_changed(self, index):
        if self.tabText(index) == "+":
            self.append_tab(index=index)
            self.SIG_REGION_CREATED.emit(self.currentWidget())
        elif index >= 2:
            region = self.currentWidget()

    def append_tab(self, index=None):
        if not index: index = self.count()-1
        name = "Region" + str(index - 1)
        region_tab = RegionTab(self.__slider_attrs, name=name)
        self.insertTab(index, region_tab, name)
        self.setCurrentIndex(index)
        self.__region_tabs.append(region_tab)
        self.SIG_REGION_TAB_CREATED.emit(region_tab)

    def remove_region_tabs(self):
        for region_tab in self.__region_tabs:
            index = self.indexOf(region_tab)
            self.setCurrentIndex(index-1)
            self.removeTab(index)
        self.__region_tabs = []

    def remove_tab(self, tab):
        index = self.indexOf(tab)
        self.setCurrentIndex(0)
        self.removeTab(index)

    def __tab_moved(self, from_index, to_index):
        self.SIG_REORDER_REGIONS.emit(from_index, to_index)

    @QtCore.Slot(int)
    def on_tab_close(self, index):
        tab_to_remove = self.widget(index)
        self.SIG_REGION_TAB_CLOSED.emit(tab_to_remove)
        self.__region_tabs.remove(tab_to_remove)
        tab_to_remove.deleteLater()
        self.setCurrentIndex(index-1)
        self.removeTab(index)


class ColorCorrectTabBar(QtWidgets.QTabBar):
    """ QTabBar on double click, rename tab."""
    SIG_TAB_MOVED = QtCore.Signal(int, int)
    SIG_RENAME_TAB = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.setMovable(True)
        self.installEventFilter(self)
        self.tabMoved.connect(self.__tab_moved)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Wheel:
            return True

        if event.type() == QtCore.QEvent.MouseMove:
            if source.currentIndex() in (0, 1):
                return True
            else:
                moving_leftEdge = event.pos().x() - self.__edge_offset_left
                moving_rightEdge = event.pos().x() + self.__edge_offset_right
                fixed_rightEdge = self.tabRect(0).width() + self.tabRect(1).width()
                if moving_leftEdge < fixed_rightEdge:
                    return True
                if moving_rightEdge > self.__width:
                    return True

        elif event.type() == QtCore.QEvent.Type.MouseButtonPress:
            # Get mouse click horizontal position.
            x_click = event.pos().x()
            # Get the left and right edge horizontal position of the targeted tab.
            x_left = self.tabRect(self.tabAt(event.pos())).x()
            x_right = self.tabRect(self.tabAt(event.pos())).right()
            # Compute and store offset between mouse click horizontal
            # position and the left edgeand right edge of the targeted tab.
            self.__edge_offset_left = x_click - x_left
            self.__edge_offset_right = x_right - x_click
            self.__width = self.__get_tab_widths()

        return super().eventFilter(source, event)

    def mouseDoubleClickEvent(self, event):
        tab_index = self.tabAt(event.pos())
        if tab_index < 2 or self.tabText(tab_index) == '+':
            return
        self.__start_rename(tab_index)

    def __get_tab_widths(self):
        width = 0
        for index in range(self.count()-1):
            tab_rect = self.tabRect(index)
            width = width + tab_rect.width()
        return width

    def __start_rename(self, tab_index):
        self.__edited_tab = tab_index
        rect = self.tabRect(tab_index)
        top_margin = 3
        left_margin = 6
        self.__edit = QtWidgets.QLineEdit(self)
        self.__edit.show()
        self.__edit.move(rect.left() + left_margin, rect.top() + top_margin)
        self.__edit.resize(rect.width() - 2 * left_margin, rect.height() - 2 * top_margin)
        self.__edit.setText(self.tabText(tab_index))
        self.__edit.editingFinished.connect(self.__finish_rename)

    @QtCore.Slot(int, int)
    def __tab_moved(self, from_index, to_index):
        if from_index >= 2 and to_index >= 2:
            self.SIG_TAB_MOVED.emit(from_index, to_index)

    @QtCore.Slot()
    def __finish_rename(self):
        new_name = self.__edit.text().strip()
        self.setTabText(self.__edited_tab, new_name)
        self.__parent.widget(self.__edited_tab).set_name = new_name
        self.__edit.deleteLater()