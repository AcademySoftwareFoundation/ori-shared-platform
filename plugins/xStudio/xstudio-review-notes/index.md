+++
title       = "xStudio Review Notes Exporter"
description = "Export reviewer annotations and session notes from xStudio to JSON or CSV for downstream pipeline consumption."
date        = 2026-06-11T00:00:00Z
draft       = false

version = "1.0.0"
author  = "erikstrauss"
license = "Apache-2.0"

host_app = ["xStudio"]
tags     = ["annotation", "export", "pipeline", "workflow"]

[params]
  repoUrl   = "https://github.com/erikstrauss/xstudio-review-notes"
  repoOwner = "erikstrauss"
+++

## Overview

xStudio Review Notes Exporter adds a panel to xStudio that collects all annotations,
drawn notes, and text comments from a review session and exports them to a structured
file for use in downstream pipeline tools.

Supported output formats:

- **JSON** — structured per-shot, per-frame annotation data
- **CSV** — flat spreadsheet-friendly format for editorial and production tracking

## Requirements

| Requirement | Version |
|---|---|
| xStudio | 1.2.0 or later |
| Python | 3.9+ |
| OS | macOS 12+, Linux (RHEL 8+) |

## Installation

1. Download or clone the plugin from the repository linked above.
2. Copy the plugin folder into your xStudio plugin path:
   - **macOS**: `~/Library/Application Support/xStudio/plugins/`
   - **Linux**: `~/.xstudio/plugins/`
3. Restart xStudio.
4. Open **Preferences → Plugins** and enable **Review Notes Exporter**.

## Usage

1. Complete your review session and add annotations as normal.
2. Open **Tools → Notes Export**.
3. Choose an output format (JSON or CSV) and a destination path.
4. Click **Export** — a file is written containing all annotations for the current session.

### JSON output example

```json
{
  "session": "review_2026-06-11",
  "shots": [
    {
      "name": "SH010",
      "frame": 1042,
      "timecode": "00:00:43:10",
      "author": "reviewer",
      "note": "Fix the sky grade in the upper left corner.",
      "color": "#ff4444"
    }
  ]
}
```

## Known Limitations

- Drawn (freehand) annotations are exported as bounding-box coordinates only, not vector paths.
- CSV export does not preserve annotation colour data.
- Exporting sessions with more than 5,000 annotations may be slow on first run.
