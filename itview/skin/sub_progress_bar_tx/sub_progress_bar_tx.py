from PySide2 import QtCore
# from itview.skin.sub_progress_bar_tx.api.clip_attr_api_tx \
#     import ClipAttrApiTx


class SubProgressBarTx(QtCore.QObject):

    def __init__(self, rpc, rpa):
        super().__init__()
        # self.__clip_attr_api = ClipAttrApiTx(rpc, rpa.clip_attr_api)
