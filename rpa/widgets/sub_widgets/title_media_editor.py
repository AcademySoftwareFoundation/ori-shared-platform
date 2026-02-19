try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets
from dataclasses import dataclass
from rpa.utils.resources import icons


class TitleMediaEditor(QtWidgets.QDialog):

    def __init__(self,
        text="",
        text_font=QtGui.QFont("DejaVu Sans", 16),
        text_alignment="left",
        text_color=QtGui.QColor("white"),
        background_color=QtGui.QColor("black"),
        parent=None):
        super().__init__(parent)

        self.setWindowTitle("Title Media Editor")
        self.__font_db = QtGui.QFontDatabase()
        self.__font_dialog = CustomFontDialog(
            self.__font_db, self, font=text_font)
        self.__color_dialog = QtWidgets.QColorDialog()

        # font
        self.__text_font = text_font
        self.__font_button = QtWidgets.QPushButton("", self)
        self.__font_button.clicked.connect(self.__choose_font)
        self.__update_font_button(self.__text_font)

        # text alignment
        self.__text_alignment = text_alignment

        # self.__align_left = QtWidgets.QToolButton(self)
        # self.__align_left.setText("left")
        # self.__align_left.setToolTip("Left")
        # self.__align_left.setCheckable(True)
        # self.__align_left.setIcon(QtGui.QIcon(QtGui.QPixmap(":align_left.png")))

        # self.__align_center = QtWidgets.QToolButton(self)
        # self.__align_center.setText("center")
        # self.__align_center.setToolTip("Center")
        # self.__align_center.setCheckable(True)
        # self.__align_center.setIcon(QtGui.QIcon(QtGui.QPixmap(":align_center.png")))

        # self.__align_right = QtWidgets.QToolButton(self)
        # self.__align_right.setText("right")
        # self.__align_right.setToolTip("Right")
        # self.__align_right.setCheckable(True)
        # self.__align_right.setIcon(QtGui.QIcon(QtGui.QPixmap(":align_right.png")))

        # self.__align_justify = QtWidgets.QToolButton(self)
        # self.__align_justify.setText("justify")
        # self.__align_justify.setToolTip("Justify")
        # self.__align_justify.setCheckable(True)
        # self.__align_justify.setIcon(QtGui.QIcon(QtGui.QPixmap(":align_justify.png")))

        # self.__text_alignment_group = QtWidgets.QButtonGroup(self)
        # self.__text_alignment_group.addButton(self.__align_left)
        # self.__text_alignment_group.addButton(self.__align_right)
        # self.__text_alignment_group.addButton(self.__align_center)
        # self.__text_alignment_group.addButton(self.__align_justify)
        # self.__text_alignment_group.buttonClicked.connect(
        #     self.__text_alignment_button_clicked)

        # for button in self.__text_alignment_group.buttons():
        #     if button.text == self.__text_alignment:
        #         button.setChecked(True)

        # text edit
        self.__text_edit = QtWidgets.QPlainTextEdit(text, self)

        # text color
        self.__text_color = text_color
        self.__text_color_pixmap = QtGui.QPixmap(20, 20)
        self.__text_color_button = QtWidgets.QToolButton(self)
        self.__text_color_button.setIconSize(self.__text_color_pixmap.size())
        self.__text_color_button.setToolTip("Text Color")
        self.__text_color_button.clicked.connect(self.__choose_text_color)
        self.__button_color_changed(
            self.__text_color, self.__text_color_pixmap, self.__text_color_button)

        # background color
        self.__background_color = background_color
        self.__background_color_pixmap = QtGui.QPixmap(20, 20)
        self.__background_color_button = QtWidgets.QToolButton(self)
        self.__background_color_button.setIconSize(self.__background_color_pixmap.size())
        self.__background_color_button.setToolTip("Background Color")
        self.__background_color_button.clicked.connect(self.__choose_background_color)
        self.__button_color_changed(
            self.__background_color, self.__background_color_pixmap, self.__background_color_button)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # layouts
        font_alignment_layout = QtWidgets.QHBoxLayout()
        font_alignment_layout.addWidget(QtWidgets.QLabel("Font:"))
        font_alignment_layout.addWidget(self.__font_button)
        font_alignment_layout.addStretch()

        # TODO not available for title media overlay usage
        # font_alignment_layout.addWidget(QtWidgets.QLabel("Alignment: "))
        # font_alignment_layout.addWidget(self.__align_left)
        # font_alignment_layout.addWidget(self.__align_center)
        # font_alignment_layout.addWidget(self.__align_right)
        # font_alignment_layout.addWidget(self.__align_justify)
        # font_alignment_layout.addStretch()

        text_edit_layout = QtWidgets.QHBoxLayout()
        text_edit_layout.addWidget(QtWidgets.QLabel("Text: "))
        text_edit_layout.addWidget(self.__text_edit)

        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(QtWidgets.QLabel("Text Color: "))
        color_layout.addWidget(self.__text_color_button)
        color_layout.addStretch()
        color_layout.addWidget(QtWidgets.QLabel("Background Color: "))
        color_layout.addWidget(self.__background_color_button)
        color_layout.addStretch()

        self.__main_layout = QtWidgets.QVBoxLayout(self)
        self.__main_layout.addLayout(font_alignment_layout)
        self.__main_layout.addLayout(text_edit_layout)
        self.__main_layout.addLayout(color_layout)
        self.__main_layout.addWidget(button_box)

    def __choose_font(self):
        if self.__font_dialog.exec_():
            font = self.__font_dialog.get_font()
        else:
            font = None

        if font is None:
            return

        self.__text_font = font
        self.__update_font_button(font)

    def __update_font_button(self, font):
        style_name = self.__font_dialog.find_style_name(font)
        self.__font_button.setText(
            f"{font.family()}, {style_name}, {font.pointSize()}")

    def __text_alignment_button_clicked(self, button):
        self.__text_alignment = button.text()

    def __button_color_changed(self, color, pixmap, button):
        pixmap.fill(color)
        button.setIcon(QtGui.QIcon(pixmap))

    def __choose_text_color(self):
        color = self.__color_dialog.getColor(
            self.__text_color, self, "Select Text Color")
        if not color.isValid():
            return
        self.__text_color = color
        self.__button_color_changed(
            self.__text_color,
            self.__text_color_pixmap,
            self.__text_color_button)

    def __choose_background_color(self):
        color = self.__color_dialog.getColor(
            self.__background_color, self, "Select Background Color")
        if not color.isValid():
            return
        self.__background_color = color
        self.__button_color_changed(
            self.__background_color,
            self.__background_color_pixmap,
            self.__background_color_button)

    def get_properties(self):
        text = self.__text_edit.toPlainText()
        font = self.__text_font.toString()
        alignment = self.__text_alignment
        text_r, text_g, text_b, text_a = self.__text_color.getRgbF()
        bkg_r, bkg_g, bkg_b, bkg_a = self.__background_color.getRgbF()

        tmp = {
            "text" : text,
            "text_font" : font,
            "text_alignment" : alignment,
            "text_color" : (text_r, text_g, text_b, text_a),
            "background_color" : (bkg_r, bkg_g, bkg_b, bkg_a)
        }
        return tmp


class CustomFontDialog(QtWidgets.QDialog):
    def __init__(
        self, font_db, parent=None,
        title="Select Font", font=QtGui.QFont("DejaVu Sans", 16)):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.__font_db = font_db
        self.__font = font #QFont
        self.__style = self.find_style_name(font)
        self.__size = str(font.pointSize()) #str

        # font
        self.__font_label = QtWidgets.QLabel("Font")
        self.__font_combobox = QtWidgets.QFontComboBox(self)
        self.__font_combobox.setCurrentFont(self.__font.family())
        self.__font_combobox.currentFontChanged.connect(self.__font_changed)

        # style
        self.__font_style_label = QtWidgets.QLabel("Font Style")
        self.__font_style_line_edit = QtWidgets.QLineEdit("")
        self.__font_style_line_edit.setReadOnly(True)

        self.__font_style_list = QtWidgets.QListWidget(self)
        self.__font_style_list.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        self.__font_style_list.currentItemChanged.connect(self.__font_style_changed)
        self.__update_style_list(self.__font.family())

        # size
        self.__font_size_label = QtWidgets.QLabel("Font Size")
        self.__font_size_line_edit = QtWidgets.QLineEdit(f"{self.__size}")
        self.__font_size_line_edit.setValidator(QtGui.QIntValidator(1, 99))
        self.__font_size_line_edit.textEdited.connect(self.__size_edited)

        self.__font_size_list = QtWidgets.QListWidget(self)
        self.__font_size_list.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        self.__font_size_list.currentItemChanged.connect(self.__font_size_changed)
        self.__font_size_list.addItems(
            [str(size) for size in self.__font_db.standardSizes()])
        self.__size_edited(self.__size)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # layout
        self.__layout = QtWidgets.QGridLayout(self)

        self.__layout.addWidget(self.__font_label, 0, 0)
        self.__layout.addWidget(self.__font_combobox, 1, 0, 1, 2)

        self.__layout.addWidget(self.__font_style_label, 2, 0)
        self.__layout.addWidget(self.__font_style_line_edit, 3, 0)
        self.__layout.addWidget(self.__font_style_list, 4, 0)

        self.__layout.addWidget(self.__font_size_label, 2, 1)
        self.__layout.addWidget(self.__font_size_line_edit, 3, 1)
        self.__layout.addWidget(self.__font_size_list, 4, 1)

        self.__layout.setColumnStretch(0, 1)
        self.__layout.setColumnStretch(1, 1)

        self.__layout.addWidget(buttons, 5, 1, 1, 2)

    def __font_changed(self, font:QtGui.QFont):
        self.__font = font
        self.__update_style_list(font.family())

    def __font_style_changed(self, style):
        if style:
            self.__style = str(style.text())
            self.__font_style_line_edit.setText(self.__style)

    def __font_size_changed(self, size):
        if size:
            self.__size = size.text()
            self.__font_size_line_edit.setText(self.__size)

    def __size_edited(self, size:str):
        matching_items = self.__font_size_list.findItems(size, QtCore.Qt.MatchExactly)
        if matching_items:
            item = matching_items[0]
            self.__font_size_list.setCurrentItem(item)
            self.__size = item.text()
        else:
            self.__font_size_list.clearSelection()
            self.__size = size

    def __update_style_list(self, font_family):
        styles = self.__font_db.styles(font_family)
        self.__font_style_list.clear()
        self.__font_style_list.blockSignals(True)
        self.__font_style_list.addItems(styles)
        self.__font_style_list.blockSignals(False)

        all_items = \
            [self.__font_style_list.item(i) for i in range(self.__font_style_list.count())]
        for item in all_items:
            if self.__style == item.text():
                self.__font_style_list.setCurrentItem(item)
                break

        if self.__font_style_list.currentItem() is None:
            self.__font_style_list.setCurrentRow(0)

    def find_style_name(self, font):
        styles = self.__font_db.styles(font.family())
        style_name = self.__font_db.styleString(font)
        style_name = "Regular" if style_name == "Normal" else style_name
        if style_name:
            return style_name
        else:
            styles = self.__font_db.styles(font.family())
            for style in styles:
                f = self.__font_db.font(font_family, style, font.pointSize())
                if f.weight() == font.weight() and f.italic() == font.italic():
                    style_name = style
                    break

            return style_name

    def get_font(self):
        font = self.__font_db.font(
            self.__font.family(), self.__style, int(self.__size))
        return font
