import keyboard
import time
import threading

def on_press(event):
    print(f"Key Press Down: {event.name}")
    # Try combo detection
    if keyboard.is_pressed('ctrl+alt+t'):
        print("Combo Active!: ctrl+alt+t")

# keyboard.hook(on_press)

print("Press 'k' to test single key Long Press or 'ctrl+alt+k' for combo.")

# Simulating combo press detection
def combo_handler():
    print("Combo Triggered (Down)!")
    time.sleep(1) # Fake delay
    if keyboard.is_pressed('ctrl+alt+k'):
        print("Combo Long Press Success!")
    else:
        print("Combo Released Early!")

try:
    # Adding a hotkey for combo test
    keyboard.add_hotkey('ctrl+alt+k', combo_handler, suppress=True, trigger_on_release=False)
    
    # Adding single key handler
    keyboard.on_press_key('k', lambda e: print("Single K Down"), suppress=True)
    
    keyboard.wait('esc')
except KeyboardInterrupt:
    pass
