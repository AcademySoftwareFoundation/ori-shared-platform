class DelegateMngr:
    def __init__(self):
        self.__core_delegates = {}
        self.__delegates = {}

    def register_core_delegate_func(self, primary_func, delegate_func):
        self.__core_delegates[primary_func] = delegate_func

    def add_delegate_func(self, primary_func, delegate_func):
        self.__delegates.setdefault(primary_func, []).append(delegate_func)

    def call(self, primary_func, args=None, kwargs=None):
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        core_delegate_func = self.__core_delegates.get(primary_func)
        out = None
        if core_delegate_func:
            out = core_delegate_func(*args, **kwargs)

        delegate_funcs = self.__delegates.get(primary_func)
        if delegate_funcs:
            for delegate_func in delegate_funcs:
                delegate_func(*args, **kwargs)

        return out
