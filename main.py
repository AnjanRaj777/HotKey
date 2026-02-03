import sys
import os
import ctypes
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon
from ui.ai_voice_widget import AiVoiceWidget
from config_manager import ConfigManager
from hotkey_manager import HotkeyManager
from text_expander import TextExpander
from workspace_manager import WorkspaceManager
from PyQt6.QtCore import pyqtSignal, QObject

# Signal helper to bridge threads
class SignalHelper(QObject):
    launch_ai = pyqtSignal(str)

def main():
    # Fix Taskbar Icon on Windows
    # Windows groups all python processes under the python icon unless we set a unique AppUserModelID
    try:
        myappid = 'anjanraj.hotkey.manager.1.0' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"Failed to set AppUserModelID: {e}")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Keep app running when window is closed (minimized to tray)
    
    # Set App Icon
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Initialize Core Components
    print("Starting main...")
    config_manager = ConfigManager()
    print("Config loaded")

    # Check for CLI arguments
    if len(sys.argv) > 2 and sys.argv[1] == "--add-hotkey":
        file_path = sys.argv[2]
        print(f"Adding hotkey for: {file_path}")
        # Add to config with a placeholder trigger
        config_manager.add_hotkey(trigger_key="<Assign Key>", 
                                  action_type="run", 
                                  action_target=file_path, 
                                  suppress=False)
        print("Hotkey added successfully.")
        sys.exit(0)

    hotkey_manager = HotkeyManager(config_manager)
    text_expander = TextExpander(config_manager)
    workspace_manager = WorkspaceManager(config_manager, hotkey_manager)
    hotkey_manager.set_workspace_switcher(workspace_manager.switch_to_workspace)
    
    # Initialize UI
    print("Initializing UI...")
    main_window = MainWindow(config_manager, workspace_manager)
    print("UI initialized")
    tray_icon = TrayIcon(main_window)
    tray_icon.show()
    
    # --- Anywhere AI Setup ---
    ai_widget = None
    signal_helper = SignalHelper()

    def launch_ai_voice(url):
        # This function runs on the main thread via signal
        nonlocal ai_widget
        print(f"Launching AI Voice: {url}")
        if ai_widget:
            ai_widget.close()
            ai_widget = None
        
        # Default URL if empty
        if not url or url == "AI Bot URL (e.g., https://chatgpt.com/)":
             url = "https://chatgpt.com/"
        
        ai_widget = AiVoiceWidget(url)
        ai_widget.show()
        ai_widget.raise_()
        ai_widget.activateWindow()

    signal_helper.launch_ai.connect(launch_ai_voice)
    hotkey_manager.set_ai_voice_callback(signal_helper.launch_ai.emit)

    # --- Managers Control ---
    def start_listeners():
        hotkey_manager.start_listener()
        text_expander.start_listener()

    def stop_listeners():
        hotkey_manager.stop_listener()
        text_expander.stop_listener()
    
    def refresh_hotkeys():
        if hotkey_manager.is_running:
            hotkey_manager.reload_hotkeys()

    def refresh_snippets():
        if text_expander.is_running:
            text_expander.reload_snippets()

    # Connect Signals
    main_window.start_listener_signal.connect(lambda start: start_listeners() if start else stop_listeners())
    
    # Hotkey Signals
    main_window.add_hotkey_signal.connect(lambda t, typ, tar, sup: [config_manager.add_hotkey(t, typ, tar, sup), refresh_hotkeys()])
    main_window.remove_hotkey_signal.connect(lambda idx: [config_manager.remove_hotkey(idx), refresh_hotkeys()])
    main_window.toggle_hotkey_signal.connect(lambda idx, state: [config_manager.update_hotkey_status(idx, state), refresh_hotkeys()])
    main_window.update_hotkey_signal.connect(lambda idx, data: [config_manager.update_hotkey(idx, data), refresh_hotkeys()])
    
    # Text Expansion Signals
    # Note: Accessing the tab directly or through a signal from main_window?
    # MainWindow doesn't bubble up signals from TextExpansionTab by default unless we connect them.
    # Approach: Instantiating TextExpansionTab inside MainWindow makes it hard to access its signals here unless MainWindow exposes them.
    # BETTER: MainWindow exposes the instantiated tabs or we connect to signals on the tab object directly if accessible.
    # Accessing via main_window.text_expansion_tab
    te_tab = main_window.text_expansion_tab
    te_tab.add_snippet_signal.connect(lambda trig, repl: [config_manager.add_snippet(trig, repl), refresh_snippets()])
    te_tab.remove_snippet_signal.connect(lambda idx: [config_manager.remove_snippet(idx), refresh_snippets()])
    te_tab.toggle_snippet_signal.connect(lambda idx, state: [config_manager.update_snippet_status(idx, state), refresh_snippets()])
    te_tab.update_snippet_signal.connect(lambda idx, trig, repl: [config_manager.update_snippet(idx, trig, repl), refresh_snippets()])

    # Import Signal
    main_window.import_config_signal.connect(lambda: [refresh_hotkeys(), refresh_snippets()])

    
    # Handle "Close to Tray" signal
    # The clean implementation is already in MainWindow.closeEvent which hides the window.
    # We just need to ensure the app doesn't quit (handled by setQuitOnLastWindowClosed(False))

    # Auto-start listener if configured? (Optional, skipping for now, defaults to stopped)
    # hotkey_manager.start_listener() # Uncomment to auto-start

    # Show window initially?
    main_window.show()

    # Auto-start listener
    main_window.toggle_listener_btn.setChecked(True)
    main_window.on_toggle_listener()

    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to continue...")  # Keep window open if run from double-click
