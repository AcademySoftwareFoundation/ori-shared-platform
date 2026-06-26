+++
title       = "Filesystem Browser"
description = "A multi-threaded filesystem browser plugin for visual effects review tools. Browse large directory trees, detect image sequences, filter by time or version, preview media on hover, and load files into the host application — all without blocking the UI."
date        = 2026-06-28T00:00:00Z
draft       = false

version = "1.0.0"
author  = "richardssam"
license = "Apache-2.0"

host_app = ["OpenRV"]
tags     = ["review", "io", "import utility"]

[params]
  repoUrl = "https://github.com/richardssam/filesystem_browser"
  repoOwner = "richardssam"
+++

## Overview

A multi-threaded filesystem browser plugin for visual effects review tools. Browse large directory trees, detect image sequences, filter by time or version, preview media on hover, and load files into the host application — all without blocking the UI.

Supports xStudio and OpenRV. The core plugin (filesystem_browser/) is host-agnostic; the openrv_compat/ shim layer adapts it to OpenRV without modifying any shared code.

- **Non-blocking directory scan** — background thread pool with live progress; partial results stream to the UI as scanning proceeds
- **Image sequence detection** — groups frame ranges using [fileseq](https://github.com/justinfx/fileseq) (e.g. `shot.####.exr 1001-1100`)
- **Four view modes** — List, Tree, Grouped (compressed path tree), Thumbnails
- **ffmpeg thumbnails** — generated asynchronously by a 4-worker pool; persisted in a platform-appropriate cache directory across sessions; coalesced into a single UI refresh per 50 ms burst
- **Preview on hover** — single-click loads a clip temporarily; double-click commits it and discards the preview
- **Filtering** — free-text, modification-time bracket (last day / week / month), version filter (latest / latest 2)
- **Path autocomplete** — Tab-completion in the path field with arrow-key navigation
- **Quick Access** — pinned directories + recently visited history
- **Context menu** — Replace current media, Compare (A/B), Append, Copy path, Show in Finder
- **Environment-variable pins** — pre-populate bookmarks via `XSTUDIO_BROWSER_PINS`

## Requirements

| Requirement | Version |
|---|---|
| OpenRV | 2025.0 or later |
| Python | 3.10+ |
| OS | macOS 12+, Linux (RHEL 8+) |

## Installation

### OpenRV

1. Download the [plugin](https://github.com/richardssam/filesystem_browser/blob/main/rvplugin/filesystembrowser.zip)
2. Inside openrv goto **Preferences->Packages** and click on "Add packages" and select the above zip file.
3. Restart OpenRV.
4. Open **Preferences → Packages** and enable **Filesystem Browser**.

### Verify

After restarting, a **Filesystem Browser** menu option should appear in the **File** menu.

## Usage

See [https://github.com/richardssam/filesystem_browser](https://github.com/richardssam/filesystem_browser) for details on configuration and usage.

## Known Limitations

- Not tested on windows, but should be possible.

