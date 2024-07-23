from exceptions import SingletonInstantiatedException


class Mapper:
    __instance = None

    @classmethod
    def get_instance(cls):
        """Returns the sigleton instance of ActionsHeader"""
        if cls.__instance is None:
            cls.__instance = Mapper()
        return cls.__instance

    def __init__(self):
        if Mapper.__instance is not None:
            raise SingletonInstantiatedException()
        Mapper.__instance = self

        self.__review_plugin_api = None

    def set_review_plugin_api(self, review_plugin_api):
        self.__review_plugin_api = review_plugin_api

    def get_review_plugin_api(self):
        return self.__review_plugin_api
