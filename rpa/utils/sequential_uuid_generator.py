import hashlib


class SequentialUUIDGenerator:
    def __init__(self, seed):
        self.__uuid = seed

    def next_uuid(self):
        self.__uuid = hashlib.sha256(
            self.__uuid.encode('utf-8')).hexdigest()[:32]
        return self.__uuid
