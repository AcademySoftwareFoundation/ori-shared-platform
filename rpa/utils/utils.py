try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets
import re
import os
import subprocess
from typing import List


FONT_WEIGHT_MAP = {
    0: "Thin",
    12: "ExtraLight",
    25: "Light",
    50: "Regular",
    57: "Medium",
    63: "DemiBold",
    75: "Bold",
    81: "ExtraBold",
    87: "Black"
}

FONT_STYLE_MAP = {
    0: "Normal",
    1: "Italic",
    2: "Oblique"
}


def find_font_path(font:QtGui.QFont):
    final_font_path = ""
    font_db = QtGui.QFontDatabase()

    font_family = font.family()
    no_bracket_font_family = re.sub(r"\[.*?\]", "", font_family).strip()

    style_name = font_db.styleString(font)
    style_name = "Regular" if style_name == "Normal" else style_name
    if not style_name:
        return final_font_path

    font_style = font.style()
    font_style_str = FONT_STYLE_MAP.get(font_style, "Normal")
    font_bold = font.bold()
    font_weight = font.weight()
    font_weight_str = FONT_WEIGHT_MAP.get(font_weight, "Regular")

    try:
        cmd = ["fc-list", ":", "file", "family", "style"]
        output = subprocess.check_output(cmd, text=True)
    except:
        print("Can not use font config; Using default font instead")
        return final_font_path

    candidates = []
    for i, line in enumerate(output.splitlines()):
        font_parts = line.split(":", 2)
        if len(font_parts) < 3:
            continue

        font_path, families, styles = font_parts
        families_list = [f.strip() for f in families.split(',')]
        styles_list = [s.strip().removeprefix("style=") for s in styles.split(',')]

        if font_family in families_list or no_bracket_font_family in families_list:
            candidates.append([font_path, styles_list])

    exact_matches = []
    matches = []
    for candidate in candidates:
        font_path, styles_list = candidate
        if style_name in styles_list and len(styles_list) == 1:
            exact_matches.append(font_path)
        elif style_name in styles_list:
            matches.append(font_path)

    # if exact matches or matches found, return the first match right away
    if exact_matches:
        return exact_matches[0]
    elif matches:
        return matches[0]

    # else continue to narrow down
    style_candidates = []
    for candidate in candidates:
        _, styles_list = candidate

        if font.style() == QtGui.QFont.StyleNormal:
            if not any("Italic" in elem or "Oblique" in elem for elem in styles_list):
                style_candidates.append(candidate)
        elif font.style() == QtGui.QFont.StyleItalic:
            if any(font_style_str in style for style in styles_list):
                style_candidates.append(candidate)
        elif font.style() == QtGui.QFont.StyleOblique:
            if any(font_style_str in style for style in styles_list):
                style_candidates.append(candidate)

    specific_candidates = []
    for style_candidate in style_candidates:
        _, styles_list = style_candidate
        bold_style = any("Bold" in style for style in styles_list)
        if (font_bold and bold_style) or (not font_bold and not bold_style):
            specific_candidates.append(style_candidate)

    weight_match_candidates = []
    for final_candidate in specific_candidates:
        _, styles_list = final_candidate
        if any(font_weight_str in style for style in styles_list):
            weight_match_candidates.append(final_candidate)

    final_candidates = []
    for weight_match_candidate in weight_match_candidates:
        _, styles_list = weight_match_candidate
        if not any("Condensed" in style for style in styles_list):
            final_candidates.append(weight_match_candidate)

    font_paths = []
    if not final_candidates:
        if not weight_match_candidates:
            font_paths = [ttf_path for ttf_path, _ in specific_candidates]
        else:
            font_paths = [ttf_path for ttf_path, _ in weight_match_candidates]
    else:
        font_paths = [ttf_path for ttf_path, _ in final_candidates]

    ttf_paths = [font_path for font_path in font_paths if font_path.endswith(".ttf")]
    non_ttf_paths = [font_path for font_path in font_paths if not font_path.endswith(".ttf")]

    if ttf_paths:
        final_font_path = ttf_paths[0]
    else:
        final_font_path = "" if not non_ttf_paths else non_ttf_paths[0]
    return final_font_path


def get_offset_id(ids:List[str], index:int, offset:int)->str:
    if len(ids) == 1:
        new_index = 0
    elif index == len(ids) - 1:
        new_index = 0 if offset > 0 else index - 1
    else:
        new_index = index + offset

    if new_index == -1:
        new_index = len(ids) - 1

    new_id = ids[new_index]
    return new_id


def __goto_clip(rpa, offset:int):
    clip_id = rpa.session_api.get_current_clip()
    if clip_id is None:
        return

    reselect = False
    playlist_id = rpa.session_api.get_playlist_of_clip(clip_id)
    selected_clip_ids = rpa.session_api.get_active_clips(playlist_id)
    clip_ids = rpa.session_api.get_clips(playlist_id)

    if not selected_clip_ids:
        selected_clip_ids = clip_ids
    elif len(selected_clip_ids) == 1:
        selected_clip_ids = clip_ids
        reselect = True

    current_index = selected_clip_ids.index(clip_id)

    new_clip_id = \
        get_offset_id(selected_clip_ids, current_index, offset)

    if clip_id != new_clip_id:
        rpa.session_api.set_current_clip(new_clip_id)
        if reselect:
            rpa.session_api.set_active_clips(
                playlist_id, [new_clip_id])


def goto_prev_clip(rpa):
    __goto_clip(rpa, -1)


def goto_next_clip(rpa):
    __goto_clip(rpa, 1)


def get_current_clip_frame(rpa):
    clip_frame = rpa.timeline_api.get_clip_frames(
        [rpa.timeline_api.get_current_frame()])
    if not clip_frame: return -1
    else:
        [clip_frame] = clip_frame
        if type(clip_frame) is not tuple: return -1
        return clip_frame[1]


def undo_annotations(rpa):
    cguid = rpa.session_api.get_current_clip()
    current_frame = get_current_clip_frame(rpa)
    rpa.annotation_api.undo(cguid, current_frame)


def redo_annotations(rpa):
    cguid = rpa.session_api.get_current_clip()
    current_frame = get_current_clip_frame(rpa)
    rpa.annotation_api.redo(cguid, current_frame)


def goto_nearest_feedback_frame(rpa, forward=True):
    playlist_id = rpa.session_api.get_fg_playlist()
    clip_id = rpa.session_api.get_current_clip()
    if not playlist_id or not clip_id:
        return False
    current_frame = rpa.timeline_api.get_current_frame()
    clip_ids = rpa.session_api.get_clips(playlist_id)
    num_of_clips = len(clip_ids)
    def get_unique_values(l1, l2):
        unique_values = set(l1).union(set(l2))
        return sorted(unique_values)
    for ii, i in enumerate(range(num_of_clips+1)):
        clip_index = (clip_ids.index(clip_id) + (i if forward else -i)) % num_of_clips
        new_clip_id = clip_ids[clip_index]
        annotation_frames = rpa.annotation_api.get_rw_frames(new_clip_id) \
                            + rpa.annotation_api.get_ro_frames(new_clip_id)
        cc_frames = rpa.color_api.get_rw_frames(new_clip_id) \
                    + rpa.color_api.get_ro_frames(new_clip_id)
        frames = get_unique_values(annotation_frames, cc_frames)
        if not frames: continue
        seq_frames = rpa.timeline_api.get_seq_frames(new_clip_id, frames)
        if not seq_frames: continue
        first_seq_frames_only = [seqs[0] for _, seqs in seq_frames]
        seq_frames_only = first_seq_frames_only if forward else list(reversed(first_seq_frames_only))
        for frame in seq_frames_only:
            if frame == -1:
                continue
            if new_clip_id != clip_id:
                rpa.session_api.set_current_clip(new_clip_id)
                rpa.timeline_api.goto_frame(frame)
                return
            if forward:
                if (ii == 0 and frame > current_frame) \
                        or (ii != 0 and frame < current_frame):
                    rpa.timeline_api.goto_frame(frame)
                    return
            else:
                if (ii == 0 and frame < current_frame) \
                        or (ii != 0 and frame > current_frame):
                    rpa.timeline_api.goto_frame(frame)
                    return
    return


def clear_current_frame_annotations(rpa):
    cguid = rpa.session_api.get_current_clip()
    current_frame = get_current_clip_frame(rpa)
    rpa.annotation_api.clear_frame(cguid, current_frame)
