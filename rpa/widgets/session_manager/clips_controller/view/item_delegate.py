from PySide2 import QtCore, QtWidgets, QtGui


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        proxy_model = index.model()
        source_model = proxy_model.sourceModel()
        column_index = proxy_model.mapToSource(index).column()
        attr = source_model.attrs[column_index]

        if source_model.get_attr_data_type(attr) == "path":
            media_path = self.__get_file_path_from_file_dialog()
            current_path = proxy_model.data(index, QtCore.Qt.EditRole)
            if media_path and media_path != current_path:
                proxy_model.setData(index, media_path, QtCore.Qt.EditRole)
            return None

        if source_model.get_attr_data_type(attr) == "bool":
            current_value = proxy_model.data(index, QtCore.Qt.EditRole)
            proxy_model.setData(index, not current_value, QtCore.Qt.EditRole)
            return None

        if isinstance(editor, QtWidgets.QLineEdit):
            current_value = proxy_model.data(index, QtCore.Qt.EditRole)
            editor = MultiLineEdit(parent, self, current_value)
            QtCore.QTimer.singleShot(0, lambda: self.__select_all_text(editor))
        return editor

    def setEditorData(self, editor, index):
        return super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QtWidgets.QPlainTextEdit):
            text = editor.toPlainText()
            model.setData(index, text, QtCore.Qt.EditRole)
        else:
            return super().setModelData(editor, model, index)

    def __select_all_text(self, editor):
        cursor = editor.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(cursor.End, cursor.KeepAnchor)
        editor.setTextCursor(cursor)

    def __get_file_path_from_file_dialog(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Browse Path",
            "",
            "",
            options=QtWidgets.QFileDialog.DontUseNativeDialog)
        return file_path


class MultiLineEdit(QtWidgets.QPlainTextEdit):

    MIN_H = 0
    MAX_H = 44
    LINE_H = 18

    def __init__(self, parent, item_delegate, text):
        super().__init__(parent)

        self.__parent = parent
        self.__item_delegate = item_delegate
        self.__text = text
        self.setPlainText(text)

        self.__set_document_height()
        self.document().contentsChanged.connect(self.__change_height)

    def __set_document_height(self):
        line_count = len(self.__text.split("\n"))

        if line_count > 2 and line_count <= int(self.MAX_H / self.LINE_H):
            self.setMinimumHeight(line_count * self.LINE_H)
        elif line_count >= int(self.MAX_H / self.LINE_H):
            self.setMinimumHeight(self.MAX_H)

    def __change_height(self):
        doc_h = self.document().size().height()
        if self.MIN_H <= doc_h <= self.MAX_H:
            self.setMinimumHeight(doc_h)

    def setPlainText(self, text):
        self.__text = text
        super().setPlainText(text)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) \
            and not(event.modifiers() & QtCore.Qt.ShiftModifier):
            self.__item_delegate.commitData.emit(self)
            self.__item_delegate.closeEditor.emit(
                self, QtWidgets.QAbstractItemDelegate.NoHint)
            return
        return super().keyPressEvent(event)
