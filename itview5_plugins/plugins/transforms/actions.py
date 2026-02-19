from PySide2 import QtCore, QtGui, QtWidgets
import transforms.resources.resources


class Actions(QtCore.QObject):

    def __init__(self):
        super().__init__()

        self.toggle_transform = QtWidgets.QAction("Transform Mode")
        self.toggle_transform.setCheckable(True)
        self.toggle_transform.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":transforms.png")))

        self.toggle_dynamic_transform = QtWidgets.QAction("Dynamic Transform Mode")
        self.toggle_dynamic_transform.setCheckable(True)
        self.toggle_dynamic_transform.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":transforms_dynamic.png")))

        self.set_transform_key = QtWidgets.QAction("Set Transform Key")
        self.set_transform_key.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":set_key.png")))
        self.remove_transform_key = QtWidgets.QAction("Remove Transform Key")
        self.remove_transform_key.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":remove_key.png")))

        self.prev_key_frame = QtWidgets.QAction("Prev Key Frame")
        self.prev_key_frame.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":left.png")))
        self.next_key_frame = QtWidgets.QAction("Next Key Frame")
        self.next_key_frame.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":right.png")))

        self.crop_transforms = QtWidgets.QAction("Crop Transforms")
        self.crop_transforms.setCheckable(True)
        self.crop_transforms.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":crop_transforms_on.png")))

        self.reset_all = QtWidgets.QAction("Reset Transforms")
        self.reset_all.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":reload_button_16x20.png")))
