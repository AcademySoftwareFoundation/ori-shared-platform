import copy
from typing import List


class AttrsMetadata:
    def __init__(self, parent):
        self.__parent = parent
        self.__metadata = {}
        self.add(
            {
                "play_order": {
                    "name": "Play Order",
                    "data_type": "int",
                    "is_read_only": True,
                    "is_keyable": False,
                    "default_value": 0,
                    "attr_type": "core"
                }
            }
        )
        self.add(
            {
                "comment": {
                    "name": "Comment",
                    "data_type": "str",
                    "is_read_only": False,
                    "is_keyable": False,
                    "default_value": "",
                    "attr_type": "session"
                }
            }
        )

    @property
    def parent(self):
        return self.__parent

    def add(self, attr:dict):
        self.__metadata.update(attr)

    def get_copy(self):
        return copy.deepcopy(self.__metadata)

    def update(self, attrs):
        self.__metadata.update(attrs)

    def clear(self):
        for id, meta_data in list(self.__metadata.items()):
            if isinstance(meta_data, dict):
                meta_data.clear()
            del self.__metadata[id]
        self.__metadata.clear()

    @property
    def ids(self):
        return list(self.__metadata.keys())

    @property
    def read_only_ids(self):
        out = []
        for id, meta_data in self.__metadata.items():
            if meta_data.get("is_read_only"):
                out.append(id)
        return out

    @property
    def read_write_ids(self):
        out = []
        for id, meta_data in self.__metadata.items():
            if not meta_data.get("is_read_only"):
                out.append(id)
        return out

    @property
    def keyable_ids(self):
        out = []
        for id, meta_data in self.__metadata.items():
            if meta_data.get("is_keyable"):
                out.append(id)
        return out

    def get_name(self, id):
        return self.__metadata.get(id).get("name")

    def is_read_only(self, id):
        return self.__metadata.get(id).get("is_read_only")

    def get_data_type(self, id):
        return self.__metadata.get(id).get("data_type")

    def get_default_value(self, id):
        return self.__metadata.get(id).get("default_value")

    def is_keyable(self, id):
        return self.__metadata.get(id).get("is_keyable")

    def get(self, attr_id, metadata_id):
        meta_data = self.__metadata.get(attr_id)
        if meta_data is None:
            return
        return meta_data.get(metadata_id)
