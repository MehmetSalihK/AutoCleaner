import os
import sys
import win32com.client
from pathlib import Path

def create_shortcut():
    try:
        # Define paths
        app_name = "AutoCleaner Demo"
        # Assuming we are running inside the repo
        target = os.path.abspath("main.py")
        python_exe = sys.executable
        icon = os.path.abspath("AutoCleanerLogo.ico")
        
        # Start Menu Path
        shell = win32com.client.Dispatch("WScript.Shell")
        start_menu = shell.SpecialFolders("StartMenu")
        shortcut_path = os.path.join(start_menu, "Programs", f"{app_name}.lnk")
        
        print(f"Creating shortcut at: {shortcut_path}")
        
        # Create shortcut
        shortcut = shell.CreateShortcut(shortcut_path)
        # We need to run python.exe with main.py as argument
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = os.path.dirname(target)
        if os.path.exists(icon):
            shortcut.IconLocation = icon
        shortcut.Description = "AutoCleaner System Optimizer"
        shortcut.save()
        
        print("Shortcut created successfully!")
        print("Notifications should now work.")
        
    except Exception as e:
        print(f"Failed to create shortcut: {e}")

if __name__ == "__main__":
    create_shortcut()
