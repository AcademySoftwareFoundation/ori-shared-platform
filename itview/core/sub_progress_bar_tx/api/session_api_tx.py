class SessionApiTx:

    def __init__(self, rpc, rpa):
        self.__rpc = rpc
        self.__rpa = rpa

        self.__rpa.PRG_CLIPS_CREATION_STARTED.connect(
            self.__clips_cretation_started)
        self.__rpa.PRG_CLIP_CREATED.connect(self.__clip_created)
        self.__rpa.PRG_CLIPS_CREATION_COMPLETED.connect(
            self.__hide_progress_bar)

        self.__rpa.PRG_CLIPS_DELETION_STARTED.connect(
            self.__clips_deletion_started)
        self.__rpa.PRG_CLIP_DELETED.connect(self.__clip_deleted)
        self.__rpa.PRG_CLIPS_DELETION_COMPLETED.connect(
            self.__hide_progress_bar)

        self.__rpa.PRG_GET_ATTR_VALUES_STARTED.connect(
            self.__get_attr_values_started)
        self.__rpa.PRG_GOT_ATTR_VALUE.connect(
            self.__got_attr_value)
        self.__rpa.PRG_GET_ATTR_VALUES_COMPLETED.connect(
            self.__hide_progress_bar)

        self.__rpa.PRG_SET_ATTR_VALUES_STARTED.connect(
            self.__set_attr_values_started)
        self.__rpa.PRG_SET_ATTR_VALUE.connect(
            self.__set_attr_value)
        self.__rpa.PRG_SET_ATTR_VALUES_COMPLETED.connect(
            self.__hide_progress_bar)

    def __clips_cretation_started(self, num_of_clips):
        self.__rpc.rpc.progress_bar_rx.init(
            "Clip Creation in Progress...", "Creating Clips...",
            num_of_clips)

    def __clip_created(
        self, num_of_clips_created, num_of_clips_to_create):
        self.__rpc.rpc.progress_bar_rx.update(
            "Clip Creation in Progress...", "Creating Clips...",
            num_of_clips_created, num_of_clips_to_create)

    def __clips_deletion_started(self, num_of_clips_to_delete):
        self.__rpc.rpc.progress_bar_rx.init(
            "Clip Deletion in Progress...", "Deleting Clips...",
            num_of_clips_to_delete)

    def __clip_deleted(self, num_of_clips_deleted, num_of_clips_to_delete):
        self.__rpc.rpc.progress_bar_rx.update(
            "Clip Deletion in Progress...", "Deleting Clips...",
            num_of_clips_deleted, num_of_clips_to_delete)

    def __get_attr_values_started(self, total_cnt):
        self.__rpc.rpc.progress_bar_rx.init(
            "Getting attr values in Progress...",
            "Getting attr values:", total_cnt)

    def __got_attr_value(
        self, progress_cnt, total_cnt):
        self.__rpc.rpc.progress_bar_rx.update(
            "Getting attr values in Progress...",
            "Getting attr values:", progress_cnt, total_cnt)

    def __set_attr_values_started(self, total_cnt):
        self.__rpc.rpc.progress_bar_rx.init(
            "Setting attr values in Progress...",
            "Setting attr values:", total_cnt)

    def __set_attr_value(
        self, progress_cnt, total_cnt):
        self.__rpc.rpc.progress_bar_rx.update(
            "Setting attr values in Progress...",
            "Setting attr values:", progress_cnt, total_cnt)

    def __hide_progress_bar(self):
        self.__rpc.rpc.progress_bar_rx.hide()
