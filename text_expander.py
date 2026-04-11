import keyboard
import time
import threading
from utils import set_clipboard

class TextExpander:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_word = ""
        self.is_running = False
        self.snippets = {} # trigger -> replacement
        self.last_expansion = None

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
            # Check for undo first
            if self.last_expansion:
                # The FIRST backspace press after expansion triggers the undo.
                # However, this backspace event is NOT suppressed by on_press.
                # So the system will delete the last char of the replacement.
                # We need to take that into account.
                
                # Wait a tiny bit to let the system process the physical backspace
                # (which removes 1 char)
                # But since we are in the callback, we are parallel.
                # It's safer to let it happen, then fix up.
                self._perform_undo()
                return 

            # Remove last char from buffer
            if len(self.current_word) > 0:
                self.current_word = self.current_word[:-1]
                # print(f"DEBUG: Backspace. Buffer: '{self.current_word}'", flush=True)
        
        else:
            # Any other key clears the undo window
            # EXCEPT maybe navigation keys? But safer to clear.
            if self.last_expansion:
                 self.last_expansion = None

            # Delimiters: Space, Enter, Tab, and Punctuation
            if name in ("space", "enter", "tab", ".", ",", "!", "?", ";", ":"):
                # Check for match (case-insensitive)
                # print(f"DEBUG: Delimiter '{name}'. Checking match for '{self.current_word}'", flush=True)
                candidate = self.current_word.lower()
                if candidate in self.snippets:
                    # print(f"DEBUG: Match found! Swapping '{self.current_word}' -> '{self.snippets[candidate]}'", flush=True)
                    delimiter_char = name
                    if name == "space": delimiter_char = " "
                    elif name == "enter": delimiter_char = "\n"
                    elif name == "tab": delimiter_char = "\t"
                    
                    self._perform_swap(self.current_word, self.snippets[candidate], delimiter_char)
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


    def _perform_swap(self, trigger, replacement, delimiter):
        def worker():
            # Calculate backspaces needed: len(trigger) + 1 (for the delimiter)
            backspaces = len(trigger) + 1
            
            # Use simple backspace chars instead of individual send commands for speed/reliability
            print(f"DEBUG: Swapping. Sending {backspaces} backspaces, then '{replacement}'", flush=True)
            
            # Sending backspaces to remove the trigger and the delimiter
            # Note: We need to ensure the system has processed the 'space' before we backspace it
            time.sleep(0.05) 
            
            keyboard.write('\b' * backspaces)
            time.sleep(0.05) # Small buffer between delete and write
            
            # Use Clipboard Paste for reliability
            if set_clipboard(replacement):
                keyboard.send('ctrl+v')
            else:
                # Fallback to write if clipboard fails
                keyboard.write(replacement, delay=0.01)
                
            # Record this expansion for potential undo
            self.last_expansion = {
                'trigger': trigger,
                'replacement': replacement,
                'delimiter': delimiter,
                'time': time.time()
            }
        threading.Thread(target=worker, daemon=True).start()

    def _perform_undo(self):
        def worker():
            print("DEBUG: Undoing expansion...")
            try:
                data = self.last_expansion
                self.last_expansion = None # prevent recursion or double undo
                
                # We assume the user just pressed Backspace, removing 1 char of replacement.
                # So we need to remove len(replacement) - 1 chars.
                remaining_len = len(data['replacement']) - 1
                
                print(f"DEBUG: Undo - Deleting {remaining_len} chars")
                
                # Use a loop for reliability
                if remaining_len > 0:
                    for _ in range(remaining_len):
                        keyboard.send('backspace')
                        time.sleep(0.01) # 10ms delay per char to prevent buffer overflow/skips
                
                # Restore Trigger + Delimiter
                # Wait a tiny bit for deletions to register
                time.sleep(0.05)
                
                # Write back the original trigger and delimiter
                to_restore = data['trigger'] + data['delimiter']
                keyboard.write(to_restore)
                print(f"DEBUG: Undo - Restored '{to_restore}'")
                
            except Exception as e:
                print(f"ERROR in _perform_undo: {e}")
                import traceback
                traceback.print_exc()
        threading.Thread(target=worker, daemon=True).start()

