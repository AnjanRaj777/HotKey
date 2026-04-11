from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QLabel, QAbstractItemView)
from PyQt6.QtCore import Qt

class WindowsShortcutsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        
        # Search / Filter
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search shortcuts...")
        self.search_input.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Shortcut", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.populate_shortcuts()

    def populate_shortcuts(self):
        self.shortcuts = [
             ("Win", "Open Start Menu"),
             ("Win + D", "Show Desktop (Minimize/Restore all)"),
             ("Win + E", "Open File Explorer"),
             ("Win + I", "Open Settings"),
             ("Win + L", "Lock PC"),
             ("Win + M", "Minimize all windows"),
             ("Win + R", "Open Run dialog"),
             ("Win + S", "Open Search"),
             ("Win + X", "Open Quick Link menu"),
             ("Win + .", "Open Emoji Panel"),
             ("Win + Left/Right", "Snap window to side"),
             ("Win + Up", "Maximize window"),
             ("Win + Down", "Minimize/Restore window"),
             ("Win + Tab", "Open Task View"),
             ("Win + Ctrl + D", "Create new virtual desktop"),
             ("Win + Ctrl + F4", "Close current virtual desktop"),
             ("Win + Ctrl + Left/Right", "Switch virtual desktops"),
             ("Win + Shift + S", "Take screenshot (Snipping Tool)"),
             ("Win + V", "Open Clipboard History"),
             ("Ctrl + C", "Copy"),
             ("Ctrl + X", "Cut"),
             ("Ctrl + V", "Paste"),
             ("Ctrl + Z", "Undo"),
             ("Ctrl + Y", "Redo"),
             ("Ctrl + A", "Select All"),
             ("Ctrl + F", "Find"),
             ("Ctrl + Shift + Esc", "Open Task Manager"),
             ("Alt + Tab", "Switch apps"),
             ("Alt + F4", "Close active window"),
        ]
        
        self.shortcuts.sort(key=lambda x: x[0]) # Sort by keys
        
        self.update_table(self.shortcuts)

    def update_table(self, data):
        self.table.setRowCount(len(data))
        for i, (keys, desc) in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(keys))
            self.table.setItem(i, 1, QTableWidgetItem(desc))

    def filter_table(self, text):
        filtered = [
            (k, d) for k, d in self.shortcuts 
            if text.lower() in k.lower() or text.lower() in d.lower()
        ]
        self.update_table(filtered)
