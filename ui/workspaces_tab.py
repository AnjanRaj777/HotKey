from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QMessageBox, QLabel, QListWidgetItem, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.add_workspace_dialog import AddWorkspaceDialog

class WorkspacesTab(QWidget):
    switch_workspace_signal = pyqtSignal(str) # Emits workspace ID
    update_workspaces_signal = pyqtSignal() # Emits when list changes

    def __init__(self, config_manager, workspace_manager):
        super().__init__()
        self.config_manager = config_manager
        self.workspace_manager = workspace_manager
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search workspaces...")
        self.search_input.textChanged.connect(self.filter_workspaces)
        layout.addWidget(self.search_input)
        
        # Workspace List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_switch_clicked) # Double click to switch
        layout.addWidget(self.list_widget)
        
        # Instructions
        layout.addWidget(QLabel("Double-click to Switch Workspace"))

        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Workspace")
        add_btn.clicked.connect(self.add_workspace)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_workspace)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_workspace)
        
        switch_btn = QPushButton("Switch To Selected")
        switch_btn.setStyleSheet("font-weight: bold; background-color: #2da44e; color: white;")
        switch_btn.clicked.connect(self.on_switch_clicked)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(switch_btn)
        
        layout.addLayout(btn_layout)
        
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        workspaces = self.config_manager.get_workspaces()
        for w in workspaces:
            text = f"{w['name']} (Desktop {w.get('desktop_index', 1)})"
            if w.get('launch_hotkey'):
                text += f" [{w['launch_hotkey']}]"
                
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, w['id'])

            self.list_widget.addItem(item)

    def filter_workspaces(self, text):
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text not in item.text().lower())

    def add_workspace(self):
        dialog = AddWorkspaceDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.workspace_manager.create_workspace(
                name=data["name"],
                desktop_index=data["desktop_index"],
                apps=data["apps"],
                launch_hotkey=data["launch_hotkey"]
            )
            self.refresh_list()
            self.update_workspaces_signal.emit()

    def edit_workspace(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
            
        w_id = current_item.data(Qt.ItemDataRole.UserRole)
        w_data = self.config_manager.get_workspace_by_id(w_id)
        
        if w_data:
            dialog = AddWorkspaceDialog(self, workspace_data=w_data)
            if dialog.exec():
                new_data = dialog.get_data()
                # Update in place
                w_data.update(new_data)
                self.config_manager.save_config()
                self.refresh_list()
                self.update_workspaces_signal.emit()

    def remove_workspace(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
            
        w_id = current_item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(self, "Confirm Remove", "Are you sure you want to delete this workspace?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.config_manager.remove_workspace(w_id)
            self.refresh_list()
            self.update_workspaces_signal.emit()

    def on_switch_clicked(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        
        w_id = current_item.data(Qt.ItemDataRole.UserRole)
        self.switch_workspace_signal.emit(w_id)
