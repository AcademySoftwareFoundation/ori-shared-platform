from dataclasses import dataclass, field
from scipy import interpolate


@dataclass(frozen=True)
class TransformType:
    fps = "FPS"
    rotate = "ROTATE"
    pan_x = "PAN_X"
    pan_y = "PAN_Y"
    zoom_x = "ZOOM_X"
    zoom_y = "ZOOM_Y"


@dataclass(frozen=True)
class TransformData:
    zoom_mult = 100
    default_0 = 0.0
    default_1 = 1.0
    default_24 = 24.0


@dataclass(frozen=True)
class DynamicAttrs:
    rotation = "dynamic_rotation"
    pan_x = "dynamic_translate_x"
    pan_y = "dynamic_translate_y"
    zoom_x = "dynamic_scale_x"
    zoom_y = "dynamic_scale_y"


@dataclass(frozen=True)
class StaticAttrs:
    rotation = "rotation"
    pan_x = "pan_x"
    pan_y = "pan_y"
    zoom_x = "scale_x"
    zoom_y = "scale_y"


MEDIA_FPS = "media_fps"

DYNAMIC_TRANSFORM_ATTRS = \
    [DynamicAttrs.rotation, DynamicAttrs.pan_x, DynamicAttrs.pan_y, DynamicAttrs.zoom_x, DynamicAttrs.zoom_y]

STATIC_TRANSFORM_ATTRS = \
    [StaticAttrs.rotation, StaticAttrs.pan_x, StaticAttrs.pan_y, StaticAttrs.zoom_x, StaticAttrs.zoom_y]

SCALE_ATTRS = \
    [StaticAttrs.zoom_x, StaticAttrs.zoom_y, DynamicAttrs.zoom_x, DynamicAttrs.zoom_y]


class Interpolator:
    def __init__(self, x_values, y_values, degree=1):
        self.__size = len(x_values)
        if self.__size != len(y_values):
            raise RuntimeError("Lists sizes do not match")
        self.__x_values = x_values
        self.__y_values = y_values
        self.__interpolator = None
        if self.__size >= 2:
            k = min(degree, self.__size - 1)
            self.__interpolator = interpolate.splrep(x_values, y_values, k=k)

    def get(self, x, default=0.0):
        if self.__size == 0:
            return default
        if x <= self.__x_values[0]:
            return self.__y_values[0]
        if x >= self.__x_values[-1]:
            return self.__y_values[-1]
        return float(interpolate.splev(x, self.__interpolator))


class RotationInterpolator:
    def __init__(self, x_values, y_values, degree=1):
        # keep the diff in (-180, +180) degree range
        for i in range(1, len(y_values)):
            while y_values[i] - y_values[i - 1] < -180:
                y_values[i] += 360
            while y_values[i] - y_values[i - 1] > +180:
                y_values[i] -= 360
        self.__interpolator = Interpolator(x_values, y_values, degree=degree)

    def get(self, x, default=0.0):
        return self.__interpolator.get(x, default=default) % 360.0
