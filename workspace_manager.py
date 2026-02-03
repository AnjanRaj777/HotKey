import uuid
import os
import time
from pyvda import AppView, VirtualDesktop, get_virtual_desktops
from utils import run_command

class WorkspaceManager:
    def __init__(self, config_manager, hotkey_manager):
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager

    def get_workspaces(self):
        return self.config_manager.get_workspaces()

    def create_workspace(self, name, desktop_index=1, apps=None, hotkey_profile_id=None, launch_hotkey=None):
        workspace = {
            "id": str(uuid.uuid4()),
            "name": name,
            "desktop_index": desktop_index, # 1-based index
            "apps": apps if apps else [],
            "hotkey_profile_id": hotkey_profile_id,
            "launch_hotkey": launch_hotkey
        }
        self.config_manager.add_workspace(workspace)
        return workspace

    def switch_to_workspace(self, workspace_id):
        workspace = self.config_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            print(f"Workspace {workspace_id} not found.")
            return

        print(f"Switching to Workspace: {workspace['name']}")

        # 1. Switch Virtual Desktop
        # 1. Switch Virtual Desktop
        try:
            target_index = workspace.get("desktop_index", 1)
            desktops = get_virtual_desktops()
            
            # Auto-create if not exists
            while len(desktops) < target_index:
                print(f"Creating new desktop (Current: {len(desktops)}, Target: {target_index})")
                VirtualDesktop.create()
                time.sleep(0.5) # Wait for Windows to register
                desktops = get_virtual_desktops()
            
            # Switch
            if 1 <= target_index <= len(desktops):
                VirtualDesktop(target_index).go()
            else:
                print(f"Desktop index {target_index} out of range (Available: {len(desktops)})")
        except Exception as e:
            print(f"Error switching desktop: {e}")

        # 2. Launch Apps
        apps = workspace.get("apps", [])
        for app_path in apps:
            # Check if running? Ideally yes, but simplistic "run" for now.
            # config_manager.py uses utils.run_command
            try:
                run_command(app_path)
            except Exception as e:
                print(f"Failed to launch {app_path}: {e}")

        # 3. Update Active Profile (Hotkeys)
        # We need to tell HotkeyManager to filter for this workspace or profile.
        # For now, let's assume we store the current workspace ID in a runtime state
        self.hotkey_manager.set_current_workspace(workspace_id)
        
        # Determine if we need to reload hotkeys
        # HotkeyManager.set_current_workspace should trigger a reload if necessary
