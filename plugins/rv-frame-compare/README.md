# RV Frame Compare

Side-by-side frame comparison with wipe, difference, and overlay modes for OpenRV review sessions.

- **Version**: 1.0.0
- **Author**: test-contributor
- **License**: Apache-2.0
- **Host app**: OpenRV 2024.0+

## Overview

RV Frame Compare adds a dockable panel to OpenRV that lets reviewers compare any two frames or sources
side-by-side without leaving the session. Three comparison modes are supported:

- **Wipe** — drag a split line horizontally or vertically across the viewport
- **Difference** — subtracts pixel values and amplifies the result for spotting subtle changes
- **Overlay** — blends two sources at a configurable opacity

## Installation

1. Copy the `rv-frame-compare/` folder into your RV support path:
   - **macOS**: `~/Library/Application Support/RV/Mu/`
   - **Linux**: `~/.rv/Mu/`
2. Restart OpenRV.
3. Open **Preferences → Packages** and enable **RV Frame Compare**.

## Usage

1. Load two sources into your session.
2. Open **View → Frame Compare** to dock the panel.
3. Select sources A and B from the dropdowns.
4. Choose a comparison mode from the toolbar.

## Known Limitations

- Difference mode requires both sources to have matching pixel dimensions.
- Overlay opacity resets to 50% on session reload.
- Not compatible with OpenRV stereo display mode.
