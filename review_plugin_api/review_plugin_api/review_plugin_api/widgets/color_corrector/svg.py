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

UNDO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
    fill="{0}">
    <path d="M447.9,368.2c0-16.8,3.6-83.1-48.7-135.7c-35.2-35.4-80.3-53.4-143.3-56.2V96L64,224l192,128v-79.8 c40,1.1,62.4,9.1,86.7,20c30.9,13.8,55.3,44,75.8,76.6l19.2,31.2H448C448,389.9,447.9,377.1,447.9,368.2z"/>
</svg>
"""

REDO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
    fill="{0}">
    <path d="M64,400h10.3l19.2-31.2c20.5-32.7,44.9-62.8,75.8-76.6c24.4-10.9,46.7-18.9,86.7-20V352l192-128L256,96v80.3 c-63,2.8-108.1,20.7-143.3,56.2c-52.3,52.7-48.7,119-48.7,135.7C64.1,377.1,64,389.9,64,400z"/>
</svg>
"""

TOOL_SIZE = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="{0}" fill="{1}" stroke="{2}" stroke-width="1" />
</svg>
"""