try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
from rpa.widgets.color_corrector.view.color_corrector import ColorCorrectionAndGrading
import rpa.widgets.color_corrector.view.resources.resources


class ColorCorrectorTabWidget(QtWidgets.QTabWidget):
    SIG_APPEND_TAB = QtCore.Signal(str)
    SIG_REORDER_TABS = QtCore.Signal(int, int)
    SIG_TAB_CLOSED = QtCore.Signal(str)
    SIG_TAB_RENAMED = QtCore.Signal(str, str)
    SIG_TAB_CHANGED = QtCore.Signal(str)

    def __init__(self, parent, slider_data):
        super().__init__(parent=parent)
        self.setTabBar(ColorCorrectTabBar(self))
        self.setTabsClosable(True)

        self.__slider_attrs = slider_data
        self.__clip_tab = ColorCorrectionAndGrading(None, "Clip", "clip", self.__slider_attrs)

        self.addTab(self.__clip_tab, "Clip")
        self.addTab(QtWidgets.QWidget(), "+")
        # We hide the close button for the first two tabs
        for i in range(2):
            self.tabBar().setTabButton(i, QtWidgets.QTabBar.RightSide, None)

        self.__curr_clip_id = None
        self.__id_to_tab = {}
        self.__is_all_mute = False
        self.__tabs = []
        self.__tabs.append(self.__clip_tab)

        self.currentChanged.connect(self.__on_current_changed)
        self.tabCloseRequested.connect(self.__on_tab_close)
        self.tabBar().SIG_TAB_MOVED.connect(self.__reorder_tabs)
        self.tabBar().SIG_TAB_RENAMED.connect(self.SIG_TAB_RENAMED)

    @property
    def clip_tab(self):
        return self.__clip_tab

    def is_all_mute(self):
        return self.__is_all_mute

    def get_tab(self, cc_id):
        return self.__id_to_tab.get(cc_id, None)

    def get_tabs(self):
        return self.__tabs

    def get_name(self, index):
        return str(self.tabBar().tabText(index))

    def set_name(self, tab, name):
        index = self.indexOf(tab)
        self.setTabText(index, name)
        tab.name = name

    def mute_all_tabs(self, mute):
        self.__is_all_mute = mute
        for index in range(self.count()):
            if self.tabText(index) == "+":
                continue
            widget = self.widget(index)
            widget.mute_all(mute)

    @QtCore.Slot(int)
    def __on_current_changed(self, index):
        if self.tabText(index) == "+":
            name = "Frame_cc" + str(index)
            self.SIG_APPEND_TAB.emit(name)
        else:
            tab = self.widget(index)
            if tab: self.SIG_TAB_CHANGED.emit(tab.id)

    @QtCore.Slot(int)
    def __on_tab_close(self, index):
        """
        We allow only closing of frame tabs in the UI and not clip tabs.
        """
        tab_to_remove = self.widget(index)
        self.SIG_TAB_CLOSED.emit(tab_to_remove.id)

    def __reorder_tabs(self, from_index, to_index):
        """ UI tabs are moved, we change the tabs order stored. """
        tab = self.__tabs.pop(from_index)
        self.__tabs.insert(to_index, tab)
        if tab.is_read_only():
            self.lock(tab)
        self.SIG_REORDER_TABS.emit(from_index, to_index)

    def move_tab(self, from_index, to_index):
        """ This is called when tab has been moved through API """
        self.blockSignals(True)
        tab = self.widget(from_index)
        self.removeTab(from_index)
        self.insertTab(to_index, tab, tab.name)
        self.setCurrentIndex(to_index)
        self.blockSignals(False)

    def update_clip_tab(self, new_id):
        if new_id is None:
            self.__clip_tab.reset()
            self.__curr_clip_id = None
            self.setCurrentIndex(0)
            return
        if self.__curr_clip_id in self.__id_to_tab:
            self.__id_to_tab.pop(self.__curr_clip_id)
        self.__id_to_tab[new_id] = self.__clip_tab
        self.__clip_tab.id = new_id
        self.__curr_clip_id = new_id
        self.setCurrentIndex(0)
        self.__clip_tab.clear_nodes()
        self.__clip_tab.clear_region()

    def append_tab(self, cc_id, name, type="frame"):
        tab = ColorCorrectionAndGrading(cc_id, name, type, self.__slider_attrs)
        if type == "clip":
            # We insert clip tabs in the beginning after the existing clip tab.
            index = self.tabBar().get_clip_tab_count()
            self.__tabs.insert(index, tab)
            self.tabBar().update_clip_tabs_count("+")
        else:
            index = self.count() - 1
            self.__tabs.append(tab)
        self.insertTab(index, tab, name)
        self.__id_to_tab[cc_id] = tab
        self.setCurrentIndex(index)
        return tab

    def delete_tab(self, cc_id):
        tab_to_remove = self.get_tab(cc_id)
        if tab_to_remove == self.__clip_tab: return
        if tab_to_remove.type == "clip":
            self.tabBar().update_clip_tabs_count("-")
        self.__tabs.remove(tab_to_remove)
        tab_to_remove.deleteLater()
        index = self.indexOf(tab_to_remove)
        del self.__id_to_tab[cc_id]
        self.setCurrentIndex(index-1)
        self.removeTab(index)

    def clear_all_tabs(self):
        self.setCurrentIndex(0)
        # We block the signals so we don't end up unnecessarily emitting
        # currentChanged signal on removeTab.
        self.blockSignals(True)
        for tab in reversed(self.__tabs):
            if not tab.id or tab.id == self.__curr_clip_id:
                continue
            index = self.indexOf(tab)
            self.removeTab(index)
            if tab.id in self.__id_to_tab: self.__id_to_tab.pop(tab.id)
        self.blockSignals(False)
        self.__tabs.clear()
        # We always retain the clip tab.
        self.__tabs.append(self.__clip_tab)
        self.update_clip_tab(None)
        self.tabBar().set_clip_tab_count(1)

    def lock(self, tab):
        index = self.indexOf(tab)
        # Remove the close button
        self.tabBar().setTabButton(index, QtWidgets.QTabBar.RightSide, None)
        self.tabBar().setTabIcon(index, QtGui.QIcon(QtGui.QPixmap(':lock.png')))
        tab.set_read_only(True)


class ColorCorrectTabBar(QtWidgets.QTabBar):
    """ QTabBar on double click, rename tab."""
    SIG_TAB_MOVED = QtCore.Signal(int, int)
    SIG_TAB_RENAMED = QtCore.Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.__edited_tab_index = -1
        self.__current_tab_name = None
        self.__editor = None
        self.setMovable(True)
        self.installEventFilter(self)
        self.tabMoved.connect(self.__tab_moved)
        self.__no_of_clip_tabs = 1

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Wheel:
            return True

        if event.type() == QtCore.QEvent.MouseMove:
            if source.currentIndex() < self.__no_of_clip_tabs:
                return True
            else:
                moving_leftEdge = event.pos().x() - self.__edge_offset_left
                moving_rightEdge = event.pos().x() + self.__edge_offset_right
                fixed_rightEdge = self.__get_clip_tab_widths()
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

    def set_clip_tab_count(self, value):
        self.__no_of_clip_tabs = value

    def get_clip_tab_count(self):
        return self.__no_of_clip_tabs

    def update_clip_tabs_count(self, calc):
        if calc == "+":
            self.__no_of_clip_tabs += 1
        if calc == "-":
            self.__no_of_clip_tabs -= 1

    def mousePressEvent(self, event):
        # We are doing this to avoid any other actions such as tabClose or tabMove or tabInsert
        # when the editor is open.
        if self.__editor: return
        else: super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.__editor: return
        tab_index = self.tabAt(event.pos())
        if tab_index < self.__no_of_clip_tabs or self.tabText(tab_index) == '+':
            return
        self.__start_rename(tab_index)

    def __get_clip_tab_widths(self):
        """ This get the clip tab width which we dont want to move.
        """
        width = 0
        for index in range(self.__no_of_clip_tabs):
            width = width + self.tabRect(index).width()
        return width

    def __get_tab_widths(self):
        """ This gets the width of the tabs excluding the "+" tab.
        """
        width = 0
        for index in range(self.count()-1):
            width = width + self.tabRect(index).width()
        return width

    def __start_rename(self, tab_index):
        widget = self.__parent.widget(tab_index)
        if widget.is_read_only(): return
        rect = self.tabRect(tab_index)
        self.__editor = QtWidgets.QLineEdit(self.tabText(tab_index), self)
        self.__editor.setGeometry(rect)
        self.__editor.show()
        self.__editor.selectAll()
        self.__editor.setFocus()
        self.__editor.returnPressed.connect(self.__finish_rename)
        self.__editor.editingFinished.connect(self.__finish_rename)

        self.__current_tab_name = self.tabText(tab_index)
        self.__edited_tab_index = tab_index

        # Prevent tab movement and tab closing
        self.setMovable(False)
        for i in range(self.count()):
            if self.tabButton(i, QtWidgets.QTabBar.RightSide):
                self.tabButton(i, QtWidgets.QTabBar.RightSide).setEnabled(False)

    @QtCore.Slot(int, int)
    def __tab_moved(self, from_index, to_index):
        if from_index >= self.__no_of_clip_tabs and to_index >= self.__no_of_clip_tabs:
            self.SIG_TAB_MOVED.emit(from_index, to_index)

    @QtCore.Slot()
    def __finish_rename(self):
        if not self.__editor: return
        new_name = self.__editor.text().strip()
        if not new_name: new_name = self.__current_tab_name
        self.setTabText(self.__edited_tab_index, new_name)
        widget = self.__parent.widget(self.__edited_tab_index)
        widget.name = new_name
        self.SIG_TAB_RENAMED.emit(widget.id, new_name)
        self.__clean_up_editor()

    def __clean_up_editor(self):
        self.__editor.deleteLater()
        self.__editor = None
        self.__edited_tab_index = -1
        self.__current_tab_name = None
        self.setMovable(True)
        for i in range(self.count()):
            if self.tabButton(i, QtWidgets.QTabBar.RightSide):
                self.tabButton(i, QtWidgets.QTabBar.RightSide).setEnabled(True)
