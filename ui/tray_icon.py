from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolTip("Global Keyboard Utility")
        
        # Create a simple icon (placeholder if file missing, though QSystemTrayIcon needs one)
        # For now, we'll try to use a standard system icon if possible or a simple emoji
        # In a real app, we'd load a .ico or .png
        # self.setIcon(QIcon("icon.png")) 
        # Using a standard icon from style if possible, or just empty for now until user adds one
        # Actually, PyQt6 might not show anything if icon is null. 
        # Let's try to grab a standard icon.
        self_icon = self.parent().style().standardIcon(self.parent().style().StandardPixmap.SP_ComputerIcon)
        self.setIcon(self_icon)

        self.menu = QMenu(parent)
        
        self.open_action = self.menu.addAction("Open Settings")
        self.open_action.triggered.connect(self.on_open)
        
        self.menu.addSeparator()
        
        self.exit_action = self.menu.addAction("Exit")
        self.exit_action.triggered.connect(self.on_exit)
        
        self.setContextMenu(self.menu)
        self.activated.connect(self.on_activated)

    def on_open(self):
        if self.parent():
            self.parent().show()
            self.parent().activateWindow()

    def on_exit(self):
        QCoreApplication.quit()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.on_open()
