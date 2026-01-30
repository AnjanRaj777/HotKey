from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QCheckBox, QPushButton, QHBoxLayout, 
                             QFileDialog, QDialogButtonBox, QMessageBox)
from ui.key_recorder import KeyRecorder

class AddHotkeyDialog(QDialog):
    def __init__(self, parent=None, hotkey_data=None):
        super().__init__(parent)
        self.hotkey_data = hotkey_data
        self.setWindowTitle("Edit Hotkey" if hotkey_data else "Add Hotkey")
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Trigger Key
        layout.addWidget(QLabel("Trigger Key (e.g., ctrl+alt+t):"))
        self.trigger_input = KeyRecorder()
        layout.addWidget(self.trigger_input)

        # 2. Action Type (Create first, setup later)
        layout.addWidget(QLabel("Action Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["File", "Folder", "focus", "open_url"])
        layout.addWidget(self.type_combo)

        # 3. Target (Create first)
        layout.addWidget(QLabel("Target:"))
        target_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        target_layout.addWidget(self.target_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        target_layout.addWidget(self.browse_btn)
        
        layout.addLayout(target_layout)

        # 4. Block Key
        self.block_cb = QCheckBox("Block original key (Suppress)")
        self.block_cb.setToolTip("If checked, the key combination will NOT be passed to other applications.")
        layout.addWidget(self.block_cb)

        # 5. Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # --- Logic & Pre-filling ---
        # Now that all widgets exist, we can safely connect signals and set values
        
        # Connect Type Change
        self.type_combo.currentTextChanged.connect(self.on_type_changed)

        if self.hotkey_data:
            # Pre-fill data
            self.trigger_input.setText(self.hotkey_data.get("trigger", ""))
            self.target_input.setText(self.hotkey_data.get("target", ""))
            self.block_cb.setChecked(self.hotkey_data.get("suppress", False))
            
            # Set Type last to trigger on_type_changed correctly with data
            current_type = self.hotkey_data.get("type", "File")
            self.type_combo.setCurrentText(current_type)
        else:
            # Default state
            self.on_type_changed("File")

    def on_type_changed(self, text):
        if text == "File":
            self.browse_btn.setEnabled(True)
            self.browse_btn.setVisible(True)
            self.target_input.setPlaceholderText("Path to executable or file")
        elif text == "Folder":
            self.browse_btn.setEnabled(True)
            self.browse_btn.setVisible(True)
            self.target_input.setPlaceholderText("Path to folder")
        elif text == "open_url":
            self.browse_btn.setEnabled(False)
            self.browse_btn.setVisible(False)
            self.target_input.setPlaceholderText("Enter URL (e.g., https://google.com)")
        else: # focus
            self.browse_btn.setEnabled(False)
            self.browse_btn.setVisible(False)
            self.target_input.setPlaceholderText("Window Title to match")

    def browse_file(self):
        action_type = self.type_combo.currentText()
        if action_type == "Folder":
             folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
             if folder_path:
                 self.target_input.setText(folder_path)
        else: # File (or others, but button is hidden)
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
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
