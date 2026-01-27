import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QCheckBox, QAbstractItemView,
                             QInputDialog, QComboBox, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.add_hotkey_dialog import AddHotkeyDialog
from startup_manager import StartupManager
from ui.text_expansion_tab import TextExpansionTab

class MainWindow(QMainWindow):
    # Signals to communicate with the controller/main logic
    start_listener_signal = pyqtSignal(bool) # True = start, False = stop
    add_hotkey_signal = pyqtSignal(str, str, str, bool) # trigger, type, target, suppress
    remove_hotkey_signal = pyqtSignal(int)
    toggle_hotkey_signal = pyqtSignal(int, bool)
    close_to_tray_signal = pyqtSignal()

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.setWindowTitle("Global Hotkey Manager")
        self.resize(600, 400)
        self.startup_manager = StartupManager()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header (Common for both tabs)
        header_layout = QHBoxLayout()
        self.status_label = QLabel("Listener Status: STOPPED")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.toggle_listener_btn = QPushButton("Start Listener")
        self.toggle_listener_btn.setCheckable(True)
        self.toggle_listener_btn.clicked.connect(self.on_toggle_listener)
        
        # Startup Checkbox
        self.startup_cb = QCheckBox("Run on Startup")
        self.startup_cb.setChecked(self.startup_manager.is_startup_enabled())
        self.startup_cb.toggled.connect(self.on_startup_toggled)

        header_layout.addWidget(self.status_label)
        header_layout.addStretch()
        header_layout.addWidget(self.startup_cb)
        header_layout.addWidget(self.toggle_listener_btn)
        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Hotkeys
        self.hotkey_tab = QWidget()
        self.init_hotkey_tab()
        self.tabs.addTab(self.hotkey_tab, "Hotkeys")

        # Tab 2: Text Expansion
        self.text_expansion_tab = TextExpansionTab(self.config_manager)
        self.tabs.addTab(self.text_expansion_tab, "Text Expansion")

    def init_hotkey_tab(self):
        layout = QVBoxLayout(self.hotkey_tab)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Active", "Trigger", "Type", "Target", "Block"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Hotkey")
        add_btn.clicked.connect(self.prompt_add_hotkey)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected_hotkey)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)

        self.refresh_table()

    def refresh_table(self):
        hotkeys = self.config_manager.get_hotkeys()
        self.table.setRowCount(len(hotkeys))
        
        for i, hk in enumerate(hotkeys):
            # Active Checkbox
            active_cb = QCheckBox()
            active_cb.setChecked(hk.get("active", True))
            active_cb.clicked.connect(lambda checked, r=i: self.table.selectRow(r))
            active_cb.stateChanged.connect(lambda state, idx=i: self.emit_toggle_hotkey(idx, state))
            
            # Center the checkbox
            cb_widget = QWidget()
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.addWidget(active_cb)
            cb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(i, 0, cb_widget)
            self.table.setItem(i, 1, QTableWidgetItem(hk["trigger"]))
            self.table.setItem(i, 2, QTableWidgetItem(hk["type"]))
            self.table.setItem(i, 3, QTableWidgetItem(hk["target"]))
            self.table.setItem(i, 4, QTableWidgetItem("Yes" if hk.get("suppress", False) else "No"))

    def emit_toggle_hotkey(self, index, state):
        is_active = (state == 2) # 2 is Checked
        self.toggle_hotkey_signal.emit(index, is_active)

    def on_toggle_listener(self):
        is_running = self.toggle_listener_btn.isChecked()
        if is_running:
            self.toggle_listener_btn.setText("Stop Listener")
            self.status_label.setText("Listener Status: RUNNING")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.toggle_listener_btn.setText("Start Listener")
            self.status_label.setText("Listener Status: STOPPED")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.start_listener_signal.emit(is_running)

    def prompt_add_hotkey(self):
        dialog = AddHotkeyDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.add_hotkey_signal.emit(
                data["trigger"], 
                data["type"], 
                data["target"], 
                data["suppress"]
            )
            self.refresh_table()

    def remove_selected_hotkey(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.remove_hotkey_signal.emit(current_row)
            self.refresh_table()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a row to remove.")

    def on_startup_toggled(self, checked):
        self.startup_manager.set_startup(checked)

    def closeEvent(self, event):
        # Override close event to minimize to tray instead
        event.ignore()
        self.hide()
        self.close_to_tray_signal.emit()
