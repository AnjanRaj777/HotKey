from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QListWidget, QListWidgetItem, QPushButton, QLabel,
                             QAbstractItemView, QFileIconProvider)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QFileInfo
from PyQt6.QtGui import QIcon
import os
import sys
import pythoncom

# Append parent directory to path to import installed_apps_loader if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from installed_apps_loader import get_installed_apps
except ImportError:
    # Fallback or local import attempt
    import sys
    sys.path.append("..")
    from installed_apps_loader import get_installed_apps

class AppLoaderThread(QThread):
    apps_loaded = pyqtSignal(list)

    def run(self):
        pythoncom.CoInitialize()
        apps = get_installed_apps()
        self.apps_loaded.emit(apps)
        pythoncom.CoUninitialize()

class AppSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Application")
        self.resize(500, 600)
        self.selected_app_path = None
        self.all_apps = []

        self.init_ui()
        self.load_apps()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for an app...")
        self.search_input.textChanged.connect(self.filter_apps)
        layout.addWidget(self.search_input)

        # App List
        self.app_list_widget = QListWidget()
        self.app_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.app_list_widget.setIconSize(QSize(32, 32))
        self.app_list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.app_list_widget)

        # Loading Label
        self.loading_label = QLabel("Loading apps...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.accept_selection)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(select_btn)
        layout.addLayout(btn_layout)

    def load_apps(self):
        self.loader_thread = AppLoaderThread()
        self.loader_thread.apps_loaded.connect(self.on_apps_loaded)
        self.loader_thread.start()

    def on_apps_loaded(self, apps):
        self.all_apps = apps
        self.loading_label.hide()
        self.populate_list(apps)

    def populate_list(self, apps):
        self.app_list_widget.clear()
        provider = QFileIconProvider()
        
        for app in apps:
            item = QListWidgetItem(app['name'])
            item.setData(Qt.ItemDataRole.UserRole, app['path'])
            item.setToolTip(app['path'])
            
            # Try to get icon
            # QFileIconProvider works for files, let's try
            # For .lnk it might get the shortcut icon, for .exe the exe icon
            # Since get_installed_apps resolves to .exe, we use that if we can,
            # but sometimes fetching icons for exes is slow or requires manual extraction.
            # Let's try default provider on the path.
            icon = provider.icon(QFileInfo(os.path.normpath(app['path'])))
            if not icon or icon.isNull():
                 # Fallback to default executable icon or similar?
                 # Actually for now let's just accept what QFileIconProvider gives
                 pass
            
            item.setIcon(icon)
            self.app_list_widget.addItem(item)

    def filter_apps(self, text):
        filtered = [
            app for app in self.all_apps 
            if text.lower() in app['name'].lower()
        ]
        self.populate_list(filtered)

    def accept_selection(self):
        selected_items = self.app_list_widget.selectedItems()
        if selected_items:
            self.selected_app_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            # Maybe show a message? Or just ignore
            pass

    def get_selected_app(self):
        return self.selected_app_path
