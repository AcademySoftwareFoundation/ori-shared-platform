try:
    from PySide2.QtWidgets import (
        QWidget, QVBoxLayout, QPlainTextEdit, QTextEdit, QPushButton,
        QLabel, QHBoxLayout, QCompleter
    )
    from PySide2.QtCore import Qt, QRegExp, QStringListModel
    from PySide2.QtGui import (
        QTextCharFormat, QFont, QColor, QSyntaxHighlighter, QKeyEvent
    )
except ImportError:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QPlainTextEdit, QTextEdit, QPushButton,
        QLabel, QHBoxLayout, QCompleter
    )
    from PySide6.QtCore import Qt, QRegularExpression, QStringListModel
    QRegExp = QRegularExpression 
    from PySide6.QtGui import (
        QTextCharFormat, QFont, QColor, QSyntaxHighlighter, QKeyEvent
    )

import traceback
import io
import sys
import inspect


def get_rpa_keywords(rpa):
    methods = []
    for module_name in [
    "session_api", "timeline_api", "viewport_api",
    "annotation_api", "color_api", "config_api"]:
        module = getattr(rpa, module_name)
        for name, member in inspect.getmembers(module):
            if callable(member) and not name.startswith('_'):
                methods.append(f"rpa.{module_name}.{name}")
    return methods


# --- Python syntax highlighter for code input ---
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#00FFFF"))
        keyword_format.setFontWeight(QFont.Bold)

        self.keyword_patterns = [
            r'\bdef\b', r'\bclass\b', r'\bimport\b', r'\bfrom\b',
            r'\bas\b', r'\breturn\b', r'\bif\b', r'\belse\b', r'\belif\b',
            r'\bwhile\b', r'\bfor\b', r'\bin\b', r'\btry\b', r'\bexcept\b',
            r'\bwith\b', r'\bpass\b', r'\bNone\b', r'\bTrue\b', r'\bFalse\b',
            r'\bprint\b', r'\brpa\b'
        ]
        self.highlighting_rules = [(QRegExp(pat), keyword_format) for pat in self.keyword_patterns]

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("magenta"))
        self.highlighting_rules.append((QRegExp(r'"[^"]*"'), string_format))
        self.highlighting_rules.append((QRegExp(r"'[^']*'"), string_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("darkgreen"))
        self.highlighting_rules.append((QRegExp(r'#.*'), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)


# --- Code input widget with tab-completion ---
class CodeInput(QPlainTextEdit):
    def __init__(self, keywords, callback, rpa_obj=None, parent=None):
        super().__init__(parent)
        self.setTabChangesFocus(False)
        self.setPlaceholderText("Type Python code using `rpa` here...")

        self.keywords = keywords
        self.rpa = rpa_obj  # reference to your rpa instance for attribute completion

        self.completer = QCompleter(keywords, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)

        self.callback = callback

        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: black;
                color: white;
                font-family: Consolas, monospace;
                font-size: 20px;
            }
        """)

        PythonHighlighter(self.document())  # Enable syntax highlighting

    def insert_completion(self, completion):
        if self.completer.widget() != self:
            return
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        # Select the current word under cursor and replace it with completion
        tc.movePosition(tc.Left, tc.MoveAnchor, len(self.completer.completionPrefix()))
        tc.movePosition(tc.Right, tc.KeepAnchor, len(self.completer.completionPrefix()))
        tc.removeSelectedText()
        tc.insertText(completion)
        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(tc.WordUnderCursor)
        return tc.selectedText()

    def get_object_attributes(self, obj_path):
        """
        Given a dotted object path string, e.g. 'rpa.session_api',
        return a list of attribute/method names for the object.
        """
        try:
            # Resolve object from the exec_context or self.rpa
            # For now, we only support 'rpa' root
            if not obj_path.startswith("rpa"):
                return []

            # Navigate the attributes
            parts = obj_path.split('.')
            obj = self.rpa
            for part in parts[1:]:
                obj = getattr(obj, part, None)
                if obj is None:
                    return []

            # Get list of attributes/methods excluding private
            attrs = [a for a in dir(obj) if not a.startswith('_')]
            return attrs
        except Exception:
            return []

    def get_code_to_run(self):
        code = self.textCursor().selectedText()
        if not code: code = self.toPlainText()
        code = code.strip()
        # Replace paragraph separator with regular newline
        code = code.replace('\u2029', '\n').replace('\r', '')
        return code

    def keyPressEvent(self, event):
        # If completer popup is visible, let it handle keys like Enter, Tab, etc.
        if self.completer.popup().isVisible():
            # Keys that should be forwarded to the completer
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()  # Let completer handle it
                return

        # Ctrl+Enter runs the code via callback
        if (event.key() in (Qt.Key_Enter, Qt.Key_Return) and
                event.modifiers() == Qt.ControlModifier):
            if self.callback:
                self.callback(self.get_code_to_run())
            return  # Don't insert newline on Ctrl+Enter

        super().keyPressEvent(event)  # Process the key event normally first

        # Now handle completion
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        full_text = self.toPlainText()[:cursor_pos]

        # Find the last token before the cursor relevant for completion
        # We look for either word or dot-separated object path

        # Regex to extract last dotted expression before the cursor
        import re
        pattern = r'([a-zA-Z_][\w\.]*)$'
        match = re.search(pattern, full_text)
        if match:
            obj_path = match.group(1)
        else:
            obj_path = ''

        # Determine if we are completing attributes (after dot)
        if '.' in obj_path:
            # e.g. rpa.session_api.
            if full_text.endswith('.'):
                # user just typed dot, show attributes of obj_path without last dot
                obj_for_attrs = obj_path.rstrip('.')
                attrs = self.get_object_attributes(obj_for_attrs)
                if attrs:
                    self.completer.model().setStringList(attrs)
                    self.completer.setCompletionPrefix('')
                    cr = self.cursorRect()
                    cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                                self.completer.popup().verticalScrollBar().sizeHint().width())
                    self.completer.complete(cr)
                    return
            else:
                # user typing attribute prefix after dot, e.g. rpa.session_api.ses
                last_dot = obj_path.rfind('.')
                prefix = obj_path[last_dot+1:]
                obj_for_attrs = obj_path[:last_dot]
                attrs = self.get_object_attributes(obj_for_attrs)
                filtered_attrs = [a for a in attrs if a.startswith(prefix)]
                if filtered_attrs:
                    self.completer.model().setStringList(filtered_attrs)
                    self.completer.setCompletionPrefix(prefix)
                    cr = self.cursorRect()
                    cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                                self.completer.popup().verticalScrollBar().sizeHint().width())
                    self.completer.complete(cr)
                    return
        else:
            # Completing top-level keywords and methods
            prefix = obj_path
            filtered_keywords = [k for k in self.keywords if k.startswith(prefix)]
            if filtered_keywords:
                self.completer.model().setStringList(filtered_keywords)
                self.completer.setCompletionPrefix(prefix)
                cr = self.cursorRect()
                cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                            self.completer.popup().verticalScrollBar().sizeHint().width())
                self.completer.complete(cr)
                return

        # If no matches or conditions fail, hide popup
        self.completer.popup().hide()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.completer.setWidget(self)


# --- Main interpreter widget ---
class RpaInterpreter(QWidget):
    def __init__(self, rpa, main_window):
        super().__init__(main_window)
        self.rpa = rpa
        self.exec_context = {'rpa': self.rpa}

        self.setWindowTitle("RPA Python Interpreter")
        self.setMinimumSize(600, 450)

        layout = QVBoxLayout(self)

        # Input code editor with autocomplete
        layout.addWidget(QLabel("Python Code:"))
        keywords = [
            'print', 'for', 'while', 'if', 'else', 'elif', 'def', 'class',
            'import', 'from', 'return', 'with', 'try', 'except', 'pass',
            'True', 'False', 'None'
        ]
        keywords = []
        self.input_editor = CodeInput(keywords, callback=self.execute_code, rpa_obj=rpa)
        layout.addWidget(self.input_editor)

        # Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.clear_button = QPushButton("Clear History")
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        # History output
        layout.addWidget(QLabel("Execution History:"))
        self.history_editor = QTextEdit()
        self.history_editor.setReadOnly(True)
        self.history_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;  /* dark gray */
                color: #dcdcdc;
                font-family: Consolas, monospace;
                font-size: 18px;
            }
        """)
        layout.addWidget(self.history_editor)

        # Button signals
        self.run_button.clicked.connect(
            lambda: self.execute_code(self.input_editor.get_code_to_run()))
        self.clear_button.clicked.connect(self.clear_history)

    def execute_code(self, code):
        if not code:
            return

        # Use shared context to persist session variables
        local_context = self.exec_context
        stdout_backup = sys.stdout
        stderr_backup = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            exec(code, {}, local_context)
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
        except Exception:
            output = sys.stdout.getvalue()
            error = traceback.format_exc()

        sys.stdout = stdout_backup
        sys.stderr = stderr_backup

        result = output + error
        history_entry = f">>> {code}\n{result}\n"
        self.append_to_history(history_entry)

    def append_to_history(self, text):
        self.history_editor.append(text)

    def clear_history(self):
        self.history_editor.clear()
