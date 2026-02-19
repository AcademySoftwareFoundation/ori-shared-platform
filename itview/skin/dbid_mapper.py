class DbidMapper:
    def __init__(self):
        self.__dbid_to_clips = {}
        self.__clip_to_dbid = {}

    def map(self, clip, dbid):
        self.__clip_to_dbid[clip] = dbid
        self.__dbid_to_clips.setdefault(dbid, []).append(clip)

    def get_dbid(self, clip):
        return self.__clip_to_dbid.get(clip, (None, None))

    def get_clips(self, dbid):
        return self.__dbid_to_clips.get(dbid, [])

    def unmap(self, clip):
        if clip not in self.__clip_to_dbid:
            return
        dbid = self.__clip_to_dbid[clip]
        del self.__clip_to_dbid[clip]
        self.__dbid_to_clips[dbid].remove(clip)
        if len(self.__dbid_to_clips[dbid]) == 0:
            del self.__dbid_to_clips[dbid]

    def is_mapped(self, clip):
        return clip in self.__clip_to_dbid

    def clear(self):
        self.__clip_to_dbid.clear()
        for clips in self.__dbid_to_clips.values():
            clips.clear()
        self.__dbid_to_clips.clear()
