import keyboard
import time
import threading
from utils import focus_window, run_command, open_url

class HotkeyManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.is_running = False
        self.current_workspace_id = None # None means "Global" context
        self.workspace_switcher_callback = None
        self.registered_hotkeys = []
        self.ai_voice_callback = None

    def set_workspace_switcher(self, callback):
        self.workspace_switcher_callback = callback

    def set_ai_voice_callback(self, callback):
        self.ai_voice_callback = callback

    def set_current_workspace(self, workspace_id):
        print(f"HotkeyManager: Switching to workspace {workspace_id}")
        self.current_workspace_id = workspace_id
        if self.is_running:
            self.reload_hotkeys()

    def start_listener(self):
        if self.is_running:
            return
        self.reload_hotkeys()
        self.is_running = True
        print("Hotkey Listener Started")

    def stop_listener(self):
        if not self.is_running:
            return
        keyboard.unhook_all()
        self.is_running = False
        print("Hotkey Listener Stopped")

    def reload_hotkeys(self):
        # Clear existing hotkeys managed by this manager
        for hk in self.registered_hotkeys:
            try:
                keyboard.remove_hotkey(hk)
            except Exception:
                pass
        self.registered_hotkeys.clear()
        
        # Mapping for long press handlers to keep them alive/clean up
        self.long_press_handlers = getattr(self, "long_press_handlers", [])
        for handler in self.long_press_handlers:
            handler.stop()
        self.long_press_handlers = []

        hotkeys = self.config_manager.get_hotkeys()
        for hk in hotkeys:
            if not hk.get("active", True):
                continue
            
            # Workspace Filtering
            # If 'workspaces' key is missing or empty -> Global (active everywhere)
            # If present, must contain current_workspace_id (or 'global')
            allowed_workspaces = hk.get("workspaces", [])
            if allowed_workspaces:
                # If specific workspaces are defined, we check if current ID is in there
                # We also allow 'global' entry in the list to mean "always active"
                if self.current_workspace_id not in allowed_workspaces and "global" not in allowed_workspaces:
                    continue 

            self._register_hotkey(hk)

        # Register Workspace Launch Hotkeys
        workspaces = self.config_manager.get_workspaces()
        for w in workspaces:
            trigger = w.get("launch_hotkey")
            if trigger and self.workspace_switcher_callback:
                print(f"Registering workspace hotkey: {trigger} -> {w['name']}")
                try:
                    # Use default args to capture variable in lambda
                    hk_ref = keyboard.add_hotkey(trigger, lambda wid=w['id']: self.workspace_switcher_callback(wid))
                    self.registered_hotkeys.append(hk_ref)
                except Exception as e:
                    print(f"Failed to register workspace hotkey '{trigger}': {e}")
        
        print(f"DEBUG: Total registered hotkeys: {len(self.registered_hotkeys)}")

    def _register_hotkey(self, hk):
        trigger = hk["trigger"]
        action_type = hk["type"]
        target = hk["target"]
        
        # Define the callback closure
        def callback():
            print(f"DEBUG: Hotkey callback triggered for '{trigger}'")
            print(f"Triggered: {trigger} -> {action_type}: {target}")
            
            try:
                if action_type in ("run", "File", "Folder"):
                    print(f"DEBUG: Executing run_command for {target}")
                    run_command(target)
                elif action_type == "focus":
                    print(f"DEBUG: Focusing window {target}")
                    focus_window(target)
                elif action_type == "open_url":
                    print(f"DEBUG: Opening URL {target}")
                    open_url(target)
                elif action_type == "Ai Voice Mode":
                    print(f"DEBUG: Activating AI Voice Mode for {target}")
                    if self.ai_voice_callback:
                        # Execute callback. Note: This runs on the keyboard hook thread.
                        # The callback (Qt Signal.emit) is thread-safe and will queue the slot 
                        # execution on the main thread if connected with Auto/Queued connection.
                        self.ai_voice_callback(target)
                    else:
                        print("ERROR: AI Voice callback not set!")
            except Exception as e:
                print(f"ERROR in hotkey callback for {trigger}: {e}")
                import traceback
                traceback.print_exc()

        try:
            # Check if suppression is requested, default to False (pass-through)
            should_suppress = hk.get("suppress", False)
            long_press = hk.get("long_press", False)
            
            print(f"DEBUG: Registering '{trigger}' (Action: {action_type}, LongPress: {long_press})")

            if long_press:
                # Use custom LongPressHandler
                delay = self.config_manager.get_long_press_delay() / 1000.0 # ms to s
                handler = LongPressHandler(trigger, callback, delay, should_suppress)
                handler.start()
                self.long_press_handlers.append(handler)
            else:
                hk_ref = keyboard.add_hotkey(trigger, callback, suppress=should_suppress)
                self.registered_hotkeys.append(hk_ref)
        except Exception as e:
            print(f"Failed to register hotkey '{trigger}': {e}")


class LongPressHandler:
    def __init__(self, trigger, callback, delay, suppress=True):
        self.trigger = trigger
        self.callback = callback
        self.delay = delay
        self.suppress = suppress
        self.timer = None
        self.is_execution_triggered = False
        self.active = False
        self.hotkey_ref = None
        self.poll_interval = 0.05 # Check every 50ms
        print(f"DEBUG: LongPressHandler init for '{trigger}' with delay {delay}s")

    def start(self):
        try:
            # For long presses, especially multi-key combos, add_hotkey with trigger_on_release=False
            # can be flaky or raise exceptions depending on the library version
            # Let's use it but catch specific errors, or just fall back to standard press detection
            self.hotkey_ref = keyboard.add_hotkey(
                self.trigger, 
                self.on_activate, 
                suppress=self.suppress, 
                trigger_on_release=False
            )
            self.active = True
        except ValueError as ve:
            print(f"ValueError starting LongPressHandler for {self.trigger} - likely a combination issue: {ve}")
            # Fallback for complex triggers that add_hotkey rejects
            # E.g., ctrl+j+k might not parse well for add_hotkey but hook catches it.
            # In a real app we might need a custom hook parser, but here we can try a simpler bind
            try:
                self.hotkey_ref = keyboard.on_press_key(
                    self.trigger.split("+")[-1], # hook to the last key
                    self.on_activate_fallback,
                    suppress=self.suppress
                )
                self.active = True
            except Exception as e2:
                print(f"Fallback also failed for {self.trigger}: {e2}")
        except Exception as e:
            print(f"Error starting LongPressHandler for {self.trigger}: {e}")

    def on_activate_fallback(self, event):
        # We only hooked the last key. Check if others are pressed.
        parts = self.trigger.lower().split('+')
        modifiers = parts[:-1]
        for mod in modifiers:
            if not keyboard.is_pressed(mod):
                return # Not all keys pressed
        self.on_activate()

    def stop(self):
        self.active = False
        if self.timer:
            self.timer.cancel()
        if self.hotkey_ref:
            try:
                keyboard.remove_hotkey(self.hotkey_ref)
            except:
                pass
        self.hotkey_ref = None

    def on_activate(self):
        if not self.active: return
        
        # Avoid re-entry if already processing a press
        if self.timer and self.timer.is_alive():
            return

        self.is_execution_triggered = False
        
        # Start polling for release
        self.start_time = time.time()
        self.check_release_loop()

    def check_release_loop(self):
        if not self.active: return
        
        # Check if keys are still pressed
        is_pressed = keyboard.is_pressed(self.trigger)
        elapsed = time.time() - self.start_time
        # print(f"DEBUG: Checking {self.trigger}: pressed={is_pressed}, elapsed={elapsed:.2f}s")
        
        if is_pressed:
            if elapsed >= self.delay:
                # Long Press Condition Met
                print(f"DEBUG: Long Press Met! {elapsed:.2f}s >= {self.delay}s")
                if not self.is_execution_triggered:
                    self.execute()
                # We stop polling but don't replay.
                # User is still holding keys, they might release later.
                # We can wait for release to reset? 
                # Or just exit loop and let next press trigger?
                # If we exit, and user holds for 10s, next "activate" trigger won't fire until release and re-press.
                # So we just return.
                return
            else:
                # Still holding, but not enough time. Schedule next check.
                self.timer = threading.Timer(self.poll_interval, self.check_release_loop)
                self.timer.start()
        else:
            # Released!
            elapsed = time.time() - self.start_time
            if elapsed < self.delay and not self.is_execution_triggered:
                # Short Press -> Replay
                if self.suppress:
                    self.replay_hotkey()

    def execute(self):
        self.is_execution_triggered = True
        if self.callback:
            self.callback()

    def replay_hotkey(self):
        # Unhook, Send, Rehook
        self.active = False # prevent self-trigger
        try:
            if self.hotkey_ref:
                keyboard.remove_hotkey(self.hotkey_ref)
            
            # Send the combination
            keyboard.send(self.trigger)
            
            # Brief wait to ensure OS processes input before we re-hook
            time.sleep(0.05)
            
            # Re-hook
            self.hotkey_ref = keyboard.add_hotkey(
                self.trigger, 
                self.on_activate, 
                suppress=self.suppress, 
                trigger_on_release=False
            )
            self.active = True
        except Exception as e:
            print(f"Error replaying hotkey {self.trigger}: {e}")
            self.active = True # Restore safety
