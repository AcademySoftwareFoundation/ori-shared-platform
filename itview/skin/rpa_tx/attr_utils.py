import inspect
import functools


def __method_maker(obj, api_name, method_name, *args, **kwargs):
    def api_method_wrapper(*args, **kwargs):
        api = getattr(obj._rpc.rfc.rpa_rx, api_name)
        api_method = getattr(api, method_name)
        return api_method(*args, **kwargs)
    return functools.partial(api_method_wrapper, *args, **kwargs)


def make_default_methods(from_api, api_name, to_obj):
    from_attrs = inspect.getmembers(from_api, predicate=inspect.isfunction)
    from_attrs = {attr[0]:attr[1] for attr in from_attrs}
    to_attrs = inspect.getmembers(to_obj, predicate=inspect.ismethod)
    to_attrs = {attr[0]:attr[1] for attr in to_attrs}

    for attr_name, _ in from_attrs.items():
        if attr_name in to_attrs.keys():
            continue
        setattr(
            to_obj, attr_name, __method_maker(to_obj, api_name, attr_name))
