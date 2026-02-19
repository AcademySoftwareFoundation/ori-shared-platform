class AnnotationApiTx:

    def __init__(self, rpc, rpa):
        self.__rpc = rpc
        self.__rpa = rpa

        self.__rpa.PRG_ANNO_LOADING_STARTED.connect(
            self.__anno_load_started)
        self.__rpa.PRG_ANNO_LOADED.connect(self.__anno_loaded)
        self.__rpa.PRG_ANNO_LOADING_COMPLETED.connect(
            self.__hide_progress_bar)

        self.__rpa.PRG_ANNO_DELETION_STARTED.connect(
            self.__anno_deletion_started)
        self.__rpa.PRG_ANNO_DELETED.connect(self.__anno_deleted)
        self.__rpa.PRG_ANNO_DELETION_COMPLETED.connect(
            self.__hide_progress_bar)

    def __anno_load_started(self, num_of_clips):
        self.__rpc.rpc.progress_bar_rx.init(
            "Annotation loading in Progress...", "Loading...",
            num_of_clips)

    def __anno_loaded(
        self, num_of_clips_loaded, num_of_clips_to_load):
        self.__rpc.rpc.progress_bar_rx.update(
            "Annotation loading in Progress...", "Loading...",
            num_of_clips_loaded, num_of_clips_to_load)

    def __anno_deletion_started(self, num_of_clips_to_delete):
        self.__rpc.rpc.progress_bar_rx.init(
            "Annotation Deletion in Progress...", "Deleting Annotations...",
            num_of_clips_to_delete)

    def __anno_deleted(self, num_of_clips_deleted, num_of_clips_to_delete):
        self.__rpc.rpc.progress_bar_rx.update(
            "Annotation Deletion in Progress...", "Deleting Annotations...",
            num_of_clips_deleted, num_of_clips_to_delete)

    def __hide_progress_bar(self):
        self.__rpc.rpc.progress_bar_rx.hide()




