try:
    from PySide2 import QtCore
except:
    from PySide6 import QtCore
from itview.core.sub_progress_bar_tx.api.session_api_tx \
    import SessionApiTx
from itview.core.sub_progress_bar_tx.api.annotation_api_tx \
    import AnnotationApiTx


class SubProgressBarTx(QtCore.QObject):

    def __init__(self, rpc, rpa):
        super().__init__()
        self.__session_api = SessionApiTx(rpc, rpa.session_api)
        self.__annotation_api = AnnotationApiTx(rpc, rpa.annotation_api)