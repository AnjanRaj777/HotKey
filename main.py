import sys
import ctypes
from app_controller import AppController

def main():
    # Fix Taskbar Icon on Windows
    # Windows groups all python processes under the python icon unless we set a unique AppUserModelID
    try:
        myappid = 'anjanraj.hotkey.manager.1.0' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"Failed to set AppUserModelID: {e}")

    # CLI Arguments handling (simple version, can be moved to controller if complex)
    if len(sys.argv) > 2 and sys.argv[1] == "--add-hotkey":
        from config_manager import ConfigManager
        config_manager = ConfigManager()
        file_path = sys.argv[2]
        print(f"Adding hotkey for: {file_path}")
        # Add to config with a placeholder trigger
        config_manager.add_hotkey(trigger_key="<Assign Key>", 
                                  action_type="run", 
                                  action_target=file_path, 
                                  suppress=False)
        print("Hotkey added successfully.")
        sys.exit(0)

    # Initialize Controller
    controller = AppController()
    controller.setup_app(sys.argv)
    controller.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to continue...")  # Keep window open if run from double-click

