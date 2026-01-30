import win32gui
import win32con
import win32clipboard
import subprocess
import subprocess
import os

def focus_window(window_title):
    """
    Finds a window by partial title match and brings it to the foreground.
    """
    def callback(hwnd, handles):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_title.lower() in title.lower():
                handles.append(hwnd)
        return True

    handles = []
    win32gui.EnumWindows(callback, handles)

    if handles:
        target_hwnd = handles[0] # Pick the first match
        # If minimized, restore it
        if win32gui.IsIconic(target_hwnd):
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
        
        # Bring to foreground
        try:
            win32gui.SetForegroundWindow(target_hwnd)
        except Exception as e:
            print(f"Error focusing window: {e}")
            # Sometimes SetForegroundWindow fails if the calling thread isn't foreground.
            # We can try a trick or just log it.
            pass
        return True
    return False

def run_command(command):
    """
    Runs a command or executable.
    Uses os.startfile on Windows for better file/folder opening support.
    """
    try:
        # Try native startfile first (handles spaces, associations, folders best)
        if os.name == 'nt':
            try:
                os.startfile(command)
                return
            except OSError:
                pass # Fallback to subprocess if not a file/path

        # Popen is non-blocking
        subprocess.Popen(command, shell=True)
    except Exception as e:
        print(f"Error running command: {e}")

import webbrowser

def open_url(url):
    """
    Opens a URL in the default web browser.
    Ensures the URL has a scheme (http/https).
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening URL: {e}")

def set_clipboard(text):
    """
    Sets the clipboard content to the given text using win32clipboard.
    """
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"Error setting clipboard: {e}")
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        return False
