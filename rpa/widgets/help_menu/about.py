from PySide2 import QtCore, QtWidgets


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, app_name: str, rpa_version: str = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{app_name} — About")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(self)

        # --- Title ---
        title_label = QtWidgets.QLabel(f"<h2>{app_name}</h2>")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # --- Version Info ---
        version_text = f"<b>RPA Version:</b> {rpa_version}"

        version_label = QtWidgets.QLabel(version_text)
        version_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # --- Help Text ---
        help_text = QtWidgets.QLabel("""
        <p>RPA is part of the Open Review Initiative. Learn more on the 
            <a href='https://github.com/AcademySoftwareFoundation/ori-shared-platform'>project page</a>.</p>
        """)
        help_text.setOpenExternalLinks(True)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # --- Close button ---
        button_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
