from typing import List
try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore


class ClipAttrApiCore(QtCore.QObject):
    __instance = None

    @classmethod
    def get_instance(cls):
        """Returns the sigleton instance of ActionsHeader"""
        if cls.__instance is None:
            cls.__instance = ClipAttrApiCore()
        return cls.__instance

    def __init__(self):
        if ClipAttrApiCore.__instance is not None:
            raise Exception(
                "Singleton Class! Use ClipAttrApiCore.get_instance() instead!")
        ClipAttrApiCore.__instance = self
        super().__init__()
        self.__id_to_attr = {}
        self.__session = None
        self.__initialized = False

    def init(self, session):
        if self.__initialized:
            return
        self.__session = session
        from rpa.open_rv.rpa_core.api.clip_attr_api_core \
                import _clip_attrs

    def _add_attr(self, attr):
        if attr.id_ in self.__id_to_attr:
            raise Exception(
                f"'{attr.id_}'' already used as an attr id"\
                f" for {self.__id_to_attr.get(attr.id_)}")
        self.__id_to_attr[attr.id_] = attr
        attr_dict = {
            attr.id_: {
                "name": attr.name,
                "data_type": attr.data_type,
                "is_read_only": attr.is_read_only,
                "is_keyable" : attr.is_keyable,
                "default_value": attr.default_value,
                "attr_type" : "core"
            }
        }
        self.__session.attrs_metadata.add(attr_dict)

    def get_attr(self, id):
        return self.__id_to_attr.get(id)
