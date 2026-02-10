import sys
import json
from PyQt6.QtWidgets import QApplication
from ui.text_expansion_tab import TextExpansionTab
from config_manager import ConfigManager

try:
    app = QApplication(sys.argv)
    cm = ConfigManager("config.json")
    
    # Reload to ensure we have latest
    cm.reload_config()
    print("Config loaded.")
    print(f"Snippets: {cm.get_snippets()}")

    tab = TextExpansionTab(cm)
    print("Tab initialized.")
    
    # Simulate sorting which happens on tab switch
    print("Sorting by Trigger (A-Z)...")
    tab.sort_snippets(0)
    print("Sorted 0.")
    
    print("Sorting by Trigger (Z-A)...")
    tab.sort_snippets(1)
    print("Sorted 1.")
    
    print("Sorting by Date...")
    tab.sort_snippets(2)
    print("Sorted 2.")
    
    print("Sorting by Active...")
    tab.sort_snippets(3)
    print("Sorted 3.")
    
    print("All tests pass.")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
