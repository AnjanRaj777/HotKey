import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            return {"hotkeys": []}
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"hotkeys": []}

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get_hotkeys(self):
        return self.config.get("hotkeys", [])

    def add_hotkey(self, trigger_key, action_type, action_target, suppress=False):
        """
        trigger_key: str, e.g., 'ctrl+alt+t'
        action_type: str, e.g., 'run', 'focus'
        action_target: str, e.g., 'notepad.exe', 'Spotify'
        suppress: bool, whether to block the original key event
        """
        new_hotkey = {
            "trigger": trigger_key,
            "type": action_type,
            "target": action_target,
            "active": True,
            "suppress": suppress
        }
        self.config.setdefault("hotkeys", []).append(new_hotkey)
        self.save_config()

    def remove_hotkey(self, index):
        if 0 <= index < len(self.config["hotkeys"]):
            self.config["hotkeys"].pop(index)
            self.save_config()

    def update_hotkey_status(self, index, active):
        if 0 <= index < len(self.config["hotkeys"]):
            self.config["hotkeys"][index]["active"] = active
            self.save_config()

    # --- Snippets (Text Expansion) ---

    def get_snippets(self):
        return self.config.get("snippets", [])

    def add_snippet(self, trigger, replacement):
        snippet = {
            "trigger": trigger,
            "replacement": replacement,
            "active": True
        }
        self.config.setdefault("snippets", []).append(snippet)
        self.save_config()

    def remove_snippet(self, index):
        if 0 <= index < len(self.config["snippets"]):
            self.config["snippets"].pop(index)
            self.save_config()

    def update_snippet_status(self, index, active):
        if 0 <= index < len(self.config["snippets"]):
            self.config["snippets"][index]["active"] = active
            self.save_config()
