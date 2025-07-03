"""File with helper method related to property getters/setters"""
from rv import commands as rvc


def get_property(prop):
    """
    Helper function for retrieving RV's property. It automatically detects the type and dimension
    of the property values.

    Args:
        prop (str): Name of the property.

    Returns:
        Value of the requested property.
    """
    if not rvc.propertyExists(prop):
        return []
    info = rvc.propertyInfo(prop)
    prop_type = info["type"]
    dimension = info["dimensions"][0]
    def _():
        if prop_type == rvc.IntType:
            return rvc.getIntProperty(prop)
        if prop_type == rvc.FloatType:
            return rvc.getFloatProperty(prop)
        if prop_type == rvc.StringType:
            return rvc.getStringProperty(prop)
        raise TypeError("Unsupported property type")
    values = _()
    if dimension <= 1:
        return values
    return [values[i * dimension:(i + 1) * dimension]
            for i in range((len(values) + dimension - 1) // dimension)]

def set_property(prop, values):
    """
    Helper function for setting RV's property. It automatically detects the type and dimension
    of the property values.

    Args:
        prop (str): Name of the property.
        values (list): List of values to be set.
    """
    if not values:
        if rvc.propertyExists(prop):
            rvc.deleteProperty(prop)
        return
    def _(prop_type, width, setter):
        if not rvc.propertyExists(prop):
            rvc.newProperty(prop, prop_type, width)
        return setter(prop, values, True)
    value = values[0]
    width = 1
    if isinstance(value, list):
        width = len(value)
        values = sum(values, [])
        value = value[0]
    if isinstance(value, int):
        return _(rvc.IntType, width, rvc.setIntProperty)
    if isinstance(value, float):
        return _(rvc.FloatType, width, rvc.setFloatProperty)
    if isinstance(value, str):
        return _(rvc.StringType, width, rvc.setStringProperty)
    raise TypeError("Unsupported property type")

def append_property(prop, values):
    """
    Helper function for appending to RV's property. It automatically detects the type and dimension
    of the property values.

    Args:
        prop (str): Name of the property.
        values (list): List of values to be appended.
    """
    old_values = get_property(prop) if rvc.propertyExists(prop) else []
    set_property(prop, old_values + values)

def delete_property(prop):
    """
    Helper function for deleteing RV's property. It does not raise exception in case the property
    does not exist.

    Args:
        prop (str): Name of the property.
    """
    set_property(prop, [])

def get_default_start_end_frame(source_node):
    smi = rvc.sourceMediaInfo(source_node)
    if smi:
        start = int(smi.get("startFrame"))
        end = int(smi.get("endFrame"))
        return start, end
    return None, None

def convert_frame(frame, source_node):
    """ Function that helps convert source_frame to 1....n range.
        This is done as RVPaint node recognizes only such range,
        however a clip can have frames starting from 1001...1050
        and so on.
    """
    smi = rvc.sourceMediaInfo(source_node)
    return int(frame) - smi["startFrame"] + 1

def convert_to_global_frame(frame, node):
    """ Function that helps convert frame relative to node to global frame.
        Source frame (1001...) can be converted to global frame as long as the
        node provided is the source. If stack node provided, for example,
        frame in range (1...) needs to be given.
        Return -1 if unable to convert
    """
    temp_prop = f"{node}.find.frames"
    set_property(temp_prop, [frame])
    global_frame_map = rvc.mapPropertyToGlobalFrames("find.frames", 1)
    if len(global_frame_map) > 0:
        return global_frame_map[0]
    return -1

def get_global_frame(source_node, src_frame):
    if source_node is None:
        return
    return convert_to_global_frame(src_frame, source_node)

# convert value from itview to rv value
def convert_translate_itview_to_rv(value:float, h:int)->float:
    """Function that helps convert Itview translate value to RV translate value.
       h is the height of the image in which translation is applied.
    """
    return (value / h)

# convert value from rv to itview value
def convert_translate_rv_to_itview(value:float, h:int)->float:
    """Function that helps convert RV translate value to Itview translate value.
       h is the height of the image in which translation is applied.
    """
    return float(round(value * h))