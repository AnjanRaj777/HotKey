from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QCheckBox, QAbstractItemView,
                             QInputDialog, QComboBox, QMessageBox, QTabWidget, QFileDialog, QSlider, QColorDialog, QStyle, QApplication)
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal
from ui.add_hotkey_dialog import AddHotkeyDialog
from startup_manager import StartupManager
from ui.text_expansion_tab import TextExpansionTab
from ui.blur_effect import apply_blur
from ui.themes import THEMES

class MainWindow(QMainWindow):
    # Signals to communicate with the controller/main logic
    start_listener_signal = pyqtSignal(bool) # True = start, False = stop
    add_hotkey_signal = pyqtSignal(str, str, str, bool) # trigger, type, target, suppress
    remove_hotkey_signal = pyqtSignal(int)
    toggle_hotkey_signal = pyqtSignal(int, bool)
    update_hotkey_signal = pyqtSignal(int, dict)
    close_to_tray_signal = pyqtSignal()
    import_config_signal = pyqtSignal()

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.setWindowTitle("Global Hotkey Manager")
        self.resize(600, 400)
        self.startup_manager = StartupManager()
        self.apply_appearance_settings()
        self.init_ui()

    def init_ui(self):


        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header (Common for both tabs)
        header_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setFixedSize(12, 12)
        self.status_label.setToolTip("Listener Stopped")
        self.status_label.setStyleSheet("background-color: red; border-radius: 6px; border: 1px solid #555;")
        self.toggle_listener_btn = QPushButton("Start Listener")
        self.toggle_listener_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.toggle_listener_btn.setCheckable(True)
        self.toggle_listener_btn.clicked.connect(self.on_toggle_listener)
        
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_listener_btn)
        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        
        # Sort Combo
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Trigger (A-Z)", "Trigger (Z-A)", "Date Added (Newest)", "Active Status"])
        self.sort_combo.setFixedWidth(150)
        self.sort_combo.currentIndexChanged.connect(self.apply_sorting)
        
        self.tabs.setCornerWidget(self.sort_combo, Qt.Corner.TopRightCorner)
        self.tabs.currentChanged.connect(lambda: self.apply_sorting(self.sort_combo.currentIndex()))

        main_layout.addWidget(self.tabs)

        # Tab 1: Hotkeys
        self.hotkey_tab = QWidget()
        self.init_hotkey_tab()
        self.tabs.addTab(self.hotkey_tab, "Hotkeys")

        # Tab 2: Text Expansion
        self.text_expansion_tab = TextExpansionTab(self.config_manager)
        self.tabs.addTab(self.text_expansion_tab, "Text Expansion")

        # Tab 3: Settings
        self.settings_tab = QWidget()
        self.init_settings_tab()
        self.tabs.addTab(self.settings_tab, "Settings")

    def init_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Startup
        self.startup_cb = QCheckBox("Run on Startup")
        self.startup_cb.setChecked(self.startup_manager.is_startup_enabled())
        self.startup_cb.toggled.connect(self.on_startup_toggled)
        layout.addWidget(self.startup_cb)

        layout.addSpacing(20)

        # Appearance Section
        appearance_label = QLabel("General & Appearance")
        appearance_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(appearance_label)

        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        
        # Handle current theme that might not match new names
        current_theme = self.config_manager.get_theme()
        if current_theme not in THEMES:
            current_theme = "Dark (VS Code)" # Fallback
            self.config_manager.set_theme(current_theme)
            
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Window Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100) # 20% to 100%
        current_opacity = int(self.config_manager.get_opacity() * 100)
        self.opacity_slider.setValue(current_opacity)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel(f"{current_opacity}%")
        opacity_layout.addWidget(self.opacity_label)
        layout.addLayout(opacity_layout)

        # Always on Top
        self.always_on_top_cb = QCheckBox("Always on Top")
        self.always_on_top_cb.setChecked(self.config_manager.get_always_on_top())
        self.always_on_top_cb.toggled.connect(self.on_always_on_top_toggled)
        layout.addWidget(self.always_on_top_cb)
        
        layout.addSpacing(10)
        
        # --- Advanced Appearance ---
        adv_label = QLabel("Custom Appearance")
        adv_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #888;")
        layout.addWidget(adv_label)
        
        # Accent Color
        accent_layout = QHBoxLayout()
        accent_layout.addWidget(QLabel("Accent Color:"))
        self.accent_btn = QPushButton()
        self.accent_btn.setFixedSize(50, 20)
        self.update_accent_btn_color(self.config_manager.get_accent_color())
        self.accent_btn.clicked.connect(self.on_accent_btn_clicked)
        accent_layout.addWidget(self.accent_btn)
        accent_layout.addStretch()
        layout.addLayout(accent_layout)
        
        # Corner Radius
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Corner Radius:"))
        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setRange(0, 20)
        current_radius = self.config_manager.get_corner_radius()
        self.radius_slider.setValue(current_radius)
        self.radius_slider.valueChanged.connect(self.on_corner_radius_changed)
        radius_layout.addWidget(self.radius_slider)
        self.radius_label = QLabel(f"{current_radius}px")
        radius_layout.addWidget(self.radius_label)
        layout.addLayout(radius_layout)
        
        # Hide Text Labels
        self.hide_labels_cb = QCheckBox("Hide Text Labels (Icons Only)")
        self.hide_labels_cb.setChecked(self.config_manager.get_hide_labels())
        self.hide_labels_cb.toggled.connect(self.on_hide_labels_toggled)
        layout.addWidget(self.hide_labels_cb)

        layout.addSpacing(20)

        # Backup / Restore Section
        backup_label = QLabel("Backup and Restore")
        backup_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(backup_label)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        export_btn = QPushButton("Export Backup")
        export_btn.clicked.connect(self.export_backup)
        btn_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import Backup")
        import_btn.clicked.connect(self.import_backup)
        btn_layout.addWidget(import_btn)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()

    def init_hotkey_tab(self):
        layout = QVBoxLayout(self.hotkey_tab)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Active", "Trigger", "Type", "Target", "Block"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_hotkey)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Hotkey")
        add_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        add_btn.clicked.connect(self.prompt_add_hotkey)
        self.add_hotkey_btn = add_btn # Store ref for hiding labels

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        remove_btn.clicked.connect(self.remove_selected_hotkey)
        self.remove_hotkey_btn = remove_btn # Store ref
        
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
            self.toggle_listener_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
            self.status_label.setStyleSheet("background-color: green; border-radius: 6px; border: 1px solid #555;")
            self.status_label.setToolTip("Listener Running")
        else:
            self.toggle_listener_btn.setText("Start Listener")
            self.toggle_listener_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.status_label.setStyleSheet("background-color: red; border-radius: 6px; border: 1px solid #555;")
            self.status_label.setToolTip("Listener Stopped")
        
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

    def edit_hotkey(self, row, column):
        # Allow editing by double clicking
        hotkeys = self.config_manager.get_hotkeys()
        if 0 <= row < len(hotkeys):
            data = hotkeys[row]
            dialog = AddHotkeyDialog(self, hotkey_data=data)
            if dialog.exec():
                new_data = dialog.get_data()
                self.update_hotkey_signal.emit(row, new_data)
                self.refresh_table()

    def on_startup_toggled(self, checked):
        self.startup_manager.set_startup(checked)

    def closeEvent(self, event):
        # Override close event to minimize to tray instead
        event.ignore()
        self.hide()
        self.close_to_tray_signal.emit()

    def export_backup(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Backup", "backup.json", "JSON Files (*.json)")
        if file_path:
            success, msg = self.config_manager.export_to_file(file_path)
            if success:
                QMessageBox.information(self, "Success", "Backup exported successfully!")
            else:
                QMessageBox.critical(self, "Error", msg)

    def import_backup(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Backup", "", "JSON Files (*.json)")
        if file_path:
            confirm = QMessageBox.question(self, "Confirm Import", 
                                           "Importing will overwrite current settings. Continue?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                success, msg = self.config_manager.import_from_file(file_path)
                if success:
                    self.refresh_table()
                    self.text_expansion_tab.refresh_table()
                    self.import_config_signal.emit()
                    # Re-apply appearance settings in case they changed
                    self.apply_appearance_settings()
                    QMessageBox.information(self, "Success", "Backup imported successfully!")
                else:
                    QMessageBox.critical(self, "Error", msg)

    def apply_sorting(self, index):
        current_widget = self.tabs.currentWidget()
        
        if current_widget == self.hotkey_tab:
            hotkeys = self.config_manager.get_hotkeys()
            if index == 0: # Trigger A-Z
                hotkeys.sort(key=lambda x: x["trigger"].lower())
            elif index == 1: # Trigger Z-A
                hotkeys.sort(key=lambda x: x["trigger"].lower(), reverse=True)
            elif index == 2: # Date Added
                hotkeys.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            elif index == 3: # Active Status
                hotkeys.sort(key=lambda x: x.get("active", True), reverse=True)
            
            self.config_manager.save_config()
            self.refresh_table()
            
        elif current_widget == self.text_expansion_tab:
            self.text_expansion_tab.sort_snippets(index)

    # --- Appearance Handlers ---

    def apply_appearance_settings(self):
        # 1. Start with Base Theme
        theme = self.config_manager.get_theme()
        stylesheet = THEMES.get(theme, "")
        if not stylesheet and theme not in THEMES:
             stylesheet = THEMES.get("Default Dark", "")
        
        # 2. Get Advanced Settings
        accent = self.config_manager.get_accent_color()
        radius = self.config_manager.get_corner_radius()
        hide_labels = self.config_manager.get_hide_labels()
        
        # 3. Construct Overrides
        overrides = ""
        
        # Accent Color & Corner Radius
        # We target specific widgets to apply these overrides
        overrides += f"""
            QPushButton {{
                background-color: {accent};
                border-radius: {radius}px;
                border: 1px solid {accent};
            }}
            QPushButton:hover {{
                background-color: {accent}; /* Or slightly lighter? */
                border: 1px solid #ffffff;
            }}
            QLineEdit, QComboBox {{
                border-radius: {radius}px;
                border: 1px solid #555; /* Default border */
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {accent};
            }}
            QTabBar::tab:selected {{
                border-top: 2px solid {accent};
            }}
            QSlider::handle:horizontal {{
                background: {accent};
            }}
        """
        
        # Combine and Apply
        full_stylesheet = stylesheet + overrides
        self.setStyleSheet(full_stylesheet)

        # 4. Handle Text Labels
        # We need to toggle text on specific buttons.
        # Ideally, we should store their original text.
        # For simplicity, we hardcode the known original texts here since we control them.
        
        def set_btn_text(btn, text):
            if hide_labels:
                btn.setText("")
            else:
                btn.setText(text)
                
        # Main Window Buttons
        if hasattr(self, 'toggle_listener_btn'):
            # Dynamic text for listener button
            is_running = self.toggle_listener_btn.isChecked()
            current_text = "Stop Listener" if is_running else "Start Listener"
            set_btn_text(self.toggle_listener_btn, current_text)
            
        if hasattr(self, 'add_hotkey_btn'):
            set_btn_text(self.add_hotkey_btn, "Add Hotkey")
            
        if hasattr(self, 'remove_hotkey_btn'):
            set_btn_text(self.remove_hotkey_btn, "Remove Selected")
            
        if hasattr(self, 'export_btn'): # Only if we stored ref, let's check init_ui modifications
            pass # We didn't store export/import refs in init_ui yet implementation plan. 
                 # Wait, plan said "Assign standard Qt icons... so they are visible".
                 # I haven't added refs for export/import yet. Let's do that in a separate chunk or just apply to known ones.

        # Opacity
        opacity = self.config_manager.get_opacity()
        self.setWindowOpacity(opacity)

        # Always on Top
        always_on_top = self.config_manager.get_always_on_top()
        if always_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        
        self.show() # Required to re-apply flags
        
        # Apply Blur Effect
        try:
            apply_blur(int(self.winId()))
        except Exception as e:
            print(f"Error applying blur: {e}")

    def update_accent_btn_color(self, color):
        self.accent_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #555;")

    def on_accent_btn_clicked(self):
        current = self.config_manager.get_accent_color()
        color = QColorDialog.getColor(initial=current, title="Select Accent Color")
        if color.isValid():
            hex_color = color.name()
            self.config_manager.set_accent_color(hex_color)
            self.update_accent_btn_color(hex_color)
            self.apply_appearance_settings()

    def on_corner_radius_changed(self, value):
        self.config_manager.set_corner_radius(value)
        self.radius_label.setText(f"{value}px")
        # Apply immediately for feedback? heavy? CSS re-parse is fast enough usually.
        self.apply_appearance_settings()

    def on_hide_labels_toggled(self, checked):
        self.config_manager.set_hide_labels(checked)
        self.apply_appearance_settings()

    def on_theme_changed(self, text):
        self.config_manager.set_theme(text)
        self.apply_appearance_settings()

    def on_opacity_changed(self, value):
        opacity = value / 100.0
        self.config_manager.set_opacity(opacity)
        self.setWindowOpacity(opacity)
        self.opacity_label.setText(f"{value}%")

    def on_always_on_top_toggled(self, checked):
        self.config_manager.set_always_on_top(checked)
        # Toggling window flags usually hides the window, so we need to be careful
        # apply_appearance_settings calls show(), which handles it.
        # However, calling it directly here for smoother UX
        if checked:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show()
