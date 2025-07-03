class PlaylistNameGenerator:

    def __init__(self, default_name:str=None):
        self.__title = "New Playlist" if default_name is None else default_name
        self.__title_num = 0

    def generate_name(self):
        self.__title_num += 1
        num = str(self.__title_num)
        playlist_title = self.__title + " " + num
        return playlist_title
