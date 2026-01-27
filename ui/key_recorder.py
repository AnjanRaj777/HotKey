from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QKeySequence

class KeyRecorder(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Click here and press keys...")
        self.setReadOnly(True) # Prevent manual typing
        self.held_keys = set()
        
        # Map certain keys to names compatible with 'keyboard' library
        self.key_map = {
            Qt.Key.Key_Control: "ctrl",
            Qt.Key.Key_Shift: "shift",
            Qt.Key.Key_Alt: "alt",
            Qt.Key.Key_Meta: "windows",
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_Return: "enter",
            Qt.Key.Key_Backspace: "backspace",
            Qt.Key.Key_Tab: "tab",
            Qt.Key.Key_Escape: "esc",
            Qt.Key.Key_Delete: "delete",
            Qt.Key.Key_Insert: "insert",
            Qt.Key.Key_Home: "home",
            Qt.Key.Key_End: "end",
            Qt.Key.Key_PageUp: "pageup",
            Qt.Key.Key_PageDown: "pagedown",
            Qt.Key.Key_Left: "left",
            Qt.Key.Key_Right: "right",
            Qt.Key.Key_Up: "up",
            Qt.Key.Key_Down: "down"
        }

    def keyPressEvent(self, event: QKeyEvent):
        # We don't want autorepeat to trigger multiple updates or confusing logic
        if event.isAutoRepeat():
            return
            
        key = event.key()
        
        # Handle "Unknown" key (0)
        if key == 0 or key == Qt.Key.Key_unknown:
            return

        # Get string representation
        if key in self.key_map:
            key_name = self.key_map[key]
        else:
            # Fallback for letters/numbers
            key_name = QKeySequence(key).toString().lower()

        if key_name:
            self.held_keys.add(key_name)
            self.update_display()
            
    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        key = event.key()
        if key in self.key_map:
            key_name = self.key_map[key]
        else:
            key_name = QKeySequence(key).toString().lower()

        if key_name in self.held_keys:
            self.held_keys.remove(key_name)
            
        # NOTE: We do NOT update display on release.
        # This allows the user to release keys and the last full combo remains.
        # The next Press will add to the set (if not empty) or start new (conceptually, 
        # but actually if they release everything, set is empty).
        
        # Issue: If they release everything, held_keys is empty.
        # Use case: User presses A, holds A, presses B -> "a+b".
        # Releases B -> held_keys has A. Display still "a+b".
        # Releases A -> held_keys empty. Display still "a+b".
        # Presses C -> held_keys has C. Display updates to "c".
        pass

    def update_display(self):
        # Sort keys reliably: modifiers first, then others alphabetically
        order = ["ctrl", "alt", "shift", "windows"]
        
        current = list(self.held_keys)
        
        # Split into mods and others
        presence_mods = [k for k in current if k in order]
        others = [k for k in current if k not in order]
        
        # Sort presence_mods by index in 'order'
        presence_mods.sort(key=lambda x: order.index(x))
        others.sort()
        
        final_parts = presence_mods + others
        if final_parts:
            self.setText("+".join(final_parts))

    def focusOutEvent(self, event):
        # Reset held keys when losing focus to prevent getting stuck
        self.held_keys.clear()
        super().focusOutEvent(event)
