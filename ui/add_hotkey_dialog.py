from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QComboBox, QCheckBox, QPushButton, QHBoxLayout,
                             QFileDialog, QDialogButtonBox, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from ui.key_recorder import KeyRecorder
from ui.blur_effect import apply_acrylic_blur, GRADIENT_DEEP_BLUE

class AddHotkeyDialog(QDialog):
    def __init__(self, parent=None, hotkey_data=None):
        super().__init__(parent)
        self.hotkey_data = hotkey_data
        self.setWindowTitle("Edit Hotkey" if hotkey_data else "Add Hotkey")
        self.setFixedWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            apply_acrylic_blur(int(self.winId()), gradient_color=GRADIENT_DEEP_BLUE)
        except Exception:
            pass

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QFrame()
        container.setObjectName("dialogContainer")
        container.setStyleSheet("""
            QFrame#dialogContainer {
                background-color: rgba(12, 14, 26, 0.28);
                border: none;
                border-radius: 20px;
            }
            QLabel { color: #f0f0f0; }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(container)

        # 1. Trigger Key
        layout.addWidget(QLabel("Trigger Key (e.g., ctrl+alt+t):"))
        self.trigger_input = KeyRecorder()
        layout.addWidget(self.trigger_input)

        # 2. Action Type (Create first, setup later)
        layout.addWidget(QLabel("Action Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["File", "Folder", "focus", "open_url", "Ai Voice Mode"])
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

        # 3.5. Name (Optional)
        layout.addWidget(QLabel("Name (Optional):"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Custom display name for the hotkey")
        layout.addWidget(self.name_input)

        # Note Label (Dynamic)
        self.note_label = QLabel("")
        self.note_label.setStyleSheet("color: gray; font-style: italic;")
        self.note_label.setWordWrap(True)
        self.note_label.setVisible(False)
        layout.addWidget(self.note_label)

        # 4. Block Key
        self.block_cb = QCheckBox("Block original key (Suppress)")
        self.block_cb.setToolTip("If checked, the key combination will NOT be passed to other applications.")
        layout.addWidget(self.block_cb)

        # 5. Long Press Trigger
        self.long_press_cb = QCheckBox("Long Press Trigger")
        self.long_press_cb.setToolTip("Trigger action only if key is held down for the configured delay.")
        self.long_press_cb = QCheckBox("Long Press Trigger")
        self.long_press_cb.setToolTip("Trigger action only if key is held down for the configured delay.")
        # self.long_press_cb.toggled.connect(self.on_long_press_toggled) # Removed enforcement
        layout.addWidget(self.long_press_cb)

        # 6. Buttons
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
            self.name_input.setText(self.hotkey_data.get("name", ""))
            self.block_cb.setChecked(self.hotkey_data.get("suppress", False))
            self.long_press_cb.setChecked(self.hotkey_data.get("long_press", False))
            
            # Set Type last to trigger on_type_changed correctly with data
            current_type = self.hotkey_data.get("type", "File")
            self.type_combo.setCurrentText(current_type)
        else:
            # Default state
            self.on_type_changed("File")

    def on_type_changed(self, text):
        self.note_label.setVisible(False)
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
        elif text == "Ai Voice Mode":
            self.browse_btn.setEnabled(False)
            self.browse_btn.setVisible(False)
            self.target_input.setPlaceholderText("AI Bot URL (e.g., https://chatgpt.com/)")
            self.note_label.setText("Note: This feature will launch the selected AI bot in voice mode.")
            self.note_label.setVisible(True)
        else: # focus
            self.browse_btn.setEnabled(False)
            self.browse_btn.setVisible(False)
            self.target_input.setPlaceholderText("Window Title to match")

            self.target_input.setPlaceholderText("Window Title to match")

    # def on_long_press_toggled(self, checked):
    #     if checked:
    #         self.block_cb.setChecked(True)
    #         self.block_cb.setEnabled(False)
    #     else:
    #         self.block_cb.setEnabled(True)

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
            "name": self.name_input.text().strip(),
            "suppress": self.block_cb.isChecked(),
            "long_press": self.long_press_cb.isChecked()
        }

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_pos') and self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()
