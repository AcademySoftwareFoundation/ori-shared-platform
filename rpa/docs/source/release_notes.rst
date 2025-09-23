Release Notes
=============

.. contents::
   :local:
   :depth: 1

===========================
Version History and Changes
===========================

This document contains the release notes and changelog for the RPA (Review Plugin API) project, documenting all significant changes, new features, bug fixes, and improvements across different releases.

==============
Latest Release
==============

Released: 2024-12-28
--------------------

**Major Features Added:**

* **Session Auto Saver Widget** - New widget for automatic session autosaves, providing continuous backup functionality for RPA sessions
* **Frame Editor Widget** - New widget for per-clip frame edits, enabling precise frame-level modifications
* **Playlist Export Support** - Added support for exporting playlists into video files for external use
* **Enhanced Color Correction** - Added color correction region shape borders with transient points for better visual feedback
* **Annotation Improvements** - Added provision for note markers in annotations for enhanced documentation
* **Timeline Functionality** - Extended timeline functionality with EDL (Edit Decision List) usage support
* **Viewport Enhancements** - Added viewport image rotation option for better media viewing
* **OpenGL Overlay Support** - Added support for OpenGL overlays in RPA widgets

**Technical Improvements:**

* Fixed SSBO binding index to respect GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS to avoid GL_INVALID_VALUE errors
* Various minor bug fixes and performance improvements across RPA widgets

=================
Previous Releases
=================

Released: November 2024
-----------------------

**New Features:**

* **Playlists Creator Widget** - Added example RPA widget for creating and managing playlists
* **Documentation Infrastructure** - Improved documentation build system and ReadTheDocs integration

**Bug Fixes:**

* Fixed documentation build directory issues
* Resolved ReadTheDocs YAML configuration problems
* Fixed Sphinx dependency issues
* Corrected RTD build errors and indentation problems

**Infrastructure:**

* Enhanced build tools configuration
* Improved CI/CD pipeline for documentation deployment
* Added proper requirements for documentation builds


Released: October 2024
----------------------

**Initial Public Release:**

* **Core RPA Framework** - Initial release of the RPA (Remote Production Assistant) platform
* **Widget System** - Comprehensive widget system for RV integration
* **API Modules** - Complete set of API modules for session management, annotations, color correction, timeline, and viewport control
* **OpenRV Integration** - Full integration with OpenRV for professional video editing workflows
* **Session State Management** - Robust session state management with support for playlists, clips, and annotations
* **Documentation** - Complete documentation system with API references and user guides

**Core Components:**

* Annotation API with drawing tools and color picker
* Color correction tools with advanced controls
* Session management with playlist and clip controllers
* Timeline API with EDL support
* Viewport API for media display and manipulation
* Interactive modes and background processing
* Media path overlay and session assistant widgets


For more information about recent changes and detailed technical specifications, please refer to the individual API module documentation and the git commit history.
