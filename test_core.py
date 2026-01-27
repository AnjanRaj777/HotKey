import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Testing Imports...")
    from config_manager import ConfigManager
    from utils import focus_window
    from hotkey_manager import HotkeyManager
    print("Imports Successful.")

    print("Testing ConfigManager...")
    cm = ConfigManager("test_config.json")
    cm.add_hotkey("ctrl+t", "run", "notepad")
    hotkeys = cm.get_hotkeys()
    assert len(hotkeys) == 1
    assert hotkeys[0]["trigger"] == "ctrl+t"
    print("ConfigManager Test Passed.")
    
    # Cleanup
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")

    print("All checks passed.")
except Exception as e:
    print(f"Test Failed: {e}")
    sys.exit(1)
