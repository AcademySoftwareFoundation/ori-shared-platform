import sys
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
                              QTreeWidgetItem, QLineEdit, QPushButton, QLabel,
                              QHeaderView, QKeySequenceEdit, QDialog,
                              QDialogButtonBox, QMessageBox, QApplication,
                              QMainWindow, QMenuBar, QMenu, QAction, QSplitter)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QKeySequence, QFont
from itview.skin.widgets.itv_dock_widget import ItvDockWidget


class HotkeyEditDialog(QDialog):
    """Dialog for editing a hotkey sequence"""

    def __init__(self, action_name, current_sequence, original_sequence=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Hotkey - {action_name}")
        self.setModal(True)
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        # Action name label
        name_label = QLabel(f"Action: {action_name}")
        name_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(name_label)

        # Original hotkey label
        if original_sequence is not None:
            original_text = original_sequence.toString() if original_sequence else "None"
            original_label = QLabel(f"Original Hotkey: {original_text}")
            layout.addWidget(original_label)

        # Current hotkey label
        current_text = current_sequence.toString() if current_sequence else "None"
        current_label = QLabel(f"Current Hotkey: {current_text}")
        layout.addWidget(current_label)

        # Key sequence editor
        layout.addWidget(QLabel("New Hotkey:"))
        self.key_edit = QKeySequenceEdit()
        self.key_edit.setKeySequence(current_sequence if current_sequence else QKeySequence())
        layout.addWidget(self.key_edit)

        # Button layout
        button_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear Hotkey")
        clear_btn.clicked.connect(lambda: self.key_edit.setKeySequence(QKeySequence()))
        button_layout.addWidget(clear_btn)

        # Revert button (only if original sequence is provided)
        if original_sequence is not None:
            revert_btn = QPushButton("Revert to Original")
            revert_btn.clicked.connect(lambda: self.key_edit.setKeySequence(original_sequence))
            button_layout.addWidget(revert_btn)

        layout.addLayout(button_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_key_sequence(self):
        return self.key_edit.keySequence()


class HotkeyEditor(QWidget):
    """Widget for editing hotkeys of QActions throughout the application"""

    hotkey_changed = Signal(QAction, QKeySequence)  # Emitted when a hotkey is changed

    def __init__(self, parent=None):
        super().__init__(parent)

    def itview_init(self, itview):
        self.main_window = itview.main_window
        self.actions_data = []  # Store (context_name, action, parent_widget) tuples
        self.original_hotkeys = {}  # Store original hotkeys: {action: QKeySequence}

        self.setup_ui()

        dock_widget = ItvDockWidget("Hotkey Editor", self.main_window)
        dock_widget.setWidget(self)
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
        dock_widget.hide()

        self.__toggle_action = dock_widget.toggleViewAction()
        plugins_menu = self.main_window.get_plugins_menu()
        hotkey_editor_menu = plugins_menu.addMenu("Hotkey Editor")
        hotkey_editor_menu.setTearOffEnabled(True)
        hotkey_editor_menu.addAction(self.__toggle_action)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Hotkey Editor")
        title.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(title)

        # Filter section
        filter_layout = QVBoxLayout()

        # Hotkey filter with key sequence editor
        hotkey_filter_layout = QHBoxLayout()
        hotkey_filter_layout.addWidget(QLabel("Filter by hotkey:"))

        self.hotkey_filter_edit = QKeySequenceEdit()
        self.hotkey_filter_edit.keySequenceChanged.connect(self.filter_tree)
        hotkey_filter_layout.addWidget(self.hotkey_filter_edit)

        # Clear hotkey filter button
        clear_hotkey_filter_btn = QPushButton("Clear")
        clear_hotkey_filter_btn.setMaximumWidth(60)
        clear_hotkey_filter_btn.clicked.connect(self.clear_hotkey_filter)
        hotkey_filter_layout.addWidget(clear_hotkey_filter_btn)

        filter_layout.addLayout(hotkey_filter_layout)

        # Action name filter
        name_filter_layout = QHBoxLayout()
        name_filter_layout.addWidget(QLabel("Filter by action name:"))

        self.name_filter_edit = QLineEdit()
        self.name_filter_edit.setPlaceholderText("Type action name to filter (e.g., Copy, Save, etc.)")
        self.name_filter_edit.textChanged.connect(self.filter_tree)
        name_filter_layout.addWidget(self.name_filter_edit)

        filter_layout.addLayout(name_filter_layout)

        # Filter controls
        filter_controls_layout = QHBoxLayout()

        clear_filters_btn = QPushButton("Clear All Filters")
        clear_filters_btn.clicked.connect(self.clear_filters)
        filter_controls_layout.addWidget(clear_filters_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_actions)
        filter_controls_layout.addWidget(refresh_btn)

        filter_controls_layout.addStretch()  # Push buttons to the left

        filter_layout.addLayout(filter_controls_layout)

        layout.addLayout(filter_layout)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Context / Action", "Hotkey", "Description"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tree.itemDoubleClicked.connect(self.edit_hotkey)
        layout.addWidget(self.tree)

        # Button layout
        button_layout = QHBoxLayout()

        edit_btn = QPushButton("Edit Selected Hotkey")
        edit_btn.clicked.connect(self.edit_selected_hotkey)
        button_layout.addWidget(edit_btn)

        revert_btn = QPushButton("Revert to Original")
        revert_btn.clicked.connect(self.revert_selected_hotkey)
        button_layout.addWidget(revert_btn)

        revert_all_btn = QPushButton("Revert All")
        revert_all_btn.clicked.connect(self.revert_all_hotkeys)
        button_layout.addWidget(revert_all_btn)

        layout.addLayout(button_layout)

    def clear_hotkey_filter(self):
        """Clear the hotkey filter input"""
        self.hotkey_filter_edit.setKeySequence(QKeySequence())

    def find_all_actions(self, widget, context_name="", actions_list=None):
        """Recursively find all QActions in widget hierarchy"""
        if actions_list is None:
            actions_list = []

        # Get widget's class name for context
        if not context_name:
            context_name = widget.__class__.__name__

        # Find actions directly associated with this widget
        try:
            actions = widget.actions()
            for action in actions:
                if not self.__is_hotkey_editor_action(action): continue
                if hasattr(action, 'text') and action.text():  # Only include actions with text
                    actions_list.append((context_name, action, widget))
        except (TypeError, AttributeError):
            # Widget doesn't have actions or actions() is not callable
            pass

        # Check for menu bar actions (if it's a main window)
        if hasattr(widget, 'menuBar'):
            try:
                menubar = widget.menuBar()
                if menubar:
                    self.find_menu_actions(menubar, f"{context_name} Menu", actions_list)
            except (TypeError, AttributeError, RuntimeError):
                pass

        # Check for toolbar actions
        if hasattr(widget, 'toolBars'):
            try:
                for toolbar in widget.toolBars():
                    if toolbar:  # Check if toolbar still exists
                        toolbar_name = toolbar.windowTitle() or "Toolbar"
                        try:
                            for action in toolbar.actions():
                                if not self.__is_hotkey_editor_action(action): continue
                                if hasattr(action, 'text') and action.text():
                                    actions_list.append((f"{context_name} - {toolbar_name}", action, toolbar))
                        except (TypeError, AttributeError, RuntimeError):
                            pass
            except (TypeError, AttributeError, RuntimeError):
                pass

        # Recursively check child widgets
        try:
            for child in widget.findChildren(QWidget):
                if not child:  # Skip if child is None or deleted
                    continue

                child_name = child.windowTitle()
                if not child_name:
                    child_name = child.__class__.__name__

                child_context = f"{context_name} - {child_name}"
                # Get actions from child widget
                try:
                    # Check if child has actions method and it's callable
                    if hasattr(child, 'actions'):
                        actions_method = getattr(child, 'actions')
                        if callable(actions_method):
                            child_actions = actions_method()
                            for action in child_actions:
                                if not self.__is_hotkey_editor_action(action): continue
                                if hasattr(action, 'text') and action.text():
                                    actions_list.append((child_context, action, child))
                except (TypeError, AttributeError, RuntimeError):
                    # Skip this child if we can't get its actions
                    pass

                # Check if child has a context menu
                try:
                    if hasattr(child, 'contextMenuPolicy') and child.contextMenuPolicy() != Qt.NoContextMenu:
                        # Note: Context menu actions are harder to detect without actually triggering the menu
                        pass
                except (TypeError, AttributeError, RuntimeError):
                    pass
        except (TypeError, AttributeError, RuntimeError):
            pass

        return actions_list

    def store_original_hotkeys(self):
        """Store original hotkeys for all actions (only if not already stored)"""
        for context_name, action, parent_widget in self.actions_data:
            if action not in self.original_hotkeys:
                # Store the original shortcut
                self.original_hotkeys[action] = QKeySequence(action.shortcut())

    def find_menu_actions(self, menu_or_menubar, context_name, actions_list):
        """Find actions in menus and submenus"""
        try:
            if hasattr(menu_or_menubar, 'actions'):
                actions_method = getattr(menu_or_menubar, 'actions')
                if callable(actions_method):
                    for action in actions_method():
                        if not action:  # Skip None actions
                            continue

                        if not self.__is_hotkey_editor_action(action): continue
                        if hasattr(action, 'menu') and action.menu():  # Submenu
                            submenu_name = action.text().replace('&', '') if hasattr(action, 'text') else "Submenu"
                            self.find_menu_actions(action.menu(), f"{context_name} - {submenu_name}", actions_list)
                        elif hasattr(action, 'text') and action.text() and not action.isSeparator():
                            actions_list.append((context_name, action, menu_or_menubar))
        except (TypeError, AttributeError, RuntimeError):
            # Skip if we can't access the menu or its actions
            pass

    def refresh_actions(self):
        """Refresh the list of all actions"""
        try:
            self.actions_data = self.find_all_actions(self.main_window)
            # Store original hotkeys if not already stored
            self.store_original_hotkeys()
            self.populate_tree()
        except Exception as e:
            print(f"Error refreshing actions: {e}")
            # Try to populate with whatever data we have
            self.populate_tree()

    def populate_tree(self):
        """Populate the tree widget with actions grouped by context"""
        self.tree.clear()

        # Group actions by context
        contexts = {}
        for context_name, action, parent_widget in self.actions_data:
            if context_name not in contexts:
                contexts[context_name] = []
            contexts[context_name].append((action, parent_widget))

        # Create tree items
        for context_name, actions in contexts.items():
            context_item = QTreeWidgetItem(self.tree)
            context_item.setText(0, context_name)
            context_item.setFont(0, QFont("", 9, QFont.Bold))
            context_item.setExpanded(True)

            for action, parent_widget in actions:
                action_item = QTreeWidgetItem(context_item)
                action_item.setText(0, action.text().replace('&', ''))

                # Hotkey
                shortcut = action.shortcut()
                hotkey_text = shortcut.toString() if not shortcut.isEmpty() else "None"
                action_item.setText(1, hotkey_text)

                # Description/Status tip
                description = action.statusTip() or action.toolTip() or action.whatsThis() or ""
                action_item.setText(2, description)

                # Store action reference in item data
                action_item.setData(0, Qt.UserRole, action)
                action_item.setData(1, Qt.UserRole, parent_widget)

                # Add visual indicator if hotkey has been changed from original
                original_shortcut = self.original_hotkeys.get(action, QKeySequence())
                current_shortcut = action.shortcut()
                if original_shortcut != current_shortcut:
                    # Mark as modified with different text color or style
                    font = action_item.font(1)
                    font.setBold(True)
                    action_item.setFont(1, font)
                    action_item.setToolTip(1, f"Original: {original_shortcut.toString() or 'None'}")
                else:
                    # Reset to normal style
                    font = action_item.font(1)
                    font.setBold(False)
                    action_item.setFont(1, font)
                    action_item.setToolTip(1, "")

    def filter_tree(self):
        """Filter tree items based on hotkey sequence and action name"""
        hotkey_filter_sequence = self.hotkey_filter_edit.keySequence()
        hotkey_filter = hotkey_filter_sequence.toString().lower()
        name_filter = self.name_filter_edit.text().lower()

        if not hotkey_filter and not name_filter:
            # Show all items
            for i in range(self.tree.topLevelItemCount()):
                context_item = self.tree.topLevelItem(i)
                context_item.setHidden(False)
                for j in range(context_item.childCount()):
                    context_item.child(j).setHidden(False)
            return

        # Hide/show items based on filters
        for i in range(self.tree.topLevelItemCount()):
            context_item = self.tree.topLevelItem(i)
            has_visible_children = False

            for j in range(context_item.childCount()):
                action_item = context_item.child(j)
                hotkey_text = action_item.text(1).lower()
                action_name = action_item.text(0).lower()

                # Check if hotkey matches filter (if hotkey filter is provided)
                # For exact sequence matching, compare the actual sequences
                hotkey_matches = True
                if not hotkey_filter_sequence.isEmpty():
                    action = action_item.data(0, Qt.UserRole)
                    if action:
                        action_sequence = action.shortcut()
                        # Check for exact match or partial match in string representation
                        hotkey_matches = (hotkey_filter_sequence == action_sequence or
                                        hotkey_filter in hotkey_text)
                    else:
                        hotkey_matches = hotkey_filter in hotkey_text

                # Check if action name matches filter (if name filter is provided)
                name_matches = not name_filter or name_filter in action_name

                # Item is visible if it matches all active filters
                matches = hotkey_matches and name_matches
                action_item.setHidden(not matches)

                if matches:
                    has_visible_children = True

            # Hide context if no children match
            context_item.setHidden(not has_visible_children)

    def clear_filters(self):
        """Clear all filter text boxes"""
        self.hotkey_filter_edit.setKeySequence(QKeySequence())
        self.name_filter_edit.clear()
        # filter_tree will be called automatically due to signals

    def edit_hotkey(self, item, column):
        """Edit hotkey when item is double-clicked"""
        if item.parent() is None:  # Context item, not action item
            return

        action = item.data(0, Qt.UserRole)
        if not action:
            return

        self.show_edit_dialog(action, item)

    def edit_selected_hotkey(self):
        """Edit hotkey of selected item"""
        current_item = self.tree.currentItem()
        if not current_item or current_item.parent() is None:
            QMessageBox.information(self, "No Selection", "Please select an action to edit.")
            return

        action = current_item.data(0, Qt.UserRole)
        if action:
            self.show_edit_dialog(action, current_item)

    def show_edit_dialog(self, action, tree_item):
        """Show dialog to edit action's hotkey"""
        action_name = action.text().replace('&', '')
        current_sequence = action.shortcut()
        original_sequence = self.original_hotkeys.get(action)

        dialog = HotkeyEditDialog(action_name, current_sequence, original_sequence, self)

        if dialog.exec_() == QDialog.Accepted:
            new_sequence = dialog.get_key_sequence()

            # Set new shortcut
            action.setShortcut(new_sequence)

            # Update tree item
            hotkey_text = new_sequence.toString() if not new_sequence.isEmpty() else "None"
            tree_item.setText(1, hotkey_text)

            # Emit signal
            self.hotkey_changed.emit(action, new_sequence)

            # Refresh to show any changes to conflicting actions
            self.refresh_actions()

    def revert_selected_hotkey(self):
        """Revert the selected action's hotkey to its original value"""
        current_item = self.tree.currentItem()
        if not current_item or current_item.parent() is None:
            QMessageBox.information(self, "No Selection", "Please select an action to revert.")
            return

        action = current_item.data(0, Qt.UserRole)
        if not action:
            return

        if action not in self.original_hotkeys:
            QMessageBox.information(self, "No Original Hotkey",
                                  "No original hotkey stored for this action.")
            return

        original_sequence = self.original_hotkeys[action]
        current_sequence = action.shortcut()

        if original_sequence == current_sequence:
            QMessageBox.information(self, "Already Original",
                                  "This action is already using its original hotkey.")
            return

        # Revert to original
        action.setShortcut(original_sequence)

        # Update tree item
        hotkey_text = original_sequence.toString() if not original_sequence.isEmpty() else "None"
        current_item.setText(1, hotkey_text)

        # Emit signal
        self.hotkey_changed.emit(action, original_sequence)

        # Refresh to update visual indicators
        self.populate_tree()

        QMessageBox.information(self, "Hotkey Reverted",
                              f"Hotkey for '{action.text().replace('&', '')}' has been reverted to: "
                              f"{original_sequence.toString() or 'None'}")

    def revert_all_hotkeys(self):
        """Revert all actions to their original hotkeys"""
        if not self.original_hotkeys:
            QMessageBox.information(self, "No Original Hotkeys",
                                  "No original hotkeys are stored.")
            return

        # Count how many will actually change
        changes_count = 0
        for action, original_sequence in self.original_hotkeys.items():
            if action.shortcut() != original_sequence:
                changes_count += 1

        if changes_count == 0:
            QMessageBox.information(self, "No Changes",
                                  "All actions are already using their original hotkeys.")
            return

        reply = QMessageBox.question(
            self, "Revert All Hotkeys",
            f"This will revert {changes_count} action(s) to their original hotkeys. "
            "This may cause hotkey conflicts that will be resolved by removing duplicates.\n\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # First pass: revert all to original
        conflicts = []
        for action, original_sequence in self.original_hotkeys.items():
            if action.shortcut() != original_sequence:
                action.setShortcut(original_sequence)
                self.hotkey_changed.emit(action, original_sequence)

        # Second pass: resolve conflicts by finding duplicates and clearing them
        sequence_to_actions = {}
        for action, original_sequence in self.original_hotkeys.items():
            if not original_sequence.isEmpty():
                seq_str = original_sequence.toString()
                if seq_str not in sequence_to_actions:
                    sequence_to_actions[seq_str] = []
                sequence_to_actions[seq_str].append(action)

        # Clear duplicates (keep first, clear others)
        conflict_resolved = 0
        for seq_str, actions in sequence_to_actions.items():
            if len(actions) > 1:
                for action in actions[1:]:  # Keep first, clear others
                    action.setShortcut(QKeySequence())
                    self.hotkey_changed.emit(action, QKeySequence())
                    conflict_resolved += 1

        # Refresh display
        self.populate_tree()

        message = f"Reverted {changes_count} action(s) to original hotkeys."
        if conflict_resolved > 0:
            message += f"\nResolved {conflict_resolved} conflict(s) by clearing duplicate hotkeys."

        QMessageBox.information(self, "Revert Complete", message)

    def __is_hotkey_editor_action(self, action):
        is_hotkey_editor_action = action.property("hotkey_editor")
        if is_hotkey_editor_action is None: is_hotkey_editor_action = False
        return is_hotkey_editor_action
