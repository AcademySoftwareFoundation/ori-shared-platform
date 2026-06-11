+++
title       = "RV Frame Compare"
description = "Side-by-side frame comparison with wipe, difference, and overlay modes for OpenRV review sessions."
date        = 2026-05-12T00:00:00Z
draft       = false

version = "1.0.0"
author  = "test-contributor"
license = "Apache-2.0"

host_app = ["OpenRV"]
tags     = ["review", "utility", "workflow"]

[params]
  repoPath = "plugins/rv-frame-compare"
+++

## Overview

RV Frame Compare adds a dockable panel to OpenRV that lets reviewers compare any two frames or sources
side-by-side without leaving the session. Three comparison modes are supported:

- **Wipe** — drag a split line horizontally or vertically across the viewport
- **Difference** — subtracts pixel values and amplifies the result for easy spotting of subtle changes
- **Overlay** — blends two sources at a configurable opacity

This plugin was created as a test case for the ORI plugin registry deployment workflow.

## Requirements

| Requirement | Version |
|---|---|
| OpenRV | 2024.0 or later |
| Python | 3.9+ |
| OS | macOS 12+, Linux (RHEL 8+) |

## Installation

### OpenRV

1. Download the plugin package from the repository (see link above).
2. Copy the `rv-frame-compare/` folder into your RV support path:
   - **macOS**: `~/Library/Application Support/RV/Mu/`
   - **Linux**: `~/.rv/Mu/`
3. Restart OpenRV.
4. Open **Preferences → Packages** and enable **RV Frame Compare**.

### Verify

After restarting, a **Frame Compare** panel should appear in the **View** menu.

## Usage

1. Load two sources into your session (e.g. a render and a reference plate).
2. Open **View → Frame Compare** to dock the panel.
3. Use the **A** and **B** dropdowns to select your two sources.
4. Choose a comparison mode from the toolbar:
   - **Wipe**: Click and drag the divider line in the viewport.
   - **Difference**: Adjust the **Amplify** slider to increase contrast on subtle differences.
   - **Overlay**: Use the **Opacity** slider to blend the two sources.
5. Press **Reset** to return to single-source view.

## Known Limitations

- Difference mode does not support sources with mismatched resolutions; both inputs must be the same pixel dimensions.
- Overlay mode opacity resets to 50% when the session is saved and reopened.
- Not compatible with OpenRV stereo (3D) display mode.
