import time

from PySide2.QtCore import QObject, QUrl, QByteArray, Qt
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide2.QtGui import QImage, QPixmap, QColor

class ThumbnailLoader(QObject):
    def __init__(self):
        super(ThumbnailLoader, self).__init__()
        self.manager = QNetworkAccessManager()
        self.__cache = {}
        self.responses = {}
        self.pending = 0

    def request_thumbnail(self, urls, callback):
        try:
            [url, alt_url] = urls
        except ValueError as e:
            return "N/A"
        if url in self.__cache or alt_url in self.__cache:
            return self.__cache.get(url) or self.__cache.get(alt_url)
        network_req = QNetworkRequest(QUrl(url))
        reply = self.manager.get(network_req)
        reply.ignoreSslErrors()
        reply.finished.connect(lambda: self.handle_reply(reply, url, alt_url, callback))
        return None

    def handle_reply(self, reply, url, alt_url, callback):
        if reply.error():
            if not alt_url:
                self.__cache[url] = "N/A"
            else:
                self.request_thumbnail([alt_url, None], callback)
        else:
            image_data = QByteArray(reply.readAll())
            image = QImage()
            image.loadFromData(image_data)
            if image.isNull():
                pixmap = "N/A"
            else:
                pixmap = QPixmap.fromImage(image)
            self.__cache[url] = pixmap
        callback(self.__cache[url])
