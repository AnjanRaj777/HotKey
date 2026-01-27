import sys
import os
import win32com.client

class StartupManager:
    def __init__(self, app_name="Hotkey"):
        self.app_name = app_name
        self.startup_dir = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
        self.shortcut_path = os.path.join(self.startup_dir, f"{self.app_name}.lnk")
        self.icon_path = os.path.abspath(r"assets/logo.ico")

    def is_startup_enabled(self):
        return os.path.exists(self.shortcut_path)

    def set_startup(self, enable: bool):
        if enable:
            return self._create_shortcut()
        else:
            return self._remove_shortcut()

    def _create_shortcut(self):
        try:
            # Determine python executable (pythonw.exe to hide console)
            python_exe = sys.executable
            dirname = os.path.dirname(python_exe)
            pythonw = os.path.join(dirname, "pythonw.exe")
            target_exe = pythonw if os.path.exists(pythonw) else python_exe
            
            script_path = os.path.abspath("main.py")
            working_dir = os.path.dirname(script_path)
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(self.shortcut_path)
            shortcut.TargetPath = target_exe
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = working_dir
            shortcut.IconLocation = self.icon_path
            shortcut.save()
            return True
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False

    def _remove_shortcut(self):
        try:
            if os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)
            
            # Also clean up old registry key if likely to exist from previous version
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "GlobalHotkeyManager")
                winreg.CloseKey(key)
            except:
                pass
                
            return True
        except Exception as e:
            print(f"Error removing shortcut: {e}")
            return False
