from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QCheckBox, QPushButton, QHBoxLayout, 
                             QFileDialog, QDialogButtonBox, QMessageBox)
from ui.key_recorder import KeyRecorder

class AddHotkeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Hotkey")
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Trigger
        layout.addWidget(QLabel("Trigger Key (e.g., ctrl+alt+t):"))
        self.trigger_input = KeyRecorder()
        # self.trigger_input.setPlaceholderText("Press keys or type here...") # Set in class
        layout.addWidget(self.trigger_input)

        # Action Type
        layout.addWidget(QLabel("Action Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["run", "focus", "open_url"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)

        # Target
        layout.addWidget(QLabel("Target:"))
        target_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        target_layout.addWidget(self.target_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        target_layout.addWidget(self.browse_btn)
        
        layout.addLayout(target_layout)

        # Block Key
        self.block_cb = QCheckBox("Block original key (Suppress)")
        self.block_cb.setToolTip("If checked, the key combination will NOT be passed to other applications.")
        layout.addWidget(self.block_cb)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.on_type_changed(self.type_combo.currentText())

    def on_type_changed(self, text):
        if text == "run":
            self.browse_btn.setEnabled(True)
            self.browse_btn.setVisible(True)
            self.target_input.setPlaceholderText("Path to executable or command")
        elif text == "open_url":
            self.browse_btn.setEnabled(False)
            self.browse_btn.setVisible(False)
            self.target_input.setPlaceholderText("Enter URL (e.g., https://google.com)")
        else: # focus
            self.browse_btn.setEnabled(False)
            self.browse_btn.setVisible(False)
            self.target_input.setPlaceholderText("Window Title to match")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Executable")
        if file_path:
            self.target_input.setText(file_path)

    def validate_and_accept(self):
        if not self.trigger_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Trigger key is required.")
            return
        if not self.target_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Target is required.")
            return
        self.accept()

    def get_data(self):
        return {
            "trigger": self.trigger_input.text().strip(),
            "type": self.type_combo.currentText(),
            "target": self.target_input.text().strip(),
            "suppress": self.block_cb.isChecked()
        }
