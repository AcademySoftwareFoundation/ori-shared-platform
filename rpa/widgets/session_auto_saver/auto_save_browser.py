import os
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QApplication, QDialog
)
from PySide2.QtCore import Qt, Signal, QDateTime


class AutoSaveBrowser(QDialog):
    SIG_FILE_SELECTED = Signal(str)  # Emits selected file path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recover Auto-Saved Sessions")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)
        self.label = QLabel("Select a file to restore:")
        self.list_widget = QListWidget()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)

        self.list_widget.itemClicked.connect(self.on_file_selected)

    def populate_files(self, files):
        self.list_widget.clear()
        for file in files:
            filename = os.path.basename(file)
            timestamp = QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(file))).toString("yyyy-MM-dd hh:mm:ss")
            item_text = f"{filename}  —  {timestamp}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, file)
            self.list_widget.addItem(item)

    def on_file_selected(self, item: QListWidgetItem):
        file_path = item.data(Qt.UserRole)
        self.SIG_FILE_SELECTED.emit(file_path)
        self.accept()  # Close the popup
