
import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from config_manager import ConfigManager

# Mock ConfigManager to avoid overwriting real config
class MockConfigManager(ConfigManager):
    def __init__(self):
        self.config = {
            "hotkeys": [
                {"trigger": "ctrl+1", "type": "run", "target": "notepad", "active": True},
                {"trigger": "ctrl+2", "type": "focus", "target": "chrome", "active": True}
            ]
        }
    def save_config(self):
        pass # Do nothing

def test_removal():
    app = QApplication(sys.argv)
    cm = MockConfigManager()
    mw = MainWindow(cm)
    
    # Verify initial state
    assert mw.table.rowCount() == 2
    print("Initial Row Count: 2")

    # Select Row 0
    mw.table.selectRow(0)
    print(f"Selected Row: {mw.table.currentRow()}")
    
    # Connect signal to verify emission
    removed_indices = []
    mw.remove_hotkey_signal.connect(lambda idx: removed_indices.append(idx))
    
    # Simulate clicking remove
    mw.remove_selected_hotkey()
    
    if len(removed_indices) == 1 and removed_indices[0] == 0:
        print("Signal emitted correctly for Row 0.")
    else:
        print(f"Signal failed. Indices: {removed_indices}")

    # Now verify if we actually simulate the full loop
    # In real app: signal -> main.py buffer -> config.remove -> mw.refresh
    
    # Manually do what main.py does
    if removed_indices:
        idx = removed_indices[0]
        cm.remove_hotkey(idx)
        mw.refresh_table()
    
    print(f"Row Count after remove: {mw.table.rowCount()}")
    assert mw.table.rowCount() == 1
    assert mw.table.item(0, 1).text() == "ctrl+2"
    print("Test passed successfully.")

if __name__ == "__main__":
    test_removal()
