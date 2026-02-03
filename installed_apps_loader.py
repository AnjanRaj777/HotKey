import os
import win32com.client

def get_installed_apps():
    """
    Scans the Windows Start Menu (All Users and Current User) for application shortcuts.
    Returns a list of dictionaries with 'name', 'path', and 'icon_path' (same as path for now).
    """
    apps = []
    shell = win32com.client.Dispatch("WScript.Shell")
    
    # Common Start Menu locations
    locations = [
        shell.SpecialFolders("AllUsersPrograms"),
        shell.SpecialFolders("Programs")
    ]
    
    seen_paths = set()

    for location in locations:
        if not os.path.exists(location):
            continue
            
        for root, dirs, files in os.walk(location):
            for file in files:
                if file.endswith(".lnk"):
                    lnk_path = os.path.join(root, file)
                    try:
                        shortcut = shell.CreateShortcut(lnk_path)
                        target_path = shortcut.TargetPath
                        
                        # Normalize path for deduplication
                        norm_path = os.path.normpath(target_path).lower()
                        
                        # Only include if it points to an exe and hasn't been seen
                        if norm_path.endswith(".exe") and norm_path not in seen_paths:
                            name = os.path.splitext(file)[0]
                            seen_paths.add(norm_path)
                            apps.append({
                                "name": name,
                                "path": target_path,
                                "lnk": lnk_path
                            })
                    except Exception as e:
                        # Skip broken shortcuts
                        continue
                        
    # Sort by name
    apps.sort(key=lambda x: x["name"].lower())
    return apps
