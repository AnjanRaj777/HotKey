import keyboard
import time
from hotkey_manager import LongPressHandler

print("Testing LongPressHandler independent of App...")

def on_trigger():
    print(">>> ACTION EXECUTED! <<<")

# Test Single Key
print("\nTest 1: Single Key 'k' (Hold for 1s)")
h1 = LongPressHandler('k', on_trigger, 1.0, suppress=True)
h1.start()

print("Press 'k' shortly to test replay (output 'k').")
print("Press 'k' long (>1s) to test action.")
print("Press 'esc' to move to next test.")
keyboard.wait('esc')
h1.stop()

# Test Combo
print("\nTest 2: Combo 'ctrl+alt+l' (Hold for 1s)")
h2 = LongPressHandler('ctrl+alt+l', on_trigger, 1.0, suppress=True)
h2.start()

print("Press 'ctrl+alt+l' shortly to test replay.")
print("Press 'ctrl+alt+l' long (>1s) to test action.")
print("Press 'esc' to exit.")
keyboard.wait('esc')
h2.stop()
print("Done.")
