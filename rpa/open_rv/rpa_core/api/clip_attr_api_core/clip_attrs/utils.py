from rv import commands
import numpy as np


def get_key_in(source_group:str)->int:
    cut_in = commands.getIntProperty(f"{source_group}_source.cut.in")[0]
    smi = commands.sourceMediaInfo(f"{source_group}_source")
    key_in = smi.get("startFrame") if cut_in == (np.iinfo(np.int32).max * -1) else cut_in

    if not commands.propertyExists(f"{source_group}_source.custom.keyin"):
        commands.newProperty(f"{source_group}_source.custom.keyin", commands.IntType, 1)
        commands.setIntProperty(f"{source_group}_source.custom.keyin", [key_in], True)
        return key_in
    else:
        initial_value = commands.getIntProperty(f"{source_group}_source.custom.keyin")
        start_frame = smi.get("startFrame")
        if initial_value is None:
            commands.setIntProperty(f"{source_group}_source.custom.keyin", [start_frame], True)

        key_in = commands.getIntProperty(f"{source_group}_source.custom.keyin")[0]
        return key_in


def get_key_out(source_group:str)->int:
    cut_out = commands.getIntProperty(f"{source_group}_source.cut.out")[0]
    smi = commands.sourceMediaInfo(f"{source_group}_source")
    key_out = smi.get("endFrame") if cut_out == (np.iinfo(np.int32).max) else cut_out

    if not commands.propertyExists(f"{source_group}_source.custom.keyout"):
        commands.newProperty(f"{source_group}_source.custom.keyout", commands.IntType, 1)
        commands.setIntProperty(f"{source_group}_source.custom.keyout", [key_out], True)
        return key_out
    else:
        initial_value = commands.getIntProperty(f"{source_group}_source.custom.keyout")
        end_frame = smi.get("endFrame")
        if initial_value is None:
            commands.setIntProperty(f"{source_group}_source.custom.keyout", [end_frame], True)

        key_out = commands.getIntProperty(f"{source_group}_source.custom.keyout")[0]
        return key_out


def validate_cross_dissolve(source_group:str):
    key_in = get_key_in(source_group)
    key_out = get_key_out(source_group)
    key_length = key_out - key_in + 1

    dissolve_length = commands.getFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames")[0]
    if key_length < dissolve_length:
        # Deactivate the cross dissolve node by setting its 'node.active' property to 0
        commands.setIntProperty(f"{source_group}_cross_dissolve.node.active", [0], True)
        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame", [float(0)], True)
        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames", [float(0)], True)
    else:
        commands.setIntProperty(f"{source_group}_cross_dissolve.node.active", [1], True)
        dissolve_start = key_length - dissolve_length + 1
        if dissolve_start > key_length:
            dissolve_start = 0
            commands.setIntProperty(f"{source_group}_cross_dissolve.node.active", [0], True)

        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame", [float(dissolve_start)], True)
        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames", [float(dissolve_length)], True)
    return True


def has_frame_edits(source_group)->bool:
    if not commands.propertyExists(f"{source_group}.custom.has_frame_edits"):
        return False
    return commands.getIntProperty(f"{source_group}.custom.has_frame_edits")[0] == 1
