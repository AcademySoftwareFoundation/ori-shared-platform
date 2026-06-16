+++
title       = "RV Frame Compare"
description = "Side-by-side frame comparison with wipe, difference, and overlay modes for OpenRV review sessions."
date        = 2026-06-11T00:00:00Z
draft       = false

version = "1.0.0"
author  = "erikstrauss"
license = "Apache-2.0"

host_app = ["OpenRV"]
tags     = ["review", "utility", "workflow"]

[params]
  repoUrl   = "https://github.com/erikstrauss/rv-frame-compare"
  repoOwner = "erikstrauss"
+++

## Overview

RV Frame Compare adds a dockable panel to OpenRV that lets reviewers compare any two frames or sources
side-by-side without leaving the session. Three comparison modes are supported:

- **Wipe** — drag a split line horizontally or vertically across the viewport
- **Difference** — subtracts pixel values and amplifies the result for easy spotting of subtle changes
- **Overlay** — blends two sources at a configurable opacity

## Requirements

| Requirement | Version |
|---|---|
| OpenRV | 2024.0 or later |
| Python | 3.9+ |
| OS | macOS 12+, Linux (RHEL 8+) |

## Installation

1. Download or clone the plugin from the repository linked above.
2. Copy the plugin folder into your RV support path:
   - **macOS**: `~/Library/Application Support/RV/Mu/`
   - **Linux**: `~/.rv/Mu/`
3. Restart OpenRV.
4. Open **Preferences → Packages** and enable **RV Frame Compare**.

## Usage

1. Load two sources into your session.
2. Open **View → Frame Compare** to dock the panel.
3. Use the **A** and **B** dropdowns to select your two sources.
4. Choose a comparison mode from the toolbar.
5. Press **Reset** to return to single-source view.

## Known Limitations

- Difference mode requires both sources to have matching pixel dimensions.
- Overlay opacity resets to 50% on session reload.
- Not compatible with OpenRV stereo display mode.
