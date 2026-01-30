import ctypes
from ctypes import c_int, byref, sizeof, Structure, c_void_p
from enum import Enum

class WINDOWCOMPOSITIONATTRIB(Enum):
    WCA_ACCENT_POLICY = 19

class ACCENT_STATE(Enum):
    ACCENT_DISABLED = 0
    ACCENT_ENABLE_GRADIENT = 1
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
    ACCENT_ENABLE_BLURBEHIND = 3
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
    ACCENT_INVALID_STATE = 5

class ACCENT_POLICY(Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_int),
        ("AnimationId", ctypes.c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", c_void_p),
        ("SizeOfData", ctypes.c_int)
    ]

def apply_blur(hwnd, enable=True, accent_state=ACCENT_STATE.ACCENT_ENABLE_BLURBEHIND):
    try:
        user32 = ctypes.windll.user32
        set_window_composition_attribute = user32.SetWindowCompositionAttribute
        set_window_composition_attribute.argtypes = [c_void_p, c_void_p]
        set_window_composition_attribute.restype = ctypes.c_int

        policy = ACCENT_POLICY()
        if enable:
            policy.AccentState = accent_state.value
            # GradientColor: AABBGGRR (hex). 
            # Often needs a specific color for Acrylic. e.g. 0 with low alpha.
            # For pure blur, simple 0 is usually fine or specific tint.
            # Using a semi-transparent black for generic compatibility: 0x99000000 (AA=99)
            policy.GradientColor = 0x00000000 
        else:
            policy.AccentState = ACCENT_STATE.ACCENT_DISABLED.value
            policy.GradientColor = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        data.Data = ctypes.cast(ctypes.pointer(policy), c_void_p)
        data.SizeOfData = sizeof(policy)

        set_window_composition_attribute(int(hwnd), byref(data))
    except Exception as e:
        print(f"Failed to apply blur: {e}")
