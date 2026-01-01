import os
import time
import shutil
import subprocess
import tempfile
import glob
from datetime import datetime
from config import load_config
from logs import logger, ActionLogger

class Cleaner:
    def __init__(self):
        self.config = load_config()
        self.deleted_files = 0
        self.deleted_size = 0
        self.errors = 0
        self.simulation_mode = self.config.get("simulation_mode", False)
        self.cleaned_items = [] # List of dicts {path, size, category}

    def is_path_excluded(self, file_path):
        """Check if path is in exclusion list."""
        file_path_upper = file_path.upper()
        for excluded in self.config.get("exclusions", []):
            if excluded.upper() in file_path_upper:
                return True
        return False

    def run_silent(self, cmd_list):
        """Run a subprocess command silently (no console window)."""
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(cmd_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
            return True
        except Exception as e:
            logger.error(f"Error running silent command {cmd_list}: {e}")
            return False

    def remove_file(self, file_path, category="System"):
        """Remove file or simulate removal."""
        try:
            size = os.path.getsize(file_path)
            if not self.simulation_mode:
                os.remove(file_path)
                ActionLogger.log_deletion(file_path, size, category, "deleted")
            else:
                ActionLogger.log_deletion(file_path, size, category, "simulated")
            
            self.deleted_files += 1
            self.deleted_size += size
            self.cleaned_items.append({
                "path": file_path,
                "size": size,
                "category": category
            })
            return True
        except Exception as e:
            self.errors += 1
            logger.error(f"Error removing {file_path}: {e}")
            ActionLogger.log_deletion(file_path, 0, category, "error", str(e))
            return False

    def clean_directory(self, path, patterns=None, category="System", max_age=0):
        """Clean files in a directory matching patterns."""
        if not os.path.exists(path):
            return

        if patterns is None:
            patterns = ["*"]

        for pattern in patterns:
            try:
                # Recursive search if pattern contains **
                recursive = "**" in pattern
                search_path = os.path.join(path, pattern)
                
                for file_path in glob.glob(search_path, recursive=recursive):
                    if not os.path.isfile(file_path):
                        continue
                        
                    if self.is_path_excluded(file_path):
                        continue

                    # Check age
                    if max_age > 0:
                        if time.time() - os.path.getmtime(file_path) < max_age:
                            continue

                    self.remove_file(file_path, category)
            except Exception as e:
                logger.error(f"Error cleaning {path} with pattern {pattern}: {e}")

    def clean_browsers(self):
        """Clean browser caches."""
        if not self.config.get("categories", {}).get("browsers", True):
            return

        browsers = {
            "Chrome": r"%LOCALAPPDATA%\Google\Chrome\User Data",
            "Edge": r"%LOCALAPPDATA%\Microsoft\Edge\User Data",
            "Brave": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data",
            "Opera": r"%APPDATA%\Opera Software\Opera Stable",
            "Opera GX": r"%APPDATA%\Opera Software\Opera GX Stable",
            "Vivaldi": r"%LOCALAPPDATA%\Vivaldi\User Data",
            "Yandex": r"%LOCALAPPDATA%\Yandex\YandexBrowser\User Data"
        }

        patterns = [
            r"**\Cache\*",
            r"**\Code Cache\*",
            r"**\GPUCache\*",
            r"**\ShaderCache\*",
            r"**\Service Worker\CacheStorage\*",
            r"**\Crashpad\reports\*"
        ]

        for name, path in browsers.items():
            full_path = os.path.expandvars(path)
            self.clean_directory(full_path, patterns, f"Browser ({name})")

    def clean_gaming(self):
        """Clean gaming platforms."""
        if not self.config.get("categories", {}).get("gaming", False):
            return

        paths = {
            "Steam": [
                r"%LOCALAPPDATA%\Steam\htmlcache\*",
                r"C:\Program Files (x86)\Steam\dumps\*",
                r"C:\Program Files (x86)\Steam\logs\*"
            ],
            "Epic Games": [
                r"%LOCALAPPDATA%\EpicGamesLauncher\Saved\webcache\*",
                r"%LOCALAPPDATA%\EpicGamesLauncher\Saved\Logs\*"
            ],
            "NVIDIA": [
                r"%LOCALAPPDATA%\NVIDIA Corporation\GLCache\*",
                r"%LOCALAPPDATA%\NVIDIA\DXCache\*"
            ],
            "AMD": [
                r"%LOCALAPPDATA%\AMD\DxCache\*"
            ],
            "Discord": [
                r"%APPDATA%\discord\Cache\*",
                r"%APPDATA%\discord\Code Cache\*"
            ],
            "Riot Games": [
                r"%LOCALAPPDATA%\Riot Games\Riot Client\Logs\*"
            ],
            "Ubisoft": [
                r"%LOCALAPPDATA%\Ubisoft Game Launcher\logs\*"
            ]
        }

        # Discord Fix & Add Battle.net
        paths["Discord"] = [
            r"%APPDATA%\discord\Cache\*",
            r"%APPDATA%\discord\Code Cache\*",
            r"%APPDATA%\discord\GPUCache\*"
        ]
        paths["Battle.net"] = [
            r"%LOCALAPPDATA%\Battle.net\Cache\*",
            r"%LOCALAPPDATA%\Battle.net\Logs\*"
        ]

        for name, path_list in paths.items():
            for path in path_list:
                full_path = os.path.expandvars(path)
                # Split into dir and pattern
                if "*" in full_path:
                    base_dir = os.path.dirname(full_path.split("*")[0])
                    pattern = os.path.basename(full_path)
                    self.clean_directory(base_dir, [pattern], f"Gaming ({name})")

    def clean_system(self):
        """Clean system temporary files."""
        if not self.config.get("categories", {}).get("system", True):
            return

        # Temp folders
        temp_dirs = [
            tempfile.gettempdir(), 
            r"C:\Windows\Temp",
            os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
            r"C:\Windows\Prefetch",
            r"C:\Windows\SoftwareDistribution\Download"
        ]
        
        for temp in temp_dirs:
            self.clean_directory(temp, ["*"], "System Temp")

        # Windows Logs (Safe)
        if self.config.get("deep_clean_enabled", False):
            self.clean_directory(r"C:\Windows\Logs", ["*.log"], "System Logs")
            self.clean_directory(r"C:\Windows\Minidump", ["*.dmp"], "Crash Dumps")

    def clean_apps(self):
        """Clean common application caches."""
        if not self.config.get("categories", {}).get("apps", True):
            return

        apps = {
            "Spotify": r"%LOCALAPPDATA%\Spotify\Storage\*",
            "Adobe": r"%LOCALAPPDATA%\Adobe\Common\Media Cache Files\*",
            "Teams": r"%APPDATA%\Microsoft\Teams\Cache\*"
        }
        
        # New Social Apps
        apps["Slack"] = r"%APPDATA%\Slack\Cache\*" # Will also catch Code Cache via glob if we used **
        # For Slack we need multiple paths so we handle separately or use wildcards more aggressively
        # Let's add specific entries for better control
        additional_apps = {
            "Slack": [
                r"%APPDATA%\Slack\Cache\*",
                r"%APPDATA%\Slack\Code Cache\*", 
                r"%APPDATA%\Slack\GPUCache\*"
            ],
            "Telegram": [
                r"%APPDATA%\Telegram Desktop\tdata\temp\*" # Safe temp only
            ]
        }
        
        # Standard single-path apps
        for name, path in apps.items():
            full_path = os.path.expandvars(path)
            base_dir = os.path.dirname(full_path.split("*")[0])
            self.clean_directory(base_dir, ["*"], f"App ({name})")

        # Multi-path apps
        for name, paths in additional_apps.items():
            for path in paths:
                full_path = os.path.expandvars(path)
                base_dir = os.path.dirname(full_path.split("*")[0])
                if os.path.exists(base_dir):
                    self.clean_directory(base_dir, ["*"], f"App ({name})")

    def clean_dev(self):
        """Clean developer tool caches."""
        if not self.config.get("categories", {}).get("dev", True):
            return

        # VS Code
        vscode_paths = [
            r"%APPDATA%\Code\Cache\*",
            r"%APPDATA%\Code\CachedData\*",
            r"%APPDATA%\Code\Code Cache\*",
            r"%APPDATA%\Code\GPUCache\*"
        ]
        
        for path in vscode_paths:
            full = os.path.expandvars(path)
            base = os.path.dirname(full.split("*")[0])
            self.clean_directory(base, ["*"], "Dev (VS Code)")

        # JetBrains (PyCharm, IntelliJ, Android Studio)
        # Using glob to find versions
        jetbrains_locations = [
            r"%LOCALAPPDATA%\JetBrains\PyCharm*\caches",
            r"%LOCALAPPDATA%\JetBrains\IntelliJ*\caches",
            r"%LOCALAPPDATA%\Google\AndroidStudio*\caches"
        ]

        for location in jetbrains_locations:
            expanded_loc = os.path.expandvars(location)
            # Find directories matching the pattern (e.g. PyCharm2023.1)
            # Note: clean_directory expects a base path, but here the base path *is* the variable part.
            # We need to list directories first.
            parent = os.path.dirname(expanded_loc)
            if os.path.exists(parent):
                pattern = os.path.basename(expanded_loc)
                for folder in glob.glob(os.path.join(parent, pattern)):
                    if os.path.isdir(folder):
                        self.clean_directory(folder, ["*"], f"Dev ({os.path.basename(os.path.dirname(folder))})")

    def perform_cleanup(self, simulation=False):
        """Execute cleanup routine."""
        self.config = load_config() # Reload config
        self.simulation_mode = simulation or self.config.get("simulation_mode", False)
        
        self.deleted_files = 0
        self.deleted_size = 0
        self.errors = 0
        self.cleaned_items = []

        logger.info(f"Starting cleanup (Simulation: {self.simulation_mode})...")
        
        self.clean_system()
        self.clean_browsers()
        self.clean_gaming()
        self.clean_gaming()
        self.clean_apps()
        self.clean_dev()
        
        # DNS Flush (Real only)
        if not self.simulation_mode:
            self.run_silent(["ipconfig", "/flushdns"])

        logger.info(f"Cleanup finished. Files: {self.deleted_files}, Size: {self.deleted_size}")
        
        return {
            "files_cleaned": self.deleted_files,
            "space_freed": self.deleted_size,
            "errors": self.errors,
            "items": self.cleaned_items
        }
