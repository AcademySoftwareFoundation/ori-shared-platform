"""
xStudio Review Notes Exporter — exports session annotations to JSON or CSV.
"""

import csv
import json
import os

import xstudio.api as xs


SUPPORTED_FORMATS = ("json", "csv")


class ReviewNotesExporter:
    def __init__(self, session):
        self._session = session

    def collect(self) -> list[dict]:
        annotations = []
        for shot in self._session.shots():
            for note in shot.annotations():
                annotations.append(
                    {
                        "name": shot.name,
                        "frame": note.frame,
                        "timecode": note.timecode,
                        "author": note.author,
                        "note": note.text,
                        "color": note.color_hex,
                    }
                )
        return annotations

    def export(self, dest_path: str, fmt: str = "json") -> int:
        if fmt not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format {fmt!r}. Choose from {SUPPORTED_FORMATS}")

        annotations = self.collect()

        if fmt == "json":
            payload = {
                "session": os.path.basename(self._session.path),
                "shots": annotations,
            }
            with open(dest_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)

        elif fmt == "csv":
            fieldnames = ["name", "frame", "timecode", "author", "note"]
            with open(dest_path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(annotations)

        return len(annotations)


def create_plugin(session):
    return ReviewNotesExporter(session)
