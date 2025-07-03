import inspect
from functools import partial


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
    primary, secondary, is_valid_member_name, exclude=[]):

    primary_members = __get_members(primary, is_valid_member_name, exclude)
    secondary_members = __get_members(secondary, is_valid_member_name, exclude)

    for primary_member_name, primary_member in primary_members.items():
        if primary_member_name not in secondary_members:
            continue
        yield (primary_member, secondary_members[primary_member_name])

def __is_valid_method_name(member_name):
    return not member_name.startswith("_") and \
        not member_name.startswith("SIG")

def __set_core_delegates(primary, secondary):
    delegate_mngr = primary.delegate_mngr
    for primary_func, secondary_func in __get_members_with_same_name(
        primary, secondary, __is_valid_method_name):
        delegate_mngr._set_core_delegate(
            primary_func, secondary_func)


def __set_core_signals(primary, secondary):
    def is_valid_member_name(member_name):
        return member_name.startswith("SIG")
    for primary_signal, secondary_signal in __get_members_with_same_name(
        primary, secondary, is_valid_member_name):
        secondary_signal.connect(primary_signal)


def __is_valid_api_name(member_name):
    return member_name.endswith("_api") and \
        not member_name.startswith("_")


def set_core_delegates_for_all_rpa(primary, secondary, exclude=[]):
    for primary_api, secondary_api in __get_members_with_same_name(
        primary, secondary, __is_valid_api_name, exclude):
        set_core_delegates(primary_api, secondary_api)


def set_core_delegates(primary_api, secondary_api):
    __set_core_delegates(primary_api, secondary_api)
    __set_core_signals(primary_api, secondary_api)
