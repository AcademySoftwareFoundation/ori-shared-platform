import inspect


def get_attrs(api):
    attrs = {}
    for attr in dir(api):
        if not attr.startswith("_"):
            attrs[attr] = getattr(api, attr)
    return attrs


def make_callables(from_api, to_api):
    from_attrs = get_attrs(from_api)
    to_attrs = get_attrs(to_api)
    for from_attr_name, from_attr in from_attrs.items():
        if from_attr_name in to_attrs.keys() or not callable(from_attr):
            continue
        setattr(to_api, from_attr_name, from_attr)


def __get_members(module, is_valid_member_name, exclude=[]):
    members = {}
    for member_name, member in inspect.getmembers(module):
        if member in exclude:
            continue
        if is_valid_member_name(member_name):
            members[member_name] = member
        else:
            continue
    return members


def __get_members_with_same_name(
    from_api, to_api, is_valid_member_name):

    from_api_members = __get_members(from_api, is_valid_member_name)
    to_api_members = __get_members(to_api, is_valid_member_name)

    for from_api_member_name, from_api_member in from_api_members.items():
        if from_api_member_name not in to_api_members:
            continue
        yield (from_api_member, to_api_members[from_api_member_name])


def connect_signals(from_api, to_api):
    def is_valid_member_name(member_name):
        return member_name.startswith("SIG")
    for from_signal, to_signal in __get_members_with_same_name(
        from_api, to_api, is_valid_member_name):
        from_signal.connect(to_signal)
