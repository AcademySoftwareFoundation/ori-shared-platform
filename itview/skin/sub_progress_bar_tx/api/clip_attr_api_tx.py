class ClipAttrApiTx:

    def __init__(self, rpc, rpa):
        self.__rpc = rpc
        self.__rpa = rpa

        self.__rpa.PRG_GET_SHOT_DEF_AUDIO_STARTED.connect(
            self.__get_shot_def_audio_started)
        self.__rpa.PRG_GOT_SHOT_DEF_AUDIO.connect(
            self.__got_shot_def_audio)
        self.__rpa.PRG_GET_SHOT_DEF_AUDIO_COMPLETED.connect(
            self.__hide_progress_bar)

    def __get_shot_def_audio_started(
        self, total_num):
        self.__rpc.rpc.progress_bar_rx.init(
            "Get Default Shot Audio Path...",
            "Getting default shot audio path :", total_num)

    def __got_shot_def_audio(
        self, progress, total_num):
        self.__rpc.rpc.progress_bar_rx.update(
            "Get Default Shot Audio Path...",
            "Getting default shot audio path :", progress, total_num)

    def __hide_progress_bar(self):
        self.__rpc.rpc.progress_bar_rx.hide()
