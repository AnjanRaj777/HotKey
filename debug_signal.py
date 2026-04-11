from PyQt6.QtCore import QObject, pyqtSignal

class Signaller(QObject):
    sig = pyqtSignal(int)

def slot():
    print("Slot called")

def verify():
    s = Signaller()
    # Case 1: lambda with no args
    try:
        s.sig.connect(lambda: print("Lambda called"))
        print("Emitting signal...")
        s.sig.emit(10) 
        print("Success: Lambda with no args works (PyQt ignores extras?)")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    verify()
