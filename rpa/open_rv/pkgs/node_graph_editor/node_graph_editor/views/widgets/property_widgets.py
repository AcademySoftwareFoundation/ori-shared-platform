#
# Copyright (C) 2024  RPA Workspace
#
# SPDX-License-Identifier: Apache-2.0
#
"""
Property Widget Factory - Creates appropriate UI widgets for different property types.

Follows the Factory Pattern and Interface Segregation Principle (ISP).
"""

from typing import Any, Optional, Callable

try:
    from PySide6.QtWidgets import (
        QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox,
        QDoubleSpinBox, QLineEdit, QPushButton, QCheckBox
    )
    from PySide6.QtCore import Signal, Qt
except:
    from PySide2.QtWidgets import (
        QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox,
        QDoubleSpinBox, QLineEdit, QPushButton, QCheckBox
    )
    from PySide2.QtCore import Signal, Qt


class PropertyWidgetBase(QWidget):
    """
    Base class for property editor widgets.

    Follows OCP: Extensible for new property types without modifying existing code.
    Follows ISP: Defines minimal interface for property widgets.
    """

    # Signal emitted when value changes: (property_name, new_value)
    valueChanged = Signal(str, object)

    # Signal emitted when reset is requested
    resetRequested = Signal(str)

    def __init__(self, property_name: str, property_type: str, parent=None):
        super().__init__(parent)
        self.property_name = property_name
        self.property_type = property_type
        self._setup_ui()

    def _setup_ui(self):
        """Setup the widget UI. Override in subclasses."""
        pass

    def set_value(self, value: Any):
        """Set the widget's value. Override in subclasses."""
        raise NotImplementedError

    def get_value(self) -> Any:
        """Get the widget's current value. Override in subclasses."""
        raise NotImplementedError


class IntPropertyWidget(PropertyWidgetBase):
    """Widget for editing integer properties."""

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Label
        self.label = QLabel(self.property_name)
        self.label.setMinimumWidth(150)
        layout.addWidget(self.label)

        # SpinBox
        self.spinbox = QSpinBox()
        self.spinbox.setRange(-2147483648, 2147483647)  # int32 range
        self.spinbox.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.spinbox, 1)

        # Reset button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setMaximumWidth(30)
        self.reset_btn.setToolTip("Reset to default")
        self.reset_btn.clicked.connect(lambda: self.resetRequested.emit(self.property_name))
        layout.addWidget(self.reset_btn)

    def set_value(self, value: Any):
        if isinstance(value, (list, tuple)) and len(value) > 0:
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(int(value[0]))
            self.spinbox.blockSignals(False)
        elif isinstance(value, (int, float)):
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(int(value))
            self.spinbox.blockSignals(False)

    def get_value(self) -> int:
        return self.spinbox.value()

    def _on_value_changed(self, value):
        self.valueChanged.emit(self.property_name, [value])


class FloatPropertyWidget(PropertyWidgetBase):
    """Widget for editing float properties."""

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Label
        self.label = QLabel(self.property_name)
        self.label.setMinimumWidth(150)
        layout.addWidget(self.label)

        # DoubleSpinBox
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(-1e10, 1e10)
        self.spinbox.setDecimals(4)
        self.spinbox.setSingleStep(0.1)
        self.spinbox.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.spinbox, 1)

        # Reset button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setMaximumWidth(30)
        self.reset_btn.setToolTip("Reset to default")
        self.reset_btn.clicked.connect(lambda: self.resetRequested.emit(self.property_name))
        layout.addWidget(self.reset_btn)

    def set_value(self, value: Any):
        if isinstance(value, (list, tuple)) and len(value) > 0:
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(float(value[0]))
            self.spinbox.blockSignals(False)
        elif isinstance(value, (int, float)):
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(float(value))
            self.spinbox.blockSignals(False)

    def get_value(self) -> float:
        return self.spinbox.value()

    def _on_value_changed(self, value):
        self.valueChanged.emit(self.property_name, [value])


class StringPropertyWidget(PropertyWidgetBase):
    """Widget for editing string properties."""

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Label
        self.label = QLabel(self.property_name)
        self.label.setMinimumWidth(150)
        layout.addWidget(self.label)

        # Line edit
        self.lineedit = QLineEdit()
        self.lineedit.editingFinished.connect(self._on_value_changed)
        layout.addWidget(self.lineedit, 1)

        # Reset button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setMaximumWidth(30)
        self.reset_btn.setToolTip("Reset to default")
        self.reset_btn.clicked.connect(lambda: self.resetRequested.emit(self.property_name))
        layout.addWidget(self.reset_btn)

    def set_value(self, value: Any):
        if isinstance(value, (list, tuple)) and len(value) > 0:
            self.lineedit.blockSignals(True)
            self.lineedit.setText(str(value[0]))
            self.lineedit.blockSignals(False)
        elif isinstance(value, str):
            self.lineedit.blockSignals(True)
            self.lineedit.setText(value)
            self.lineedit.blockSignals(False)

    def get_value(self) -> str:
        return self.lineedit.text()

    def _on_value_changed(self):
        self.valueChanged.emit(self.property_name, [self.lineedit.text()])


class VectorPropertyWidget(PropertyWidgetBase):
    """Widget for editing vector/array properties (float or int arrays)."""

    def __init__(self, property_name: str, property_type: str, size: int, parent=None):
        self.size = size
        self.spinboxes = []
        super().__init__(property_name, property_type, parent)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Label
        self.label = QLabel(self.property_name)
        self.label.setMinimumWidth(150)
        layout.addWidget(self.label)

        # Create spinbox for each element
        for i in range(self.size):
            if self.property_type == "int":
                spinbox = QSpinBox()
                spinbox.setRange(-2147483648, 2147483647)
            else:  # float
                spinbox = QDoubleSpinBox()
                spinbox.setRange(-1e10, 1e10)
                spinbox.setDecimals(4)
                spinbox.setSingleStep(0.1)

            spinbox.valueChanged.connect(self._on_value_changed)
            layout.addWidget(spinbox)
            self.spinboxes.append(spinbox)

        # Reset button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setMaximumWidth(30)
        self.reset_btn.setToolTip("Reset to default")
        self.reset_btn.clicked.connect(lambda: self.resetRequested.emit(self.property_name))
        layout.addWidget(self.reset_btn)

    def set_value(self, value: Any):
        if isinstance(value, (list, tuple)):
            for i, spinbox in enumerate(self.spinboxes):
                if i < len(value):
                    spinbox.blockSignals(True)
                    if self.property_type == "int":
                        spinbox.setValue(int(value[i]))
                    else:
                        spinbox.setValue(float(value[i]))
                    spinbox.blockSignals(False)

    def get_value(self) -> list:
        if self.property_type == "int":
            return [spinbox.value() for spinbox in self.spinboxes]
        else:
            return [spinbox.value() for spinbox in self.spinboxes]

    def _on_value_changed(self, value):
        self.valueChanged.emit(self.property_name, self.get_value())


class ArrayPropertyWidget(PropertyWidgetBase):
    """Widget for displaying large array properties (read-only)."""

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Label
        self.label = QLabel(self.property_name)
        self.label.setMinimumWidth(150)
        layout.addWidget(self.label)

        # Value label (read-only)
        self.value_label = QLabel()
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label, 1)

        # No reset button for read-only properties

    def set_value(self, value: Any):
        if isinstance(value, (list, tuple)):
            if len(value) <= 5:
                display_text = str(value)
            else:
                display_text = f"[{value[0]}, {value[1]}, ..., {value[-1]}] ({len(value)} items)"
            self.value_label.setText(display_text)
        else:
            self.value_label.setText(str(value))

    def get_value(self) -> Any:
        return None  # Arrays are read-only


class PropertyWidgetFactory:
    """
    Factory for creating appropriate property widgets.

    Follows Factory Pattern and OCP:
    - Encapsulates widget creation logic
    - Easy to extend with new widget types
    """

    @staticmethod
    def create_widget(property_name: str, property_type: str, value: Any,
                     parent: Optional[QWidget] = None) -> PropertyWidgetBase:
        """
        Create an appropriate widget for the given property type.

        Args:
            property_name: Name of the property
            property_type: Type of the property ('int', 'float', 'string', etc.)
            value: Current value of the property
            parent: Parent widget

        Returns:
            PropertyWidgetBase subclass instance
        """
        # Determine if it's an array property
        is_array = isinstance(value, (list, tuple)) and len(value) > 1

        if is_array:
            # Small vectors (2-16 elements) of int/float are editable
            if property_type in ("int", "float") and 2 <= len(value) <= 16:
                widget = VectorPropertyWidget(property_name, property_type, len(value), parent)
            else:
                # Large arrays or non-numeric arrays are read-only
                widget = ArrayPropertyWidget(property_name, property_type, parent)
        elif property_type == "int":
            widget = IntPropertyWidget(property_name, property_type, parent)
        elif property_type == "float":
            widget = FloatPropertyWidget(property_name, property_type, parent)
        elif property_type == "string":
            widget = StringPropertyWidget(property_name, property_type, parent)
        else:
            # Default to array widget for unknown types
            widget = ArrayPropertyWidget(property_name, property_type, parent)

        widget.set_value(value)
        return widget





