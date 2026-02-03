import keyboard
import time
from utils import focus_window, run_command, open_url

class HotkeyManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.is_running = False
        self.current_workspace_id = None # None means "Global" context
        self.workspace_switcher_callback = None
        self.registered_hotkeys = []
        self.ai_voice_callback = None

    def set_workspace_switcher(self, callback):
        self.workspace_switcher_callback = callback

    def set_ai_voice_callback(self, callback):
        self.ai_voice_callback = callback

    def set_current_workspace(self, workspace_id):
        print(f"HotkeyManager: Switching to workspace {workspace_id}")
        self.current_workspace_id = workspace_id
        if self.is_running:
            self.reload_hotkeys()

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
        # Clear existing hotkeys managed by this manager
        for hk in self.registered_hotkeys:
            try:
                keyboard.remove_hotkey(hk)
            except Exception:
                pass
        self.registered_hotkeys.clear()
        
        hotkeys = self.config_manager.get_hotkeys()
        for hk in hotkeys:
            if not hk.get("active", True):
                continue
            
            # Workspace Filtering
            # If 'workspaces' key is missing or empty -> Global (active everywhere)
            # If present, must contain current_workspace_id (or 'global')
            allowed_workspaces = hk.get("workspaces", [])
            if allowed_workspaces:
                # If specific workspaces are defined, we check if current ID is in there
                # We also allow 'global' entry in the list to mean "always active"
                if self.current_workspace_id not in allowed_workspaces and "global" not in allowed_workspaces:
                    continue 

            self._register_hotkey(hk)

        # Register Workspace Launch Hotkeys
        workspaces = self.config_manager.get_workspaces()
        for w in workspaces:
            trigger = w.get("launch_hotkey")
            if trigger and self.workspace_switcher_callback:
                print(f"Registering workspace hotkey: {trigger} -> {w['name']}")
                try:
                    # Use default args to capture variable in lambda
                    hk_ref = keyboard.add_hotkey(trigger, lambda wid=w['id']: self.workspace_switcher_callback(wid))
                    self.registered_hotkeys.append(hk_ref)
                except Exception as e:
                    print(f"Failed to register workspace hotkey '{trigger}': {e}")

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
            elif action_type == "Ai Voice Mode":
                if self.ai_voice_callback:
                    # Execute on main thread if possible? 
                    # Note: callback calls from 'keyboard' are in a separate thread.
                    # We rely on the callback implementation (instantiating Qt widgets) to handle thread safety via signals if needed.
                    # Or we just call it and hope PyObject wrapper handles it (often signals are better).
                    # Ideally, self.ai_voice_callback should emit a signal.
                    self.ai_voice_callback(target)

        try:
            # Check if suppression is requested, default to False (pass-through)
            should_suppress = hk.get("suppress", False)
            hk_ref = keyboard.add_hotkey(trigger, callback, suppress=should_suppress)
            self.registered_hotkeys.append(hk_ref)
        except Exception as e:
            print(f"Failed to register hotkey '{trigger}': {e}")
