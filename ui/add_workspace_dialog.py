from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QListWidget, QSpinBox, 
                             QFileDialog, QMessageBox, QWidget)
from PyQt6.QtCore import Qt


from .app_selection_dialog import AppSelectionDialog
from .key_recorder import KeyRecorder

class AddWorkspaceDialog(QDialog):
    def __init__(self, parent=None, workspace_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add Workspace" if not workspace_data else "Edit Workspace")
        self.resize(400, 500)
        self.workspace_data = workspace_data
        
        self.init_ui()
        
        if self.workspace_data:
            self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Workspace Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Coding, Gaming")
        layout.addWidget(self.name_input)
        
        # Launch Hotkey
        layout.addWidget(QLabel("Global Launch Hotkey:"))
        self.hotkey_recorder = KeyRecorder()
        self.hotkey_recorder.setPlaceholderText("Click and press keys (e.g. Ctrl+Alt+1)")
        layout.addWidget(self.hotkey_recorder)
        
        # Virtual Desktop Index
        layout.addWidget(QLabel("Target Virtual Desktop (Index):"))
        self.desktop_spin = QSpinBox()
        self.desktop_spin.setRange(1, 10) # Assuming max 10 for now
        self.desktop_spin.setValue(1)
        layout.addWidget(self.desktop_spin)
        
        # Apps
        layout.addWidget(QLabel("Auto-launch Apps (Full Path):"))
        self.apps_list = QListWidget()
        layout.addWidget(self.apps_list)
        
        app_btn_layout = QHBoxLayout()
        
        browse_app_btn = QPushButton("Select Folder...")
        browse_app_btn.clicked.connect(self.browse_app)
        
        select_app_btn = QPushButton("Select Installed App")
        select_app_btn.clicked.connect(self.select_installed_app)
        
        remove_app_btn = QPushButton("Remove App")
        remove_app_btn.clicked.connect(self.remove_app)
        
        app_btn_layout.addWidget(browse_app_btn)
        app_btn_layout.addWidget(select_app_btn)
        app_btn_layout.addWidget(remove_app_btn)
        layout.addLayout(app_btn_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def load_data(self):
        self.name_input.setText(self.workspace_data.get("name", ""))
        self.desktop_spin.setValue(self.workspace_data.get("desktop_index", 1))
        
        hotkey = self.workspace_data.get("launch_hotkey", "")
        if hotkey:
            self.hotkey_recorder.setText(hotkey)
            self.hotkey_recorder.held_keys = set(hotkey.split("+"))
            
        for app in self.workspace_data.get("apps", []):
            self.apps_list.addItem(app)

    def browse_app(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.apps_list.addItem(folder_path)

    def select_installed_app(self):
        dialog = AppSelectionDialog(self)
        if dialog.exec():
            app_path = dialog.get_selected_app()
            if app_path:
                self.apps_list.addItem(app_path)

    def remove_app(self):
        current_row = self.apps_list.currentRow()
        if current_row >= 0:
            self.apps_list.takeItem(current_row)

    def get_data(self):
        apps = [self.apps_list.item(i).text() for i in range(self.apps_list.count())]
        return {
            "name": self.name_input.text(),
            "desktop_index": self.desktop_spin.value(),
            "launch_hotkey": self.hotkey_recorder.text(),
            "apps": apps
        }
