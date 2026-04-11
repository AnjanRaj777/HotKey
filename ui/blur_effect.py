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
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", c_void_p),
        ("SizeOfData", ctypes.c_int)
    ]

# Gradient color format: 0xAABBGGRR  (Alpha=opacity of tint, then BGR channels)
# Lower AA = more transparent tint = more frosted blur visible. Same navy RGB.
GRADIENT_DEEP_BLUE  = 0x721A0F0A   # ~45% tint opacity, navy blue — strong blur visible
GRADIENT_MIDNIGHT   = 0x90100606   # ~56% opacity, deep blue
GRADIENT_DARK_SLATE = 0x55201212   # ~33% opacity, very glassy


def _set_accent(hwnd, state: ACCENT_STATE, gradient_color: int, flags: int = 2):
    """Low-level helper: call SetWindowCompositionAttribute."""
    try:
        user32 = ctypes.windll.user32
        fn = user32.SetWindowCompositionAttribute
        fn.argtypes = [c_void_p, c_void_p]
        fn.restype = ctypes.c_int

        policy = ACCENT_POLICY()
        policy.AccentState   = state.value
        policy.AccentFlags   = flags
        policy.GradientColor = gradient_color
        policy.AnimationId   = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute  = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        data.Data       = ctypes.cast(ctypes.pointer(policy), c_void_p)
        data.SizeOfData = sizeof(policy)

        res = fn(int(hwnd), byref(data))
        if res == 0:
            print("SetWindowCompositionAttribute returned 0 (may be unsupported on this build).")
        return res
    except Exception as e:
        print(f"_set_accent error: {e}")
        return 0


def _apply_rounded_corners(hwnd):
    """Ask DWM for Win11-style rounded corners."""
    try:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        pref = c_int(DWMWCP_ROUND)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(hwnd), DWMWA_WINDOW_CORNER_PREFERENCE, byref(pref), sizeof(pref)
        )
    except Exception:
        pass  # Win10 and older don't support this attribute


def apply_blur(hwnd, enable=True,
               accent_state=ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND,
               gradient_color=0x44FFFFFF):
    """
    Legacy helper kept for back-compatibility.
    Prefer apply_acrylic_blur() for the solid deep-blue look.
    """
    if enable:
        _set_accent(hwnd, accent_state, gradient_color)
    else:
        _set_accent(hwnd, ACCENT_STATE.ACCENT_DISABLED, 0)
    _apply_rounded_corners(hwnd)


def apply_acrylic_blur(hwnd, gradient_color=GRADIENT_DEEP_BLUE):
    """
    Apply a solid, high-quality blur with a deep navy-blue tint.
    Using ACCENT_ENABLE_BLURBEHIND to ensure the blur actually works 
    and doesn't fall back to plain transparency on some Windows builds.
    """
    # BLURBEHIND generally avoids the lag and "clear transparency" bug of ACRYLIC.
    # We use flags=0 and gradient_color=0 because BLURBEHIND ignores them,
    # and passing non-zero values or conflicting DWM commands causes intense graphical glitches!
    _set_accent(hwnd, ACCENT_STATE.ACCENT_ENABLE_BLURBEHIND, 0, flags=0)
    _apply_rounded_corners(hwnd)


def remove_blur(hwnd):
    """Remove blur effect from a window."""
    _set_accent(hwnd, ACCENT_STATE.ACCENT_DISABLED, 0, flags=0)
