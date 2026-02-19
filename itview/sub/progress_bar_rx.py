from itview.sub.progress_bar import ProgressBar


class ProgressBarRx:
    def __init__(self, main_window):
        self.__main_window = main_window
        self.__progress_bar = ProgressBar(self.__main_window)

    def init(self, window_title, label, maximum):
        if self.__progress_bar is not None:
            self.hide()
        self.__progress_bar = ProgressBar(self.__main_window)
        self.__progress_bar.init(window_title, label, maximum)

    def update(self, window_title, label, value, maximum):
        if self.__progress_bar is None:
            self.init(window_title, label, maximum)
        is_in_progress = self.__progress_bar.update(
            window_title, label, value, maximum)
        if not is_in_progress:
            self.hide()

    def hide(self):
        self.__progress_bar.close()
        self.__progress_bar.deleteLater()
        self.__progress_bar = None
