import os
from PySide2 import QtCore, QtGui, QtNetwork, QtWebEngineCore, QtWebEngineWidgets, QtWebChannel


class WebView(QtWebEngineWidgets.QWebEngineView):

    SIG_CONTEXT_MENU = QtCore.Signal(str)
    SIG_JTS_IDS_SELECTED = QtCore.Signal(list)
    SIG_ADD_SELECTED_JTS = QtCore.Signal(list)

    def __init__(self, parent):
        super().__init__(parent)

        self.__web_channel = QtWebChannel.QWebChannel()

        self.__event_handler = JsEventHandler()
        self.__event_handler.SIG_CONTEXT_MENU.connect(self.SIG_CONTEXT_MENU)
        self.__event_handler.SIG_JTS_IDS_SELECTED.connect(self.SIG_JTS_IDS_SELECTED)
        self.__event_handler.SIG_ADD_SELECTED_JTS.connect(self.SIG_ADD_SELECTED_JTS)
        self.__web_channel.registerObject('webChannel', self.__event_handler)

        self.__create_unique_profile()

        self.page().setBackgroundColor(QtGui.QColor("#3b3b3b"))

    def __create_unique_profile(self):
        profile_number = Counter.get_instance().get_count()

        self.__web_profile = \
            QtWebEngineWidgets.QWebEngineProfile(
                f'webEngineProfile_{profile_number}', self)
        cache_dir = \
            f"/tmp/webengine-cache{profile_number}-" + os.getenv("USER", "unknown")
        self.__web_profile.setCachePath(cache_dir)
        self.__web_engine_page = \
            QtWebEngineWidgets.QWebEnginePage(self.__web_profile, self)
        self.__web_engine_page.setWebChannel(self.__web_channel)
        self.setPage(self.__web_engine_page)

    def clean_up(self):
        # self.setPage(None)
        # self.__web_engine_page.deleteLater()

        self.setParent(None)
        self.page().deleteLater()
        self.deleteLater()

        self.__web_profile.setParent(None)
        self.__web_profile.deleteLater()


class JsEventHandler(QtCore.QObject):

    SIG_CONTEXT_MENU = QtCore.Signal(str)
    SIG_JTS_IDS_SELECTED = QtCore.Signal(list)
    SIG_ADD_SELECTED_JTS = QtCore.Signal(list)

    @QtCore.Slot(list)
    def assignSelected(self, selected):
        self.SIG_JTS_IDS_SELECTED.emit(selected)

    @QtCore.Slot(str)
    def handleContextMenu(self, category):
        self.SIG_CONTEXT_MENU.emit(category)

    @QtCore.Slot(list)
    def handleClick(self, data):
        pass

    @QtCore.Slot(list)
    def handleDoubleClick(self, selected):
        self.SIG_ADD_SELECTED_JTS.emit(selected)

    @QtCore.Slot(str)
    def handleMouseDown(self, data):
        pass

    @QtCore.Slot(str)
    def handleMouseMove(self, data):
        pass

    @QtCore.Slot(str)
    def handleMouseUp(self, data):
        pass

    @QtCore.Slot()
    def handleMouseLeave(self):
        pass

class Counter:
    __instance = None

    @classmethod
    def get_instance(cls):
        """Returns the sigleton instance of ActionsHeader"""
        if cls.__instance is None:
            cls.__instance = Counter()
        return cls.__instance

    def __init__(self):
        if Counter.__instance is not None:
            raise Exception("Singleton! Use get_instance to get instance!")
        Counter.__instance = self
        self.__count = 1

    def get_count(self):
        cur_count = self.__count
        self.__count += 1
        return cur_count
