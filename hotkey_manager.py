import keyboard
import time
from utils import focus_window, run_command, open_url

class HotkeyManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.is_running = False

    def start_listener(self):
        if self.is_running:
            return
        self.reload_hotkeys()
        self.is_running = True
        print("Hotkey Listener Started")

    def stop_listener(self):
        if not self.is_running:
            return
        keyboard.unhook_all()
        self.is_running = False
        print("Hotkey Listener Stopped")

    def reload_hotkeys(self):
        keyboard.unhook_all()
        hotkeys = self.config_manager.get_hotkeys()
        for hk in hotkeys:
            if hk.get("active", True):
                self._register_hotkey(hk)

    def _register_hotkey(self, hk):
        trigger = hk["trigger"]
        action_type = hk["type"]
        target = hk["target"]
        
        # Define the callback closure
        def callback():
            print(f"Triggered: {trigger} -> {action_type}: {target}")
            if action_type in ("run", "File", "Folder"):
                run_command(target)
            elif action_type == "focus":
                focus_window(target)
            elif action_type == "open_url":
                open_url(target)

        try:
            # Check if suppression is requested, default to False (pass-through)
            should_suppress = hk.get("suppress", False)
            keyboard.add_hotkey(trigger, callback, suppress=should_suppress)
        except Exception as e:
            print(f"Failed to register hotkey '{trigger}': {e}")
