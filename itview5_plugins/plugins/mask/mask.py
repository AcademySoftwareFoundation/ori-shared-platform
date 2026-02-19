import os
import OpenImageIO as oiio
from dataclasses import dataclass
from PySide2 import QtCore, QtGui, QtWidgets
from mask.actions import Actions


@dataclass
class Mask:
    index: int
    name: str
    content: str


ITVIEW_MASK_IMAGE = "ITVIEW_MASK_IMAGE"
TOGGLE_MASK = "toggle_mask"


class MaskPlugin:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__viewport_api = self.__rpa.viewport_api
        self.__session_api = self.__rpa.session_api

        self.__masks = {}
        self.__current_mask = None
        self.__prev_mask = None
        self.__guess_mask_enabled = False

        self.__mask_menu = None
        self.__mask_ag = None

        self.__actions = Actions()
        self.__initialize_masks()
        self.__create_menu_bar()
        self.__connect_signals()

        self.__actions.toggle_mask.setProperty("hotkey_editor", True)
        self.__actions.cycle_mask.setProperty("hotkey_editor", True)

        self.__viewport_api.delegate_mngr.add_post_delegate(
            self.__viewport_api.set_mask, self.__update_mask)

        self.__session_api.delegate_mngr.add_post_delegate(
            self.__session_api.set_custom_session_attr, self.__post_set_custom_session_attr)

    def __set_toggle_mask_custom_attr(self, state):
        self.__rpa.session_api.set_custom_session_attr(
            TOGGLE_MASK, state)

    def __post_set_custom_session_attr(self, out, attr_id, value):
        if attr_id == TOGGLE_MASK:
            self.__toggle_mask(value)

    def __initialize_masks(self):
        mask_images = os.environ.get(ITVIEW_MASK_IMAGE)
        if mask_images:
            masks = mask_images.split(",")
            for mask in masks:
                content = mask.split(":")[0]
                name = mask.split(":")[1]
                self.__masks[name] = content

    def __create_menu_bar(self):
        plugins_menu = self.__main_window.get_plugins_menu()

        mask_controls_menu = QtWidgets.QMenu("Mask Controls", plugins_menu)
        mask_controls_menu.setTearOffEnabled(True)
        mask_controls_menu.addAction(self.__actions.toggle_mask)
        mask_controls_menu.addAction(self.__actions.cycle_mask)
        mask_controls_menu.addAction(self.__actions.guess_mask)
        mask_controls_menu.addSeparator()
        plugins_menu.addMenu(mask_controls_menu)

        self.__mask_menu = QtWidgets.QMenu("Select Mask", mask_controls_menu)
        mask_controls_menu.addMenu(self.__mask_menu)

    def __connect_signals(self):
        self.__actions.toggle_mask.triggered.connect(self.__set_toggle_mask_custom_attr)
        self.__actions.cycle_mask.triggered.connect(self.__cycle_mask)
        self.__actions.guess_mask.triggered.connect(self.__enable_guess_mask)

        self.__mask_menu.aboutToShow.connect(self.__populate_mask_menu)
        self.__mask_menu.triggered.connect(self.__select_mask)

    def __populate_mask_menu(self):
        if self.__mask_menu is None:
            return

        self.__mask_menu.clear()

        if not self.__masks:
            no_mask_found = self.__mask_menu.addAction("No masks defined")
            no_mask_found.setEnabled(False)
            return

        no_mask = self.__mask_menu.addAction("None")
        mask_data = Mask(index=0, name=no_mask.text(), content=None)
        no_mask.setData(mask_data)
        no_mask.setCheckable(True)
        self.__mask_menu.insertAction(self.__mask_menu.actions()[0], no_mask)

        for i, (name, mask) in enumerate(self.__masks.items()):
            action = self.__mask_menu.addAction(name)
            mask_data = Mask(index=i+1, name=name, content=mask)
            action.setData(mask_data)
            action.setCheckable(True)

        self.__mask_ag = QtWidgets.QActionGroup(self.__mask_menu)
        self.__mask_ag.setExclusive(True)
        self.__mask_ag.addAction(no_mask)
        for action in self.__mask_menu.actions():
            self.__mask_ag.addAction(action)

        if self.__current_mask is None:
            self.__current_mask = no_mask.data()
            no_mask.setChecked(True)
        else:
            for action in self.__mask_ag.actions():
                if self.__current_mask == action.data():
                    action.setChecked(True)
                    break

    def __toggle_mask(self, state):
        if not self.__mask_menu.actions():
            self.__populate_mask_menu()

        actions = self.__mask_menu.actions()
        if len(actions) < 2:
            return

        if state:
            if self.__prev_mask:
                action = actions[self.__prev_mask.index]
            else:
                action = actions[1]
            action.setChecked(True)
        else:
            self.__prev_mask = self.__current_mask
            for action in actions:
                if action.data().content is None:
                    action.setChecked(True)
                    break

        final_mask = self.__mask_ag.checkedAction().data()
        self.__set_mask(final_mask)

    def __cycle_mask(self):
        if not self.__mask_menu.actions():
            self.__populate_mask_menu()

        actions = self.__mask_menu.actions()
        if len(actions) < 2:
            return

        checked_mask = self.__mask_ag.checkedAction().data()

        if checked_mask.content is None or checked_mask.index == 0:
            # self.__toggle_mask(True)
            self.__set_toggle_mask_custom_attr(True)
        else:
            if checked_mask.index == len(actions) - 1:
                mask_index = 1
            else:
                mask_index = checked_mask.index + 1

            action = actions[mask_index]
            action.setChecked(True)
            mask = action.data()
            self.__set_mask(mask)

    def __enable_guess_mask(self, state):
        if self.__guess_mask_enabled == state:
            return
        self.__guess_mask_enabled = state

        if state:
            self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(
                self.__guess_mask, type=QtCore.Qt.QueuedConnection)
            c_id = self.__session_api.get_current_clip()
            self.__guess_mask(c_id)
        else:
            try:
                self.__session_api.SIG_CURRENT_CLIP_CHANGED.disconnect(
                    self.__guess_mask)
            except:
                pass

    def __guess_mask(self, clip_id):
        if clip_id is None:
            return
        playlist_id = self.__session_api.get_fg_playlist()
        if not playlist_id or not clip_id:
            return

        if not self.__mask_menu.actions():
            self.__populate_mask_menu()

        actions = self.__mask_menu.actions()
        if len(actions) < 2:
            return

        media_w, media_h = \
            self.__get_resolution(playlist_id, clip_id)

        match_found = False
        for action in actions:
            mask = action.data()
            if mask.content is None:
                continue
            if os.path.exists(mask.content):
                image_input = oiio.ImageInput.open(mask.content)
                mask_w = image_input.spec().width
                mask_h = image_input.spec().height

                if (media_w == mask_w) and (media_h == mask_h):
                    match_found = True
                    if action.data() == self.__current_mask:
                        return
                    else:
                        action.setChecked(True)
                        self.__set_mask(mask)
                        break

        # if none of the masks matched
        if not match_found:
            for action in actions:
                mask = action.data()
                if mask.content is None:
                    action.setChecked(True)
                    self.__set_mask(mask)
                    break

    def __get_resolution(self, playlist_id, clip_id):
        w, h = 0, 0
        resolution = self.__session_api.get_attr_value(
            clip_id, "resolution")
        w, h = resolution.split("x")
        w = int(w.strip())
        h = int(h.strip())
        return w, h

    def __select_mask(self, action):
        selected_mask = action.data()
        if self.__current_mask == selected_mask:
            return

        self.__set_mask(selected_mask)

    def __set_mask(self, mask:Mask):
        self.__current_mask = mask

        if self.__current_mask.content is None:
            self.__actions.toggle_mask.setChecked(False)
        else:
            self.__actions.toggle_mask.setChecked(True)

        self.__viewport_api.set_mask(self.__current_mask.content)
        self.__viewport_api.display_msg(f"Mask: {self.__current_mask.name}")

    def __update_mask(self, out, mask):
        if mask is None:
            self.__actions.toggle_mask.setChecked(False)
            if self.__current_mask and self.__current_mask.index != 0:
                self.__prev_mask = self.__current_mask
        else:
            self.__actions.toggle_mask.setChecked(True)
            for i, (name, m) in enumerate(self.__masks.items()):
                if m == mask:
                    self.__current_mask = Mask(index=i+1, name=name, content=m)
                    if not self.__mask_menu.actions():
                        self.__populate_mask_menu()
                    for action in self.__mask_ag.actions():
                        action.setChecked(action.data() == self.__current_mask)
