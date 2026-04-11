import sys
import os

# Ensure root dir is in path
sys.path.append(os.getcwd())

from ui.text_expansion_tab import TextExpansionTab
from config_manager import ConfigManager
from PyQt6.QtWidgets import QApplication

def check_structure():
    print("Checking TextExpansionTab structure...")
    try:
        app = QApplication(sys.argv)
        cm = ConfigManager()
        tab = TextExpansionTab(cm)
        
        if hasattr(tab, 'sort_snippets'):
            print("SUCCESS: sort_snippets method exists.")
        else:
            print("FAILURE: sort_snippets method MISSING.")
            
        # Try calling it to see if it crashes internally
        print("Attempting to call sort_snippets(0)...")
        tab.sort_snippets(0)
        print("SUCCESS: sort_snippets(0) executed without crash.")
        
    except Exception as e:
        print(f"CRASHED during check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_structure()
