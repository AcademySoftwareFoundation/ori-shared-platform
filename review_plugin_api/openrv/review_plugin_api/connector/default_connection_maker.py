import inspect


def __get_api_funcs(api):
    api_funcs = {}
    for func_name, func in inspect.getmembers(api):
        if func_name.startswith("_"):
            continue
        api_funcs[func_name] = func
    return api_funcs


def __get_funcs_with_same_name(review_plugin_api, connection):
    review_plugin_api_funcs = __get_api_funcs(review_plugin_api)
    connection_funcs = __get_api_funcs(connection)

    for review_plugin_api_func_name, review_plugin_api_func in review_plugin_api_funcs.items():
        if review_plugin_api_func_name not in connection_funcs:
            continue
        yield (review_plugin_api_func, connection_funcs[review_plugin_api_func_name])


def register_core_delegate_func(review_plugin_api, connection):
    delegate_mngr = review_plugin_api.get_delegate_mngr()
    for review_plugin_api_func, connection_func in \
        __get_funcs_with_same_name(review_plugin_api, connection):
        delegate_mngr.register_core_delegate_func(
            review_plugin_api_func, connection_func)


def add_delegate_func(review_plugin_api, connection):
    delegate_mngr = review_plugin_api.get_delegate_mngr()
    for review_plugin_api_func, connection_func in \
        __get_funcs_with_same_name(review_plugin_api, connection):
        delegate_mngr.add_delegate_func(review_plugin_api_func, connection_func)
