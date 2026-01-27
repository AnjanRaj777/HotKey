import keyboard
import time

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
        self.snippets = {s["trigger"]: s["replacement"] for s in raw_snippets if s.get("active", True)}

    def _on_key_press(self, event):
        if not self.is_running:
            return

        name = event.name
        # print(f"DEBUG: Key pressed: '{name}' | Current Buffer: '{self.current_word}'", flush=True)
        
        # Ignore modifiers being pressed alone
        if name in ("ctrl", "alt", "shift", "windows", "caps lock", "tab", "shift"):
            return

        if name == "backspace":
            # Remove last char
            if len(self.current_word) > 0:
                self.current_word = self.current_word[:-1]
                print(f"DEBUG: Backspace. Buffer: '{self.current_word}'", flush=True)
        elif name == "space" or name == "enter":
            print(f"DEBUG: Delimiter '{name}'. Checking match for '{self.current_word}' in {list(self.snippets.keys())}", flush=True)
            # Check for match
            if self.current_word in self.snippets:
                print(f"DEBUG: Match found! Swapping '{self.current_word}' -> '{self.snippets[self.current_word]}'", flush=True)
                self._perform_swap(self.current_word, self.snippets[self.current_word])
                self.current_word = "" # Reset after swap
            else:
                self.current_word = "" # Reset on delimiter if no match
        elif len(name) == 1:
            # Regular character
            self.current_word += name
            print(f"DEBUG: Appended '{name}'. Buffer: '{self.current_word}'", flush=True)
        else:
            # Other navigation keys resets buffer
            print(f"DEBUG: Resetting buffer due to key '{name}'", flush=True)
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
        time.sleep(0.1) 
        
        keyboard.write('\b' * backspaces)
        keyboard.write(replacement)
