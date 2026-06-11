# xStudio Review Notes Exporter

Export reviewer annotations and session notes from xStudio to JSON or CSV for downstream pipeline consumption.

- **Version**: 1.0.0
- **Author**: test-contributor
- **License**: Apache-2.0
- **Host app**: xStudio 1.2.0+

## Overview

Collects all annotations, drawn notes, and text comments from a review session and exports them to a structured file for use in downstream pipeline tools. Supports JSON and CSV output formats.

## Installation

1. Copy the `xstudio-review-notes/` folder into your xStudio plugin path:
   - **macOS**: `~/Library/Application Support/xStudio/plugins/`
   - **Linux**: `~/.xstudio/plugins/`
2. Restart xStudio.
3. Open **Preferences → Plugins** and enable **Review Notes Exporter**.

## Usage

1. Complete your review session with annotations.
2. Open **Tools → Notes Export**.
3. Choose JSON or CSV output format and a destination path.
4. Click **Export**.
