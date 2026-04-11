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

    def reload_config(self):
        self.config = self.load_config()

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

    def add_hotkey(self, trigger_key, action_type, action_target, suppress=False, long_press=False, name=""):
        """
        trigger_key: str, e.g., 'ctrl+alt+t'
        action_type: str, e.g., 'run', 'focus'
        action_target: str, e.g., 'notepad.exe', 'Spotify'
        action_target: str, e.g., 'notepad.exe', 'Spotify'
        suppress: bool, whether to block the original key event
        long_press: bool, whether to use long press trigger
        """
        print(f"DEBUG: add_hotkey called with long_press={long_press}")
        new_hotkey = {
            "trigger": trigger_key,
            "type": action_type,
            "target": action_target,
            "name": name,
            "active": True,
            "suppress": suppress,
            "long_press": long_press,
            "created_at": time.time()
        }
        self.config.setdefault("hotkeys", []).append(new_hotkey)
        self.save_config()

    def update_hotkey(self, index, data):
        print(f"DEBUG: update_hotkey called for index {index} with data: {data}")
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
        return self.config.get("opacity", 0.97) # Default 97%

    def set_opacity(self, opacity):
        # opacity is a float between 0.1 and 1.0
        self.config["opacity"] = max(0.1, min(1.0, float(opacity)))
        self.save_config()

    def get_always_on_top(self):
        return self.config.get("appearance", {}).get("always_on_top", False)

    def set_always_on_top(self, enabled):
        self.config.setdefault("appearance", {})["always_on_top"] = enabled
        self.save_config()

    def get_solid_mode(self):
        return self.config.get("appearance", {}).get("solid_mode", False)

    def set_solid_mode(self, enabled):
        self.config.setdefault("appearance", {})["solid_mode"] = enabled
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

    def get_context_menu_enabled(self):
        return self.config.get("general", {}).get("context_menu_enabled", False)

    def set_context_menu_enabled(self, enabled):
        self.config.setdefault("general", {})["context_menu_enabled"] = enabled
        self.config.setdefault("general", {})["context_menu_enabled"] = enabled
        self.save_config()

    def get_long_press_delay(self):
        return self.config.get("general", {}).get("long_press_delay", 500) # Default 500ms

    def set_long_press_delay(self, delay_ms):
        self.config.setdefault("general", {})["long_press_delay"] = delay_ms
        self.save_config()

    # --- Workspaces ---

    def get_workspaces(self):
        return self.config.get("workspaces", [])

    def add_workspace(self, workspace):
        self.config.setdefault("workspaces", []).append(workspace)
        self.save_config()

    def remove_workspace(self, workspace_id):
        workspaces = self.get_workspaces()
        self.config["workspaces"] = [w for w in workspaces if w["id"] != workspace_id]
        self.save_config()

    def get_workspace_by_id(self, workspace_id):
        for w in self.get_workspaces():
            if w["id"] == workspace_id:
                return w
        return None

