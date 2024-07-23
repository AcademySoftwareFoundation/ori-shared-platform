class SingletonInstantiatedException(Exception):
    """To raise when a singleton object is tired to be instantiated"""
    def __init__(self):
        super().__init__(
            "This is a singleton, cannot instantiate it! Use get_instance()"
            "class method to get an instance of this class!")
