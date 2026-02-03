import os
import win32com.client

def get_installed_apps():
    apps = []
    shell = win32com.client.Dispatch("WScript.Shell")
    
    # Common Start Menu locations using WScript.Shell
    # "AllUsersPrograms" -> C:\ProgramData\Microsoft\Windows\Start Menu\Programs
    # "Programs" -> C:\Users\<User>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs
    
    locations = [
        shell.SpecialFolders("AllUsersPrograms"),
        shell.SpecialFolders("Programs")
    ]
    
    print(f"Scanning locations: {locations}")

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
                        
                        # Only include if it points to an exe
                        if target_path.lower().endswith(".exe"):
                            name = os.path.splitext(file)[0]
                            # Try to get icon? ExtractIcon is harder without win32api/gui, 
                            # but we can just use the target executable path and let Qt extract it if needed.
                            apps.append({
                                "name": name,
                                "path": target_path,
                                "lnk": lnk_path
                            })
                    except Exception as e:
                        # Some shortcuts might be broken or unreadable
                        pass
                        
    return apps

if __name__ == "__main__":
    try:
        apps = get_installed_apps()
        print(f"Found {len(apps)} apps.")
        # Deduplicate by path
        seen = set()
        unique_apps = []
        for app in apps:
            if app['path'].lower() not in seen:
                seen.add(app['path'].lower())
                unique_apps.append(app)
        
        print(f"Unique Executables: {len(unique_apps)}")
        for app in unique_apps[:10]: # Print first 10
            print(f"{app['name']}: {app['path']}")
    except Exception as e:
        print(f"Global Error: {e}")
