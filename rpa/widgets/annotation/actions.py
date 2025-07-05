try:
    from PySide2 import QtGui, QtCore, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtGui, QtCore, QtWidgets
    from PySide6.QtGui import QAction
from rpa.widgets.annotation import svg
from rpa.widgets.annotation import constants as C
import rpa.widgets.annotation.resources.resources


class SizeAction(QAction):
    SIG_TRIGGERED = QtCore.Signal(object)
    def __init__(self, size):
        super().__init__(str(size))
        self.__size = size
        self.triggered.connect(self.__emit_triggered)

    def get_size(self):
        return self.__size

    def __emit_triggered(self):
        self.SIG_TRIGGERED.emit(self)


class Actions(QtCore.QObject):
    SIG_DRAW_SIZE_CHANGED = QtCore.Signal(object)
    SIG_ERASER_SIZE_CHANGED = QtCore.Signal(object)
    SIG_TEXT_SIZE_CHANGED = QtCore.Signal(object)

    def __init__(self):
        super().__init__()
        self.color = QAction("Color")
        self.__color_pixmap = QtGui.QPixmap(24, 24)

        self.__create_size_setters()

        self.show_annotations = QAction("Toggle visibility")
        self.show_annotations.setCheckable(True)
        self.show_annotations.setChecked(False)
        self.show_annotations.setShortcut(QtGui.QKeySequence("Alt+A"))
        self.show_annotations.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":show_annotations_on.png")))
        self.show_annotations.setToolTip("Show Annotations")

        self.clear_frame = QAction("Clear all in frame")
        self.clear_frame.setShortcut(QtGui.QKeySequence("Ctrl+R"))

        self.undo = QAction("Undo Stroke")
        self.undo.setShortcut(QtGui.QKeySequence("Ctrl+Z"))
        self.undo.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":undo.png")))

        self.redo = QAction("Redo Stroke")
        self.redo.setShortcut(QtGui.QKeySequence("Ctrl+Y"))
        self.redo.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":redo.png")))

        self.next_annot_frame = QAction("Next Annotation")
        self.next_annot_frame.setShortcut(QtGui.QKeySequence("."))
        self.next_annot_frame.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":next_annotation.png")))
        self.next_annot_frame.setToolTip("Goto next annotated frame")

        self.prev_annot_frame = QAction("Prev Annotation")
        self.prev_annot_frame.setShortcut(QtGui.QKeySequence(","))
        self.prev_annot_frame.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":prev_annotation.png")))
        self.prev_annot_frame.setStatusTip("Goto previous annotated frame")

        self.cut_annotations = QAction("Cut Annotations")
        self.cut_annotations.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":cut128.png")))
        self.cut_annotations.setToolTip("Cut Annotations")

        self.copy_annotations = QAction("Copy Annotations (Ctrl+C)")
        self.copy_annotations.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":copy128.png")))
        self.copy_annotations.setToolTip("Copy Annotations")

        self.paste_annotations = QAction("Paste Annotations")
        self.paste_annotations.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":paste128.png")))
        self.paste_annotations.setToolTip("Paste Annotations")

    def __create_size_setters(self):
        self.draw_sizes = {}
        draw_sizes_action_group = QActionGroup(self)
        for i, size in enumerate(C.ANNOTATION_TOOL_SIZES):
            action = SizeAction(size)
            action.setCheckable(True)
            action.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(
                QtGui.QImage.fromData(svg.TOOL_SIZE.format(
                        2.0 + 0.5 * i, C.SVG_COLOR, C.SVG_COLOR
                    ).encode("utf-8")))))
            action.SIG_TRIGGERED.connect(self.SIG_DRAW_SIZE_CHANGED)
            draw_sizes_action_group.addAction(action)
            self.draw_sizes[size] = action

        self.eraser_sizes = {}
        eraser_sizes_action_group = QActionGroup(self)
        for i, size in enumerate(C.ANNOTATION_TOOL_SIZES):
            action = SizeAction(size)
            action.setCheckable(True)
            action.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(
                QtGui.QImage.fromData(svg.TOOL_SIZE.format(
                        2.0 + 0.5 * i, "none", C.SVG_COLOR).encode("utf-8")))))
            action.SIG_TRIGGERED.connect(self.SIG_ERASER_SIZE_CHANGED)
            self.eraser_sizes[size] = action
            eraser_sizes_action_group.addAction(action)

        self.text_sizes = {}
        text_sizes_action_group = QActionGroup(self)
        for i, size in enumerate(C.ANNOTATION_TEXT_SIZES):
            action = SizeAction(size)
            action.setCheckable(True)
            action.setIcon(QtGui.QIcon(
                QtGui.QPixmap.fromImage(QtGui.QImage.fromData(
                    svg.TEXT.format(
                        C.SVG_COLOR, i / (2.0 * len(C.ANNOTATION_TEXT_SIZES)) + 0.5).encode("utf-8")))))
            action.SIG_TRIGGERED.connect(self.SIG_TEXT_SIZE_CHANGED)
            self.text_sizes[size] = action
            text_sizes_action_group.addAction(action)

    def set_color(self, r, g, b, a):
        self.__color_pixmap.fill(QtGui.QColor.fromRgbF(r, g, b, a))
        self.color.setIcon(QtGui.QIcon(self.__color_pixmap))

    def toggle_annotation_visibility(self, show):
        if show:
            self.show_annotations.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":show_annotations_on.png")))
        else:
            self.show_annotations.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":show_annotations_off.png")))
