import keyboard
import time
from utils import set_clipboard

class TextExpander:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_word = ""
        self.is_running = False
        self.snippets = {} # trigger -> replacement

    def start_listener(self):
        if self.is_running:
            return
        self.reload_snippets()
        keyboard.on_press(self._on_key_press)
        self.is_running = True
        print("Text Expander Listener Started")

    def stop_listener(self):
        if not self.is_running:
            return
        # Note: keyboard.unhook_all() removes ALL hooks, including hotkeys.
        # This might be tricky if we want to run both managers.
        # However, hotkey_manager calls unhook_all() too.
        # Ideally, we should manage hooks more carefully or just rely on main.py 
        # to stop/start everything together.
        # For now, we'll assume stop_listener is called when the whole system stops.
        
        # To remove ONLY our hook, we'd need to store the return value of on_press.
        # But `keyboard` doesn't make unhooking specific callbacks super easy without unhook_all usually.
        # Let's rely on the global unhook_all strategy used in main.py for now.
        pass

    def reload_snippets(self):
        raw_snippets = self.config_manager.get_snippets()
        # Store lowercased triggers for case-insensitive matching
        self.snippets = {s["trigger"].lower(): s["replacement"] for s in raw_snippets if s.get("active", True)}

    def _on_key_press(self, event):
        if not self.is_running:
            return

        name = event.name
        
        # Ignore modifiers being pressed alone
        if name in ("ctrl", "alt", "shift", "windows", "caps lock", "shift", "right shift"):
            return

        if name == "backspace":
            # Remove last char
            if len(self.current_word) > 0:
                self.current_word = self.current_word[:-1]
                # print(f"DEBUG: Backspace. Buffer: '{self.current_word}'", flush=True)
        
        # Delimiters: Space, Enter, Tab, and Punctuation
        elif name in ("space", "enter", "tab", ".", ",", "!", "?", ";", ":"):
            # Check for match (case-insensitive)
            # print(f"DEBUG: Delimiter '{name}'. Checking match for '{self.current_word}'", flush=True)
            candidate = self.current_word.lower()
            if candidate in self.snippets:
                # print(f"DEBUG: Match found! Swapping '{self.current_word}' -> '{self.snippets[candidate]}'", flush=True)
                self._perform_swap(self.current_word, self.snippets[candidate])
                self.current_word = "" # Reset after swap
            else:
                self.current_word = "" # Reset on delimiter if no match
        elif len(name) == 1:
            # Regular character
            self.current_word += name
            # print(f"DEBUG: Appended '{name}'. Buffer: '{self.current_word}'", flush=True)
        else:
            # Other navigation keys resets buffer
            # print(f"DEBUG: Resetting buffer due to key '{name}'", flush=True)
            self.current_word = ""


    def _perform_swap(self, trigger, replacement):
        # Calculate backspaces needed: len(trigger) + 1 (for the delimiter)
        backspaces = len(trigger) + 1
        
        # Use simple backspace chars instead of individual send commands for speed/reliability
        print(f"DEBUG: Swapping. Sending {backspaces} backspaces, then '{replacement}'", flush=True)
        
        # Sending backspaces to remove the trigger and the delimiter
        # Note: We need to ensure the system has processed the 'space' before we backspace it?
        # If we act too fast, we might backspace the trigger, then the 'space' appears?
        # Let's keep a small delay.
        time.sleep(0.05) 
        
        keyboard.write('\b' * backspaces)
        time.sleep(0.05) # Small buffer between delete and write
        
        # Use Clipboard Paste for reliability
        if set_clipboard(replacement):
            keyboard.send('ctrl+v')
        else:
            # Fallback to write if clipboard fails
            keyboard.write(replacement, delay=0.01)
