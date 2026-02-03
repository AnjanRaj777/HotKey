import sys
import os
import winreg
import ctypes

class ContextMenuManager:
    def __init__(self, app_name="HotKey", command_args="--add-hotkey \"%1\""):
        self.app_name = app_name
        self.command_args = command_args
        self.key_path = f"Software\\Classes\\*\\shell\\AddTo{self.app_name}"

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def get_executable_path(self):
        if getattr(sys, 'frozen', False):
            # If the application is frozen (compiled), use the executable path
            return sys.executable
        else:
            # If running from source, use the python interpreter and the script path
            # We assume main.py is in the same directory as this script if we're importing it,
            # but let's be safe and use abspath.
            # However, for the context menu command, we need: "path/to/python.exe" "path/to/main.py"
            # The Registry command string format: "C:\Path\To\Python.exe" "C:\Path\To\main.py" --add-hotkey "%1"
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'main.py'))
            return f'"{sys.executable}" "{script_path}"'

    def add_context_menu(self):
        # We'll use HKEY_CURRENT_USER so we typically don't need admin rights for this specific key
        # HKCU\Software\Classes\*\shell\AddToHotKey
        
        exe_cmd = self.get_executable_path()
        command = f'{exe_cmd} {self.command_args}'
        
        menu_name = f"Add to {self.app_name}"
        
        try:
            # Create the main key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.key_path)
            winreg.SetValue(key, "", winreg.REG_SZ, menu_name)
            
            # Set Icon (Optional, uses the executable icon)
            # If running from source, sys.executable is python.exe which has a generic icon.
            # If we had an .ico file, we could point to it.
            # For now, let's try to use the executable itself if frozen, or just skip if source.
            if getattr(sys, 'frozen', False):
                 winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, sys.executable)
            
            # Create the 'command' subkey
            command_key = winreg.CreateKey(key, "command")
            winreg.SetValue(command_key, "", winreg.REG_SZ, command)
            
            winreg.CloseKey(command_key)
            winreg.CloseKey(key)
            return True, "Context menu added successfully."
        except Exception as e:
            return False, f"Error adding context menu: {e}"

    def remove_context_menu(self):
        try:
            # Delete the 'command' subkey first
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{self.key_path}\\command")
            # Delete the main key
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self.key_path)
            return True, "Context menu removed successfully."
        except FileNotFoundError:
            return True, "Context menu was not present."
        except Exception as e:
            return False, f"Error removing context menu: {e}"

    def is_context_menu_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_READ)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

if __name__ == "__main__":
    # Simple CLI for testing
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", action="store_true", help="Add to context menu")
    parser.add_argument("--remove", action="store_true", help="Remove from context menu")
    args = parser.parse_args()
    
    manager = ContextMenuManager()
    
    if args.add:
        success, msg = manager.add_context_menu()
        print(msg)
    elif args.remove:
        success, msg = manager.remove_context_menu()
        print(msg)
    else:
        print(f"Current status: {'Enabled' if manager.is_context_menu_enabled() else 'Disabled'}")
