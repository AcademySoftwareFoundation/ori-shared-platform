INTERACTIVE_MODE = "interactive_mode"
INTERACTIVE_MODE_RECTANGLE = "rectangle"
INTERACTIVE_MODE_ELLIPSE = "ellipse"
INTERACTIVE_MODE_LASSO = "lasso"
INTERACTIVE_MODE_PEN = "pen"
INTERACTIVE_MODE_LINE = "line"
INTERACTIVE_MODE_MULTI_LINE = "multi_line"
INTERACTIVE_MODE_AIRBRUSH = "airbrush"
INTERACTIVE_MODE_TEXT = "text"
INTERACTIVE_MODE_HARD_ERASER = "hard_eraser"
INTERACTIVE_MODE_SOFT_ERASER = "soft_eraser"
INTERACTIVE_MODE_MOVE = "move"
INTERACTIVE_MODE_TRANSFORM = "transform"
INTERACTIVE_MODE_DYNAMIC_TRANSFORM = "dynamic_transform"

SVG_COLOR = "#f0f0f0"

PEN = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="24" height="24"
    fill="none" stroke="{0}" stroke-width="5.3">
    <path d="M 84 27 L 105 47 L 56 96 L 32 99 L 37 74 Z"/>
    <path d="M 56 96 L 37 74"/>
</svg>
"""

AIRBRUSH = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
    stroke="{0}" fill="none" stroke-width="2">
    <circle cx="12" cy="12" r="10" stroke-opacity="0.1" />
    <circle cx="12" cy="12" r="9" stroke-opacity="0.2" />
    <circle cx="12" cy="12" r="8" stroke-opacity="0.3" />
    <circle cx="12" cy="12" r="7" stroke-opacity="0.4" />
    <circle cx="12" cy="12" r="6" stroke-opacity="0.5" />
    <circle cx="12" cy="12" r="5" stroke-opacity="0.6" />
    <circle cx="12" cy="12" r="4" stroke-opacity="0.7" />
    <circle cx="12" cy="12" r="3" stroke-opacity="0.8" />
    <circle cx="12" cy="12" r="2" stroke-opacity="0.9" />
    <circle cx="12" cy="12" r="1" stroke-opacity="1.0" fill="{0}" />
</svg>
"""

TEXT = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
    fill="none" stroke="{0}" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
    <g transform="translate(12 12) scale({1} {1}) translate(-12 -12)">
        <path d="M 4 7 L 4 4 L 20 4 L 20 7"/>
        <path d="M 9 20 L 15 20"/>
        <path d="M 12 4 L 12 20"/>
    </g>
</svg>
"""

HARD_ERASER = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="24" height="24"
    fill="none" stroke="{0}" stroke-width="5.3">
    <path d="M 77 29 L 99 45 L 99 65 L 50 97 L 28 84 L 36 59 Z"/>
    <path d="M 99 45 L 57 76 L 36 59"/>
    <path d="M 50 97 L 57 76"/>
</svg>
"""

SOFT_ERASER = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
    stroke="{0}" fill="none" stroke-width="2">
    <circle cx="12" cy="12" r="10" stroke-opacity="1.0" />
    <circle cx="12" cy="12" r="9" stroke-opacity="0.9" />
    <circle cx="12" cy="12" r="8" stroke-opacity="0.8" />
    <circle cx="12" cy="12" r="7" stroke-opacity="0.7" />
    <circle cx="12" cy="12" r="6" stroke-opacity="0.6" />
    <circle cx="12" cy="12" r="5" stroke-opacity="0.5" />
    <circle cx="12" cy="12" r="4" stroke-opacity="0.4" />
    <circle cx="12" cy="12" r="3" stroke-opacity="0.3" />
    <circle cx="12" cy="12" r="2" stroke-opacity="0.2" />
    <circle cx="12" cy="12" r="1" stroke-opacity="0.1" />
</svg>
"""
