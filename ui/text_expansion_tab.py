from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QAbstractItemView, QInputDialog, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal

class TextExpansionTab(QWidget):
    add_snippet_signal = pyqtSignal(str, str) # trigger, replacement
    remove_snippet_signal = pyqtSignal(int)
    toggle_snippet_signal = pyqtSignal(int, bool)

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Active", "Trigger", "Replacement"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Snippet")
        add_btn.clicked.connect(self.prompt_add_snippet)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)

        self.refresh_table()

    def refresh_table(self):
        snippets = self.config_manager.get_snippets()
        self.table.setRowCount(len(snippets))
        
        for i, s in enumerate(snippets):
            # Active Checkbox
            active_cb = QCheckBox()
            active_cb.setChecked(s.get("active", True))
            active_cb.clicked.connect(lambda checked, r=i: self.table.selectRow(r))
            active_cb.stateChanged.connect(lambda state, idx=i: self.emit_toggle(idx, state))
            
            # Center widget
            cb_widget = QWidget()
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.addWidget(active_cb)
            cb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(i, 0, cb_widget)
            self.table.setItem(i, 1, QTableWidgetItem(s["trigger"]))
            self.table.setItem(i, 2, QTableWidgetItem(s["replacement"]))

    def emit_toggle(self, index, state):
        is_active = (state == 2)
        self.toggle_snippet_signal.emit(index, is_active)

    def prompt_add_snippet(self):
        trigger, ok = QInputDialog.getText(self, "Add Snippet", "Enter Trigger (e.g., 'omw'):")
        if not ok or not trigger: return
        
        replacement, ok = QInputDialog.getText(self, "Add Snippet", "Enter Replacement Text:")
        if not ok or not replacement: return
        
        self.add_snippet_signal.emit(trigger, replacement)
        self.refresh_table()

    def remove_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.remove_snippet_signal.emit(row)
            self.refresh_table()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a snippet to remove.")
