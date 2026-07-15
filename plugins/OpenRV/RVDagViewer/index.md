+++
title       = "RV Dag Viewer"
description = "Browser for the RV DAG node network for OpenRV. This allows you to see what nodes exist, how they related to other nodes, and what properties are on each node."
date        = 2026-07-15T00:00:00Z
draft       = false

version = "1.0.0"
author  = "richardssam"
license = "Apache-2.0"

host_app = ["OpenRV"]
tags     = ["development"]

[params]
  repoUrl = "https://github.com/richardssam/RVDagViewer"
  repoOwner = "richardssam"
+++

## Overview

This is a openRV plugin for viewing the DAG network within OpenRV.

The dagViewer.py code is designed to be somewhat portable, with a interface class that allows it to be easily mapped to other frameworks.


## Requirements

| Requirement | Version |
|---|---|
| OpenRV | 2025.0 or later |
| Python | 3.10+ |
| OS | macOS 12+, Linux (RHEL 8+) |

## Installation

### OpenRV

1. Download the [plugin](https://github.com/richardssam/RVDagViewer/blob/main/dagviewer.zip)
2. Inside openrv goto **Preferences->Packages** and click on "Add packages" and select the above zip file.
3. Restart OpenRV.
4. Open **Preferences → Packages** and enable **DAG Viewer**.

### Verify

After restarting, a *Dag Viewer* should appear under the tools menu.

## Usage

See [https://github.com/richardssam/RVDagViewer](https://github.com/richardssam/RVDagViewer) for details on configuration and usage.

## Known Limitations

- None known.

