import json
from dataclasses import dataclass, asdict
from typing import Optional, Tuple


@dataclass(frozen=True)
class OverlayType:
    text = "text"
    rect = "rect"
    window = "window"


@dataclass
class TextOverlay:
    """
    text:
        The text to be rendered as a text overlay.
    font_path:
        The path to the font of choice. Accepts .ttf(TrueType).
        When an empty string is given, default font will be used.
    size:
        The size of the text as obtained by QFont.pointSize()
    color:
        The color of the text, with each float in the tuple
        representating red, green, blue, alpha respectively.
    position:
        The position of the text box origin defined by 
        x,y-coordinates in normalized space. 
        The text box origin will be centered at this position.
    """
    text: str
    font_path: Optional[str] = ""
    size: Optional[int] = 24
    color: Optional[Tuple[float, float, float, float]] = (1.0, 1.0, 1.0, 1.0) # white
    position: Optional[Tuple[float, float]] = (0.5, 0.5)

    def to_json(self)->str:
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, s:str):
        return cls(**json.loads(s))


@dataclass
class RectOverlay:
    """
    width:
        The width of the rectangle in pixels
        This value will be translated and applied in normalized space
    height:
        The height of the rectangle in pixels
        This value will be translated and applied in normalized space
    color:
        The color of the rect, with each float in the tuple
        representating red, green, blue, alpha respectively.
    position:
        The location of the rectangle defined by 
        x,y-coordinates in normalized space. 
        The rectangle's bottom left coordinate will be at this position.
    """
    width: int
    height: int
    color: Optional[Tuple[float, float, float, float]] = (0.5, 0.5, 0.5, 0.5) # grey
    position: Optional[Tuple[float, float]] = (0.5, 0.5)

    def to_json(self)->str:
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, s:str):
        return cls(**json.loads(s))

