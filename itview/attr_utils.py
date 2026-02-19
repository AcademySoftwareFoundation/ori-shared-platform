def get_attrs(api, is_valid):
    attrs = {}
    for attr in dir(api):
        if is_valid(attr):
            attrs[attr] = getattr(api, attr)
    return attrs


def make_attrs(from_api, to_api, is_valid):
    from_attrs = get_attrs(from_api, is_valid)
    to_attrs = get_attrs(to_api, is_valid)

    for attr_name, attr in from_attrs.items():
        if attr_name in to_attrs.keys() or not callable(attr):
            continue
        setattr(to_api, attr_name, attr)
