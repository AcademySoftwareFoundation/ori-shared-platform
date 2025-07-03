from dataclasses import dataclass, field
from typing import List, Union
import copy
from rpa.session_state.utils import Point
from rpa.utils.sequential_uuid_generator import SequentialUUIDGenerator
import os
import uuid


@dataclass
class ColorTimer:
    slope: tuple = (1, 1, 1)
    offset: tuple = (0, 0, 0)
    power: tuple = (1, 1, 1)
    saturation: int = 1
    mute: bool = False
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def clear(self):
        self.slope = None
        self.offset = None
        self.power = None
        self.saturation = None
        self.mute = None

    def __getstate__(self):
        return {**self.__dict__, **{"class_name": self.__class__.__name__}}

    def get_dict(self):
        return self.__getstate__()

    def __setstate__(self, state):
        for key, value in state.items():
            if key in self.__dataclass_fields__:
                if isinstance(value, list): value = tuple(value)
                setattr(self, key, value)
        return self

    @property
    def is_modified(self):
        return not(
            self.slope == (1, 1, 1) and
            self.offset == (0, 0, 0) and
            self.power == (1, 1, 1) and
            self.saturation == 1)

@dataclass
class Grade:
    blackpoint: tuple = (0, 0, 0)
    whitepoint: tuple = (1, 1, 1)
    lift: tuple = (0, 0, 0)
    gain: tuple = (1, 1, 1)
    multiply: tuple = (1, 1, 1)
    gamma: tuple = (1, 1, 1)
    mute: bool = False
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def clear(self):
        self.blackpoint = None
        self.whitepoint = None
        self.lift = None
        self.gain = None
        self.multiply = None
        self.gamma = None
        self.mute = None

    def __getstate__(self):
        return {**self.__dict__, **{"class_name": self.__class__.__name__}}

    def get_dict(self):
        return self.__getstate__()

    def __setstate__(self, state):
        for key, value in state.items():
            if key in self.__dataclass_fields__:
                if isinstance(value, list): value = tuple(value)
                setattr(self, key, value)
        return self

    @property
    def is_modified(self):
        return not(
            self.blackpoint == (0, 0, 0) and
            self.whitepoint == (1, 1, 1) and
            self.lift == (0, 0, 0) and
            self.gain == (1, 1, 1) and
            self.multiply == (1, 1, 1) and
            self.gamma == (1, 1, 1))

@dataclass
class Shape:
    points: List[Point] = field(default_factory=list)

    def clear(self):
        for point in self.points:
            point = None

    def __getstate__(self):
        return {
            "points": [point.__getstate__() for point in self.points]
        }

    def __setstate__(self, state):
        self.points = [Point().__setstate__(point) for point in state["points"]]
        return self

@dataclass
class Region:
    falloff: int = 0
    shapes: List[Shape] = field(default_factory=list)
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def clear(self):
        self.falloff = None
        for shape in self.shapes:
            shape.clear()

    def __getstate__(self):
        return {
            "falloff" : self.falloff,
            "shapes" :  [shape.__getstate__() for shape in self.shapes]
        }

    def __setstate__(self, state):
        self.falloff = state["falloff"]
        self.shapes = [Shape().__setstate__(shape) for shape in state["shapes"]]
        return self

    @property
    def is_modified(self):
        return not(self.falloff == 0)


@dataclass
class ColorCorrection:
    id: str = None
    name: str = None
    nodes: List[Union[ColorTimer, Grade]] = field(default_factory=list)
    region: Region = None
    mute: bool = False
    is_ro: bool = False
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def clear(self):
        self.name = None
        for node in self.nodes:
            node.clear()
        if self.region: self.region.clear()

    def __getstate__(self):
        """ Convert ColorCorrection instance to a serializable state. """
        return {
            "id": self.id,
            "nodes": [node.__getstate__() for node in self.nodes],
            "name": self.name,
            "region": self.region.__getstate__() if self.region else None,
            "mute": self.mute,
            "is_ro": self.is_ro
        }

    def __setstate__(self, state):
        """ Restore the instance from a serializable state. """
        self.id = state["id"]
        for node in state["nodes"]:
            if node["class_name"] == "ColorTimer":
                n = ColorTimer().__setstate__(node)
            if node["class_name"] == "Grade":
                n = Grade().__setstate__(node)
            self.nodes.append(n)
        self.name = state["name"]
        self.region = Region().__setstate__(state["region"]) if state["region"] else None
        self.mute = state["mute"]
        self.is_ro = state["is_ro"]
        return self

    @property
    def is_modified(self):
        for node in self.nodes:
            if node.is_modified:
                return True
        return False if not self.region else self.region.is_modified

    def set_mute(self, value):
        self.mute = value
        for node in self.nodes:
            node.mute = value


@dataclass
class ColorCorrections:
    """ Defines color corrections in a particular clip. """

    def __init__(self):
        self.__uuid_generator = SequentialUUIDGenerator(
            os.environ.get("CC_UUID_SEED", uuid.uuid4().hex))
        self.__default_clip_cc_id = self.__uuid_generator.next_uuid()
        clip_cc = ColorCorrection(
            id = self.__default_clip_cc_id,
            name = "Clip",
            nodes = [ColorTimer(), Grade()]
        )
        self.id_to_cc = {self.__default_clip_cc_id:clip_cc}
        self.clip_ccs = [self.__default_clip_cc_id]
        self.frame_ccs = {} # dict[int, List[ColorCorrection]]
        self.__mute = False
        self.__custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def __getstate__(self):
        return {
            "default_clip_cc_id": self.__default_clip_cc_id,
            "id_to_cc": self.id_to_cc,
            "clip_ccs": self.clip_ccs,
            "frame_ccs": self.frame_ccs,
            "mute": self.__mute
        }

    def __setstate__(self, state):
        self.__default_clip_cc_id = state["default_clip_cc_id"]
        self.id_to_cc = state["id_to_cc"]
        self.clip_ccs = state["clip_ccs"]
        self.frame_ccs = state["frame_ccs"]
        self.__mute = state["mute"]
        return self

    # Create
    def append_ccs(self, names, frame=None, cc_ids=None):
        if not cc_ids:
            cc_ids = []
            for i in range(len(names)):
                cc_ids.append(self.__uuid_generator.next_uuid())
        for id, name in zip(cc_ids, names):
            cc = ColorCorrection(id=id, name=name)
            self.id_to_cc[id] = cc
            if frame is None:
                self.clip_ccs.append(id)
            else:
                if frame not in self.frame_ccs:
                    self.frame_ccs[frame] = []
                self.frame_ccs[frame].append(id)
        return cc_ids

    def append_nodes(self, cc_id, nodes):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        for node in nodes:
            cc.nodes.append(node)

    # Read
    def get_cc_ids(self, frame=None):
        if frame is None:
            return self.clip_ccs[:]
        frame_ccs = self.frame_ccs.get(frame, [])
        return frame_ccs[:] if frame_ccs else frame_ccs

    def get_ro_ccs(self, frame=None):
        return self.__get_ccs(is_ro=True, frame=frame)

    def get_rw_ccs(self, frame=None):
        return self.__get_ccs(is_ro=False, frame=frame)

    def __get_ccs(self, is_ro:bool, frame=None):
        ccs = []
        if frame is None:
            for cc_id in self.clip_ccs:
                cc = self.id_to_cc.get(cc_id, None)
                if cc is None or cc.is_ro is not is_ro: continue
                ccs.append(cc)
        else:
            cc_ids = self.frame_ccs.get(frame, [])
            for cc_id in cc_ids:
                cc = self.id_to_cc.get(cc_id, None)
                if cc is None or cc.is_ro is not is_ro: continue
                ccs.append(cc)
        return ccs

    def get_nodes(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return []
        return [copy.deepcopy(node) for node in cc.nodes]

    def get_node_count(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        return len(cc.nodes)

    def get_node(self, cc_id, node_index):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        try:
            return copy.deepcopy(cc.nodes[node_index])
        except IndexError:
            return None

    def get_name(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        return cc.name

    def has_region(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        return True if cc.region else False

    def get_region_falloff(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        if cc.region: return cc.region.falloff

    def get_rw_frames(self):
        frames = []
        for frame, cc_ids in self.frame_ccs.items():
            for cc_id in cc_ids:
                cc = self.id_to_cc.get(cc_id, None)
                if cc and not cc.is_ro and cc.is_modified:
                    frames.append(frame)
                    break
        return frames

    def get_ro_frames(self):
        frames = []
        for frame, cc_ids in self.frame_ccs.items():
            for cc_id in cc_ids:
                cc = self.id_to_cc.get(cc_id, None)
                if cc and cc.is_ro and cc.is_modified:
                    frames.append(frame)
                    break
        return frames

    def is_modified(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        return cc.is_modified

    def is_mute(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        return cc.mute

    def is_mute_all(self):
        return self.__mute

    def is_read_only(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        return cc.is_ro

    # Update
    def move_cc(self, from_index, to_index, frame=None):
        def is_valid_index(lst, index):
            return 0 <= index < len(lst)

        if frame is None:
            if is_valid_index(self.clip_ccs, from_index):
                clip_cc = self.clip_ccs.pop(from_index)
                self.clip_ccs.insert(to_index, clip_cc)
        else:
            frame_ccs = self.frame_ccs.get(frame)
            if frame_ccs and is_valid_index(frame_ccs, from_index):
                frame_cc = frame_ccs.pop(from_index)
                self.frame_ccs[frame].insert(to_index, frame_cc)

    def set_node_properties(self, cc_id, node_index, properties):
        cc = self.id_to_cc.get(cc_id, None)
        try:
            cc.nodes[node_index].__setstate__(properties)
        except IndexError:
            return

    def get_node_properties(self, cc_id, node_index, property_names):
        cc = self.id_to_cc.get(cc_id, None)
        try:
            node_dict = cc.nodes[node_index].get_dict()
            props = []
            for prop_name in property_names:
                props.append(node_dict.get(prop_name))
            return props
        except IndexError:
            return []

    def set_name(self, cc_id, name):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        cc.name =  name

    def create_region(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        cc.region = Region()

    def append_shape_to_region(self, cc_id, points):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        if cc.region is None: return
        points = [Point(*point) for point in points]
        cc.region.shapes.append(Shape(points=points))

    def set_region_falloff(self, cc_id, falloff):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        cc.region.falloff = falloff

    def set_mute(self, cc_id, value):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        cc.set_mute(value)

    def mute_all(self, value):
        self.__mute = value
        for cc in self.id_to_cc.values():
            cc.set_mute(value)

    def set_read_only(self, cc_id, value):
        cc = self.id_to_cc.get(cc_id, None)
        if not cc: return
        cc.is_ro = value

    # Delete
    def delete_ccs(self, cc_ids, frame=None):
        for cc_id in cc_ids:
            if cc_id not in self.id_to_cc:
                continue
            del self.id_to_cc[cc_id]
            if frame is not None and frame in self.frame_ccs:
                self.frame_ccs[frame].remove(cc_id)
            else:
                self.clip_ccs.remove(cc_id)

    def get_frame_of_cc(self, cc_id):
        for frame, cc_ids in self.frame_ccs.items():
            if cc_id in cc_ids:
                return frame
        return None

    def clear_nodes(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if cc: cc.nodes.clear()

    def delete_node(self, cc_id, node_index):
        cc = self.id_to_cc.get(cc_id, None)
        if cc and 0 <= node_index < len(cc.nodes): cc.nodes.pop(node_index)

    def delete_region(self, cc_id):
        cc = self.id_to_cc.get(cc_id, None)
        if cc: cc.region = None

    def clear(self):
        self.id_to_cc.clear()
        self.frame_ccs.clear()
        self.clip_ccs.clear()

        self.__uuid_generator = None
        self.__default_clip_cc_id = None
        self.__mute = False

    def set_ro_ccs(self, ro_ccs):
        self.__set_ccs(ro_ccs, is_ro=True)

    def set_rw_ccs(self, rw_ccs):
        self.__set_ccs(rw_ccs, is_ro=False)

    def __set_ccs(self, ccs, is_ro):
        if is_ro: self.delete_ro_ccs()
        else: self.delete_rw_ccs()
        for frame, cc in ccs:
            self.id_to_cc[cc.id] = cc
            if frame is None:
                self.clip_ccs.append(cc.id)
            else:
                if frame not in self.frame_ccs:
                    self.frame_ccs[frame] = []
                self.frame_ccs[frame].append(cc.id)
            cc.is_ro = is_ro

    def delete_ro_ccs(self):
        ro_ccs_to_remove = []
        # Delete clip ro ccs
        for cc_id in self.get_cc_ids():
            if self.id_to_cc[cc_id].is_ro: ro_ccs_to_remove.append(cc_id)
        self.delete_ccs(ro_ccs_to_remove)
        # Delete frame ro ccs
        for frame in self.get_ro_frames():
            ro_ccs_to_remove = []
            for cc_id in self.get_cc_ids(frame):
                if self.id_to_cc[cc_id].is_ro: ro_ccs_to_remove.append(cc_id)
            self.delete_ccs(ro_ccs_to_remove, frame)

    def delete_rw_ccs(self):
        rw_ccs_to_remove = []
        # Delete clip rw ccs
        for cc_id in self.get_cc_ids():
            if not self.id_to_cc[cc_id].is_ro: rw_ccs_to_remove.append(cc_id)
        self.delete_ccs(rw_ccs_to_remove)
        # Delete frame ro ccs
        for frame in self.get_rw_frames():
            rw_ccs_to_remove = []
            for cc_id in self.get_cc_ids(frame):
                if not self.id_to_cc[cc_id].is_ro: rw_ccs_to_remove.append(cc_id)
            self.delete_ccs(rw_ccs_to_remove, frame)

    def delete(self):
        # TODO : Logic to create all color-corrections needs to be here.
        pass
