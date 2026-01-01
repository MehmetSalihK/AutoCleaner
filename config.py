import os
import json
from pathlib import Path

# Constants
APP_NAME = "AutoCleaner Demo"
VERSION = "1.0"
CONTACT_EMAIL = "support@autocleaner.com"
# Remplacez ceci par votre URL de Webhook (Discord ou Formspree)
FEEDBACK_WEBHOOK_URL = "https://discord.com/api/webhooks/1456157510678351988/Ax-isQ4rXRv6F70eq7G_caYhmgaD1GP0AFjnen-kXUfW6oJgxM3S_hQBfVnK-ppWXSW8" 
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".autocleaner_config_v4.json")

# Default Configuration v4.0
DEFAULT_CONFIG = {
    "auto_cleanup_interval": 60,  # minutes
    "notifications_enabled": True,
    "sound_enabled": True,
    "deep_clean_enabled": False,
    "minimize_to_tray": True, # v4.5
    "preserve_credentials": True, # v4.5
    "log_retention_days": 90, # v4.5
    "auto_clean_interval_minutes": 30, # v4.7 - Auto clean every X minutes
    "startup_enabled": True,
    "theme": "dark",  # dark, light, system
    "theme_accent": "green", # green, blue, dark-blue
    "language": "fr",
    "stealth_mode": False,
    "simulation_mode": False, # Dry run
    "gaming_mode": False, # Auto clean before game launch (future)
    "categories": {
        "system": True,
        "browsers": True,
        "gaming": False,
        "apps": True,
        "dev": True
    },
    "exclusions": [
        # Critical System
        "Windows\\System32",
        "Windows\\SysWOW64",
        "Windows\\WinSxS",
        
        # Browsers - Keep Data
        "User Data\\Default\\Bookmarks",
        "User Data\\Default\\Login Data",
        "User Data\\Default\\Preferences",
        "User Data\\Default\\Sessions",
        
        # Gaming - Keep Saves
        "Steam\\userdata",
        "steamapps",
        "Saved Games",
        "Documents\\My Games"
    ]
}

def load_config():
    """Load configuration from JSON file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with default to ensure all keys exist
                return {**DEFAULT_CONFIG, **config}
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception:
        pass
