from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QCheckBox, QAbstractItemView,
                             QLineEdit, QInputDialog, QComboBox, QMessageBox, 
                             QTabWidget, QFileDialog, QSlider, QColorDialog, QStyle,
                             QApplication, QFrame, QMenu)
from PyQt6.QtGui import QAction, QIcon, QFont, QColor, QPainter, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QRect
import ctypes


class _WinControlBtn(QPushButton):
    """Custom window control button that paints its icon via QPainter.
    symbol: 'min' | 'max' | 'close'
    """
    def __init__(self, symbol: str, is_close=False, parent=None):
        super().__init__(parent)
        self._symbol = symbol
        self._is_close = is_close
        self._hovered = False
        self._pressed = False
        self.setFixedSize(38, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setMouseTracking(True)

        if is_close:
            self.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 6px; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 6px; }
            """)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()

        # --- Background ---
        if self._is_close:
            if self._pressed:
                bg = QColor("#922b21")
            elif self._hovered:
                bg = QColor("#e74c3c")
            else:
                bg = QColor(0, 0, 0, 0)
        else:
            if self._pressed:
                bg = QColor(255, 255, 255, 18)
            elif self._hovered:
                bg = QColor(255, 255, 255, 30)
            else:
                bg = QColor(0, 0, 0, 0)

        if bg.alpha() > 0:
            p.setBrush(bg)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(r, 6, 6)

        # --- Icon color ---
        if self._hovered or self._pressed:
            icon_color = QColor(255, 255, 255, 230)
        else:
            icon_color = QColor(200, 200, 200, 130)

        pen = QPen(icon_color)
        pen.setWidthF(1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)

        cx = r.width() / 2
        cy = r.height() / 2
        s = 5  # half-icon span

        if self._symbol == 'min':
            # Horizontal line
            p.drawLine(int(cx - s), int(cy + 1), int(cx + s), int(cy + 1))

        elif self._symbol == 'max':
            # Square outline
            p.drawRect(int(cx - s), int(cy - s), int(s * 2), int(s * 2))

        elif self._symbol == 'close':
            # X
            p.drawLine(int(cx - s), int(cy - s), int(cx + s), int(cy + s))
            p.drawLine(int(cx + s), int(cy - s), int(cx - s), int(cy + s))

        p.end()

import os
from urllib.parse import urlparse
from ui.add_hotkey_dialog import AddHotkeyDialog
from startup_manager import StartupManager
from ui.text_expansion_tab import TextExpansionTab
from ui.workspaces_tab import WorkspacesTab
from ui.windows_shortcuts_tab import WindowsShortcutsTab
from ui.blur_effect import apply_blur, apply_acrylic_blur, GRADIENT_DEEP_BLUE, remove_blur
from ui.themes import THEMES
from PyQt6.QtCore import QFileSystemWatcher
from context_menu_manager import ContextMenuManager

class MainWindow(QMainWindow):
    # Signals to communicate with the controller/main logic
    start_listener_signal = pyqtSignal(bool) # True = start, False = stop
    add_hotkey_signal = pyqtSignal(str, str, str, bool, bool, str) # trigger, type, target, suppress, long_press, name
    remove_hotkey_signal = pyqtSignal(int)
    toggle_hotkey_signal = pyqtSignal(int, bool)
    update_hotkey_signal = pyqtSignal(int, dict)
    long_press_delay_changed_signal = pyqtSignal(int)
    close_to_tray_signal = pyqtSignal()
    import_config_signal = pyqtSignal()

    def __init__(self, config_manager, workspace_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.workspace_manager = workspace_manager
        self.setWindowTitle("Global Hotkey Manager")
        self.resize(600, 555)
        self.startup_manager = StartupManager()
        self.context_menu_manager = ContextMenuManager()
        
        # Enable frameless window and translucent background for glassmorphism effect
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # For dragging the frameless window
        self._drag_pos = None
        
        # File Watcher for config.json (to detect changes from CLI adds)
        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath(self.config_manager.config_file)
        self.watcher.fileChanged.connect(self.on_config_file_changed)

        self.init_ui()
        self.apply_appearance_settings()

    def init_ui(self):
        self.container = QFrame()
        self.container.setObjectName("AppContainer")
        # Ensure we have a semi-transparent border matching the reference glass card
        self.container.setStyleSheet("""
            QFrame#AppContainer {
                background-color: rgba(12, 14, 26, 0.28);
                border: none;
                border-radius: 8px;
            }
        """)
        self.setCentralWidget(self.container)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(12, 0, 8, 0) # Use the widget for padding
        
        # Custom Title Bar for Frameless Window
        title_bar = QWidget()
        title_bar.setFixedHeight(34)
        title_bar.setStyleSheet("border-bottom: 1px solid rgba(255, 255, 255, 0.08); background: transparent;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(12, 0, 8, 0)
        
        # Notification Light
        self.status_label = QLabel()
        self.status_label.setFixedSize(12, 12)
        self.status_label.setToolTip("Listener Stopped")
        self.status_label.setStyleSheet("background-color: red; border-radius: 6px; border: 1px solid #555;")
        
        # App Icon / Title
        title_icon = QLabel()
        _logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.PNG")
        if os.path.exists(_logo_path):
            title_icon.setPixmap(QIcon(_logo_path).pixmap(20, 20))
        else:
            title_icon.setPixmap(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon).pixmap(20, 20))
        title_label = QLabel("HotKey")
        title_label.setStyleSheet("font-weight: 600; color: #ffffff; font-size: 13px; border: none; background: transparent;")
        
        # Windows Style Min/Max/Close Buttons  (painter-drawn, no font glitches)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(2)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        min_btn = _WinControlBtn('min')
        min_btn.setToolTip("Minimize")
        min_btn.clicked.connect(self.showMinimized)

        max_btn = _WinControlBtn('max')
        max_btn.setToolTip("Maximize / Restore")
        max_btn.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())

        close_btn = _WinControlBtn('close', is_close=True)
        close_btn.setToolTip("Close")
        close_btn.clicked.connect(self.close)

        btn_layout.addWidget(min_btn)
        btn_layout.addWidget(max_btn)
        btn_layout.addWidget(close_btn)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addSpacing(8)
        title_layout.addWidget(self.status_label)
        title_layout.addStretch()
        title_layout.addLayout(btn_layout)
        
        main_layout.addWidget(title_bar)

        # Sort options
        self._sort_options = [
            ("A → Z",  0),
            ("Z → A",  1),
            ("Newest", 2),
            ("Active", 3),
        ]
        self._current_sort_index = 0

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(lambda: self.apply_sorting(self._current_sort_index))

        # Listener button embedded in the tab bar row (corner widget)
        self.toggle_listener_btn = QPushButton("  Stop Listener")
        self.toggle_listener_btn.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.toggle_listener_btn.setCheckable(True)
        self.toggle_listener_btn.setChecked(True)
        self.toggle_listener_btn.clicked.connect(self.on_toggle_listener)
        
        corner_container = QWidget()
        corner_layout = QHBoxLayout(corner_container)
        corner_layout.setContentsMargins(0, 0, 15, 0)  # Add right margin to prevent clipping
        corner_layout.setSpacing(0)
        corner_layout.addWidget(self.toggle_listener_btn)
        self.tabs.setCornerWidget(corner_container, Qt.Corner.TopRightCorner)

        main_layout.addWidget(self.tabs)

        # Tab 1: Hotkeys
        self.hotkey_tab = QWidget()
        self.init_hotkey_tab()
        self.tabs.addTab(self.hotkey_tab, "Hotkeys")

        # Tab 2: Text Expansion
        self.text_expansion_tab = TextExpansionTab(self.config_manager)
        self.tabs.addTab(self.text_expansion_tab, "Text Expansion")

        # Tab 3: Workspaces
        if self.workspace_manager:
            self.workspaces_tab = WorkspacesTab(self.config_manager, self.workspace_manager)
            self.workspaces_tab.switch_workspace_signal.connect(self.on_switch_workspace)
            self.tabs.addTab(self.workspaces_tab, "Workspaces")

        # Tab 4: Windows Shortcuts
        self.shortcuts_tab = WindowsShortcutsTab()
        self.tabs.addTab(self.shortcuts_tab, "Win Shortcuts")

        # Tab 5: Settings
        self.settings_tab = QWidget()
        self.init_settings_tab()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # DEBUG: Force switch to Text Expansion tab
        # self.tabs.setCurrentIndex(1)

    def init_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Startup
        self.startup_cb = QCheckBox("Run on Startup")
        self.startup_cb.setChecked(self.startup_manager.is_startup_enabled())
        self.startup_cb.toggled.connect(self.on_startup_toggled)
        layout.addWidget(self.startup_cb)

        # Context Menu Integration
        self.context_menu_cb = QCheckBox("Show in Explorer Context Menu (Add to HotKey)")
        self.context_menu_cb.setChecked(self.config_manager.get_context_menu_enabled())
        self.context_menu_cb.toggled.connect(self.on_context_menu_toggled)
        layout.addWidget(self.context_menu_cb)

        self.context_menu_cb.toggled.connect(self.on_context_menu_toggled)
        layout.addWidget(self.context_menu_cb)

        # Long Press Delay
        lp_layout = QHBoxLayout()
        lp_layout.addWidget(QLabel("Long Press Delay (ms):"))
        self.lp_slider = QSlider(Qt.Orientation.Horizontal)
        self.lp_slider.setRange(200, 2000)
        self.lp_slider.setSingleStep(50)
        current_lp = self.config_manager.get_long_press_delay()
        self.lp_slider.setValue(current_lp)
        self.lp_slider.valueChanged.connect(self.on_lp_delay_changed)
        lp_layout.addWidget(self.lp_slider)
        self.lp_label = QLabel(f"{current_lp} ms")
        lp_layout.addWidget(self.lp_label)
        layout.addLayout(lp_layout)

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
            current_theme = "Frost Glass" # Fallback
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
        
        # Solid Mode
        self.solid_mode_cb = QCheckBox("Solid Mode (Disable blur for better performance)")
        self.solid_mode_cb.setChecked(self.config_manager.get_solid_mode())
        self.solid_mode_cb.toggled.connect(self.on_solid_mode_toggled)
        layout.addWidget(self.solid_mode_cb)
        
        layout.addSpacing(10)
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
        layout.setContentsMargins(0, 12, 0, 12)
        
        # Search Bar with Embedded Filter
        search_container = QFrame()
        search_container.setObjectName("SortSearchBar")
        search_container.setStyleSheet("""
            QFrame#SortSearchBar {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 10px;
            }
            QFrame#SortSearchBar QLineEdit {
                background: transparent;
                border: none;
                padding: 8px 4px 8px 12px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QFrame#SortSearchBar QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 11px;
                font-weight: 600;
                padding: 0 12px;
                border-left: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 0px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QFrame#SortSearchBar QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }
            QFrame#SortSearchBar QPushButton:pressed {
                background: rgba(255, 255, 255, 0.02);
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search hotkeys...")
        self.search_input.textChanged.connect(self.filter_hotkeys)

        self.sort_btn = QPushButton("\u21c5 A → Z")
        self.sort_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_btn.clicked.connect(self._show_sort_menu)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.sort_btn)
        
        layout.addWidget(search_container)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Active", "Trigger", "Type", "Target", "Name"])
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
            
            # Name Column Logic
            target = hk["target"]
            atype = hk["type"]
            display_name = hk.get("name", "").strip()
            
            if not display_name:
                if atype in ("File", "run", "Folder"):
                    display_name = os.path.basename(os.path.normpath(target))
                elif atype == "open_url":
                    try:
                        parsed = urlparse(target)
                        display_name = parsed.netloc if parsed.netloc else target
                    except:
                        display_name = target
                else:
                    display_name = target
                
            self.table.setItem(i, 4, QTableWidgetItem(display_name))

    def filter_hotkeys(self, text):
        text = text.lower()
        for i in range(self.table.rowCount()):
            match = False
            # Check Trigger (col 1), Type (col 2), Name (col 4)
            if (text in self.table.item(i, 1).text().lower() or 
                text in self.table.item(i, 2).text().lower() or 
                text in self.table.item(i, 4).text().lower()):
                match = True
            self.table.setRowHidden(i, not match)

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
                data["suppress"],
                data.get("long_press", False),
                data.get("name", "")
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()


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

    def _show_sort_menu(self):
        """Show a compact popup menu below the sort pill button."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(18, 20, 36, 0.96);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 10px;
                padding: 4px;
                font-size: 11px;
                color: rgba(255, 255, 255, 0.80);
            }
            QMenu::item {
                padding: 5px 14px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background: rgba(255, 255, 255, 0.10);
                color: #ffffff;
            }
            QMenu::item:checked {
                color: #3498db;
                font-weight: 600;
            }
        """)

        labels = ["⇅  A → Z", "⇅  Z → A", "⇅  Newest", "⇅  Active"]
        for i, label in enumerate(labels):
            action = menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(i == self._current_sort_index)
            action.setData(i)

        # Align the right edge of the menu with the right edge of the button
        pos = self.sort_btn.mapToGlobal(self.sort_btn.rect().bottomRight())
        pos.setX(pos.x() - menu.sizeHint().width())
        action_chosen = menu.exec(pos)
        
        if action_chosen:
            idx = action_chosen.data()
            short = ["A → Z", "Z → A", "Newest", "Active"][idx]
            self.sort_btn.setText(f"⇅ {short}")
            self._current_sort_index = idx
            self.apply_sorting(idx)

    def apply_sorting(self, index):
        current_widget = self.tabs.currentWidget()

        if current_widget == self.hotkey_tab:
            hotkeys = self.config_manager.get_hotkeys()
            if index == 0:
                hotkeys.sort(key=lambda x: x["trigger"].lower())
            elif index == 1:
                hotkeys.sort(key=lambda x: x["trigger"].lower(), reverse=True)
            elif index == 2:
                hotkeys.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            elif index == 3:
                hotkeys.sort(key=lambda x: x.get("active", True), reverse=True)
            self.refresh_table()

        elif current_widget == self.text_expansion_tab:
            self.text_expansion_tab.sort_snippets(index)


    # --- Appearance Handlers ---

    def apply_appearance_settings(self):
        # 1. Start with Base Theme
        theme = self.config_manager.get_theme()
        stylesheet = THEMES.get(theme, "")
        if not stylesheet and theme not in THEMES:
             stylesheet = THEMES.get("Frost Glass", "")
        
        # 2. Get Settings
        hide_labels = self.config_manager.get_hide_labels()
        
        # 3. Apply stylesheet
        self.setStyleSheet(stylesheet)

        # 4. Handle Text Labels
        def set_btn_text(btn, text):
            if hide_labels:
                btn.setText("")
            else:
                btn.setText(text)
                
        if hasattr(self, 'toggle_listener_btn'):
            is_running = self.toggle_listener_btn.isChecked()
            current_text = "Stop Listener" if is_running else "Start Listener"
            set_btn_text(self.toggle_listener_btn, current_text)
            
        if hasattr(self, 'add_hotkey_btn'):
            set_btn_text(self.add_hotkey_btn, "Add Hotkey")
            
        if hasattr(self, 'remove_hotkey_btn'):
            set_btn_text(self.remove_hotkey_btn, "Remove Selected")

        # 5. Opacity — only dims the container overlay; DWM blur stays at full opacity.
        opacity = self.config_manager.get_opacity()
        self.setWindowOpacity(1.0)  # Always keep window fully opaque so DWM acrylic is preserved
        self._set_container_alpha(opacity)

        # 6. Always on Top & FramelessWindowHint
        flags = Qt.WindowType.FramelessWindowHint
        always_on_top = self.config_manager.get_always_on_top()
        if always_on_top:
             flags |= Qt.WindowType.WindowStaysOnTopHint
             
        self.setWindowFlags(flags)
        
        self.show() # Required to re-apply flags
        
        # 7. Apply DWM acrylic blur with deep navy-blue tint (Windows 11 Mica style)
        try:
            if self.config_manager.get_solid_mode():
                remove_blur(int(self.winId()))
                # Overwrite container background to solid color when blur is off
                if hasattr(self, 'container'):
                    self.container.setStyleSheet("""
                        QFrame#AppContainer {
                            background-color: rgb(18, 20, 36);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            border-radius: 20px;
                        }
                    """)
            else:
                apply_acrylic_blur(int(self.winId()), gradient_color=GRADIENT_DEEP_BLUE)
        except Exception as _blur_err:
            print(f"Acrylic blur failed: {_blur_err}")


    def update_accent_btn_color(self, color):
        self.accent_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #555;")

    def on_accent_btn_clicked(self):
        current = self.config_manager.get_accent_color()
        # Ensure we pass a QColor object, not a string
        initial_color = QColor(current) 
        color = QColorDialog.getColor(initial=initial_color, title="Select Accent Color")
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
        # Don't touch setWindowOpacity — that would kill the DWM acrylic blur.
        # Instead, dim only the container overlay so the blur stays solid.
        self._set_container_alpha(opacity)
        self.opacity_label.setText(f"{value}%")

    def _set_container_alpha(self, opacity: float):
        """
        Maps the user's 0.20–1.0 opacity setting to the container background alpha.
        With BLURBEHIND, we need the container itself to provide the dark tint.
        At 1.0  → alpha 0.85  (very dark overlay)
        At 0.20 → alpha 0.20  (nearly invisible overlay, maximum blur / glass feel)
        """
        # Linear interpolation
        min_alpha, max_alpha = 0.20, 0.85
        alpha = min_alpha + (opacity - 0.20) / 0.80 * (max_alpha - min_alpha)
        alpha = max(min_alpha, min(max_alpha, alpha))  # clamp
        if hasattr(self, 'container'):
            self.container.setStyleSheet(f"""
                QFrame#AppContainer {{
                    background-color: rgba(12, 14, 26, {alpha:.2f});
                    border: none;
                    border-radius: 20px;
                }}
            """)

    def on_solid_mode_toggled(self, checked):
        self.config_manager.set_solid_mode(checked)
        self.apply_appearance_settings()

    def on_always_on_top_toggled(self, checked):
        self.config_manager.set_always_on_top(checked)
        # Toggling window flags usually hides the window, so we need to be careful
        flags = Qt.WindowType.FramelessWindowHint
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        # Re-apply acrylic blur because changing flags drops DWM attributes
        try:
            if self.config_manager.get_solid_mode():
                remove_blur(int(self.winId()))
            else:
                apply_acrylic_blur(int(self.winId()), gradient_color=GRADIENT_DEEP_BLUE)
        except Exception as _e:
            print(f"Re-apply blur failed: {_e}")

    def on_context_menu_toggled(self, checked):
        if checked:
            success, msg = self.context_menu_manager.add_context_menu()
            if success:
                self.config_manager.set_context_menu_enabled(True)
            else:
                QMessageBox.critical(self, "Error", msg)
                self.context_menu_cb.setChecked(False) # Revert
        else:
            success, msg = self.context_menu_manager.remove_context_menu()
            if success:
                self.config_manager.set_context_menu_enabled(False)
            else:
                QMessageBox.critical(self, "Error", msg)
                self.context_menu_cb.setChecked(True) # Revert

    def on_lp_delay_changed(self, value):
        self.config_manager.set_long_press_delay(value)
        self.lp_label.setText(f"{value} ms")
        self.refresh_table() # Might need to refresh if we display delay somewhere, but mostly for backend logic

    def on_switch_workspace(self, workspace_id):
        if self.workspace_manager:
            self.workspace_manager.switch_to_workspace(workspace_id)
            QMessageBox.information(self, "Workspace Switched", f"Switched to workspace ID: {workspace_id}")

    def on_config_file_changed(self, path):
        # Reload config from disk
        print(f"Config file changed: {path}")
        # Small delay might be needed if write is atomic/swap?
        # But let's try direct reload
        try:
            self.config_manager.reload_config()
            self.refresh_table()
            
            if hasattr(self, 'text_expansion_tab') and hasattr(self.text_expansion_tab, 'refresh_table'):
                self.text_expansion_tab.refresh_table()
            
            if hasattr(self, 'workspaces_tab') and hasattr(self.workspaces_tab, 'refresh_list'):
                self.workspaces_tab.refresh_list()
            
            # Emit signal to notify main controller (to reload hooks)
            self.import_config_signal.emit()
            
            # Re-add path to watcher if it was deleted/moved (some editors do atomic write by swap)
            if not self.watcher.files():
                self.watcher.addPath(self.config_manager.config_file)
                
        except Exception as e:
            print(f"Error reloading config: {e}")
