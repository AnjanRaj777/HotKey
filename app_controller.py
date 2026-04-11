import sys
import os
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon
from ui.ai_voice_widget import AiVoiceWidget
from config_manager import ConfigManager
from hotkey_manager import HotkeyManager
from text_expander import TextExpander
from workspace_manager import WorkspaceManager

# Signal helper to bridge threads
class SignalHelper(QObject):
    launch_ai = pyqtSignal(str)

class AppController:
    def __init__(self):
        self.app = None
        self.config_manager = None
        self.hotkey_manager = None
        self.text_expander = None
        self.workspace_manager = None
        self.main_window = None
        self.tray_icon = None
        self.ai_widgets = []
        self.signal_helper = SignalHelper()

    def setup_app(self, sys_argv):
        self.app = QApplication(sys_argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set App Icon
        # Assuming assets are relative to the controller or main script. 
        # Using abspath of this file's directory to potentiall find assets if they are in a parallel dir
        # But commonly assets are near main.py. Let's assume standard structure.
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "assets", "app_icon.ico")
        
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
        
        return self.app

    def initialize_core(self):
        print("Initializing Core Components...")
        self.config_manager = ConfigManager()
        
        self.hotkey_manager = HotkeyManager(self.config_manager)
        self.text_expander = TextExpander(self.config_manager)
        self.workspace_manager = WorkspaceManager(self.config_manager, self.hotkey_manager)
        
        # Wire up Workspace Switcher
        self.hotkey_manager.set_workspace_switcher(self.workspace_manager.switch_to_workspace)
        
        # Wire up AI Voice Callback
        self.signal_helper.launch_ai.connect(self.launch_ai_voice)
        self.hotkey_manager.set_ai_voice_callback(self.signal_helper.launch_ai.emit)

    def initialize_ui(self):
        print("Initializing UI...")
        self.main_window = MainWindow(self.config_manager, self.workspace_manager)
        self.tray_icon = TrayIcon(self.main_window)
        self.tray_icon.show()

        # Connect Signals
        self._connect_signals()
        
        # Initial State
        self.main_window.show()
        
        # Auto-start listener by default (as per previous main.py logic)
        self.main_window.toggle_listener_btn.setChecked(True)
        self.main_window.on_toggle_listener()

    def _connect_signals(self):
        # Listener Control
        self.main_window.start_listener_signal.connect(
            lambda start: self.start_listeners() if start else self.stop_listeners()
        )
        
        # Hotkey Management Signals
        self.main_window.add_hotkey_signal.connect(
            lambda t, typ, tar, sup, lp, name: [self.config_manager.add_hotkey(t, typ, tar, sup, lp, name), self.refresh_hotkeys()]
        )
        self.main_window.remove_hotkey_signal.connect(
            lambda idx: [self.config_manager.remove_hotkey(idx), self.refresh_hotkeys()]
        )
        self.main_window.toggle_hotkey_signal.connect(
            lambda idx, state: [self.config_manager.update_hotkey_status(idx, state), self.refresh_hotkeys()]
        )
        self.main_window.update_hotkey_signal.connect(
            lambda idx, data: [self.config_manager.update_hotkey(idx, data), self.refresh_hotkeys()]
        )
        
        # Text Expansion Signals
        te_tab = self.main_window.text_expansion_tab
        te_tab.add_snippet_signal.connect(
            lambda trig, repl: [self.config_manager.add_snippet(trig, repl), self.refresh_snippets()]
        )
        te_tab.remove_snippet_signal.connect(
            lambda idx: [self.config_manager.remove_snippet(idx), self.refresh_snippets()]
        )
        te_tab.toggle_snippet_signal.connect(
            lambda idx, state: [self.config_manager.update_snippet_status(idx, state), self.refresh_snippets()]
        )
        te_tab.update_snippet_signal.connect(
            lambda idx, trig, repl: [self.config_manager.update_snippet(idx, trig, repl), self.refresh_snippets()]
        )
        
        # Import/Export
        self.main_window.import_config_signal.connect(
            lambda: [self.refresh_hotkeys(), self.refresh_snippets()]
        )

    def start_listeners(self):
        self.hotkey_manager.start_listener()
        self.text_expander.start_listener()

    def stop_listeners(self):
        self.hotkey_manager.stop_listener()
        self.text_expander.stop_listener()

    def refresh_hotkeys(self):
        if self.hotkey_manager.is_running:
            self.hotkey_manager.reload_hotkeys()

    def refresh_snippets(self):
        if self.text_expander.is_running:
            self.text_expander.reload_snippets()

    def launch_ai_voice(self, url):
        print(f"Launching AI Voice: {url}")
        try:
            # Default URL if empty
            if not url or url == "AI Bot URL (e.g., https://chatgpt.com/)":
                 url = "https://chatgpt.com/"
            
            widget = AiVoiceWidget(url)
            widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            
            def on_destroyed():
                if widget in self.ai_widgets:
                    self.ai_widgets.remove(widget)
            widget.destroyed.connect(on_destroyed)
            
            self.ai_widgets.append(widget)
            widget.show()
            widget.raise_()
            widget.activateWindow()
        except Exception as e:
            print(f"CRASH in launch_ai_voice: {e}")
            import traceback
            traceback.print_exc()

    def run(self):
        if not self.app:
            print("Error: App not setup. Call setup_app() first.")
            return
        
        self.initialize_core()
        self.initialize_ui()
        
        sys.exit(self.app.exec())
