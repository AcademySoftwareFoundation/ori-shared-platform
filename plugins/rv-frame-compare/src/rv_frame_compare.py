"""
RV Frame Compare — dockable side-by-side comparison panel for OpenRV.
Supports wipe, difference, and overlay modes across two user-selected sources.
"""

import rv.commands as rvc
import rv.rvtypes as rvt


MODES = ("wipe", "difference", "overlay")


class FrameComparePlugin(rvt.MinorMode):
    def __init__(self):
        rvt.MinorMode.__init__(self)
        self._mode = "wipe"
        self._source_a = None
        self._source_b = None
        self._opacity = 0.5
        self._amplify = 1.0

    def init(self, name, globalEventTable, localEventTable, menu):
        rvt.MinorMode.init(
            self,
            name,
            globalEventTable,
            localEventTable,
            menu,
        )

    def set_mode(self, mode: str):
        if mode not in MODES:
            raise ValueError(f"Unknown mode: {mode!r}. Choose from {MODES}")
        self._mode = mode
        self._apply()

    def set_sources(self, source_a: str, source_b: str):
        self._source_a = source_a
        self._source_b = source_b
        self._apply()

    def set_opacity(self, value: float):
        self._opacity = max(0.0, min(1.0, value))
        self._apply()

    def set_amplify(self, value: float):
        self._amplify = max(0.1, value)
        self._apply()

    def _apply(self):
        if not (self._source_a and self._source_b):
            return
        # Dispatch to OpenRV display pipeline — stub for test plugin
        rvc.sendInternalEvent(
            "frame-compare-update",
            f"{self._mode}:{self._source_a}:{self._source_b}:"
            f"{self._opacity}:{self._amplify}",
        )


def createMode():
    return FrameComparePlugin()
