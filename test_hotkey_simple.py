
import keyboard
import time

def on_triggered():
    print("Hotkey h+j triggered!")

print("Registering h+j...")
try:
    keyboard.add_hotkey('h+j', on_triggered, suppress=False)
    print("Registered. Press h+j to test. Press Esc to exit.")
    keyboard.wait('esc')
except Exception as e:
    print(f"Error: {e}")
