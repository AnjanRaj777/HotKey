import json
import os
import time

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

    def export_to_file(self, file_path):
        try:
            with open(file_path, "w") as f:
                json.dump(self.config, f, indent=4)
            return True, "Success"
        except IOError as e:
            return False, f"Error exporting: {e}"

    def import_from_file(self, file_path):
        if not os.path.exists(file_path):
            return False, "File not found"
        try:
            with open(file_path, "r") as f:
                new_config = json.load(f)
                
            # Basic Validation: Ensure it's a dict
            if not isinstance(new_config, dict):
                return False, "Invalid config format"

            self.config = new_config
            self.save_config() # Persist to main config.json
            return True, "Success"
        except (json.JSONDecodeError, IOError) as e:
            return False, f"Error importing: {e}"

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
            "suppress": suppress,
            "created_at": time.time()
        }
        self.config.setdefault("hotkeys", []).append(new_hotkey)
        self.save_config()

    def update_hotkey(self, index, data):
        if 0 <= index < len(self.config["hotkeys"]):
            # Preserve created_at if not provided in data
            original = self.config["hotkeys"][index]
            if "created_at" not in data:
                data["created_at"] = original.get("created_at", time.time())
            
            # Ensure active status is preserved if not explicitly changed (though usually edits might reset or keep it, let's assume active state is managed separately or passed in data)
            # Actually, let's trust 'data' has mostly what we need, but maybe 'active' should be preserved if missing.
            if "active" not in data:
                data["active"] = original.get("active", True)

            self.config["hotkeys"][index] = data
            self.save_config()
            return True
        return False

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
            "active": True,
            "created_at": time.time()
        }
        self.config.setdefault("snippets", []).append(snippet)
        self.save_config()

    def update_snippet(self, index, trigger, replacement):
        if 0 <= index < len(self.config["snippets"]):
            snippet = self.config["snippets"][index]
            snippet["trigger"] = trigger
            snippet["replacement"] = replacement
            # Active and created_at remain unchanged
            self.save_config()
            return True
        return False

    def remove_snippet(self, index):
        if 0 <= index < len(self.config["snippets"]):
            self.config["snippets"].pop(index)
            self.save_config()

    def update_snippet_status(self, index, active):
        if 0 <= index < len(self.config["snippets"]):
            self.config["snippets"][index]["active"] = active
            self.save_config()

    # --- Appearance Settings ---

    def get_theme(self):
        return self.config.get("theme", "Dark") # Default to Dark

    def set_theme(self, theme):
        self.config["theme"] = theme
        self.save_config()

    def get_opacity(self):
        return self.config.get("opacity", 1.0) # Default 100%

    def set_opacity(self, opacity):
        # opacity is a float between 0.1 and 1.0
        self.config["opacity"] = max(0.1, min(1.0, float(opacity)))
        self.save_config()

    def get_always_on_top(self):
        return self.config.get("appearance", {}).get("always_on_top", False)

    def set_always_on_top(self, enabled):
        self.config.setdefault("appearance", {})["always_on_top"] = enabled
        self.save_config()



    def get_accent_color(self):
        return self.config.get("appearance", {}).get("accent_color", "#007acc")

    def set_accent_color(self, color):
        self.config.setdefault("appearance", {})["accent_color"] = color
        self.save_config()

    def get_corner_radius(self):
        return self.config.get("appearance", {}).get("corner_radius", 5)

    def set_corner_radius(self, radius):
        self.config.setdefault("appearance", {})["corner_radius"] = radius
        self.save_config()

    def get_hide_labels(self):
        return self.config.get("appearance", {}).get("hide_labels", False)

    def set_hide_labels(self, hidden):
        self.config.setdefault("appearance", {})["hide_labels"] = hidden
        self.save_config()
