import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon
from config_manager import ConfigManager
from hotkey_manager import HotkeyManager
from text_expander import TextExpander

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Keep app running when window is closed (minimized to tray)

    # Initialize Core Components
    print("Starting main...")
    config_manager = ConfigManager()
    print("Config loaded")
    hotkey_manager = HotkeyManager(config_manager)
    text_expander = TextExpander(config_manager)
    
    # Initialize UI
    print("Initializing UI...")
    main_window = MainWindow(config_manager)
    print("UI initialized")
    tray_icon = TrayIcon(main_window)
    tray_icon.show()

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

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
