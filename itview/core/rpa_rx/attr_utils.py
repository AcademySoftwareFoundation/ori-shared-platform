def is_valid(attr:str):
    return not attr.startswith("_") and not attr.startswith("SIG")