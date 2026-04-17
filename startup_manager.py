import sys
import os
import winreg

class StartupManager:
    def __init__(self, app_name="Hotkey"):
        self.app_name = app_name
        self.registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def is_startup_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def set_startup(self, enable: bool):
        if enable:
            return self._create_registry_key()
        else:
            return self._remove_registry_key()

    def _create_registry_key(self):
        try:
            python_exe = sys.executable
            dirname = os.path.dirname(python_exe)
            pythonw = os.path.join(dirname, "pythonw.exe")
            target_exe = pythonw if os.path.exists(pythonw) else python_exe
            
            script_path = os.path.abspath("main.py")
            command = f'"{target_exe}" "{script_path}"'
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            
            self._cleanup_old_shortcut()
            
            return True
        except Exception as e:
            print(f"Error creating registry key: {e}")
            return False

    def _remove_registry_key(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, self.app_name)
            winreg.CloseKey(key)
            
            self._cleanup_old_shortcut()
            
            return True
        except Exception as e:
            print(f"Error removing registry key: {e}")
            return False

    def _cleanup_old_shortcut(self):
        try:
            startup_dir = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
            shortcut_path = os.path.join(startup_dir, f"{self.app_name}.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            
            # Clean up old "GlobalHotkeyManager" reg key just in case
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, "GlobalHotkeyManager")
            except:
                pass
            winreg.CloseKey(key)
        except Exception:
            pass
