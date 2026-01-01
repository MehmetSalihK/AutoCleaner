import os
import sys
import ctypes
from logs import logger

def is_admin():
    """Check if running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def hide_console():
    """Hide console window on Windows."""
    if sys.platform == 'win32':
        try:
            import ctypes
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd != 0:
                ctypes.windll.user32.ShowWindow(whnd, 0)
        except:
            pass

def format_file_size(size_bytes):
    """Format bytes to human readable size."""
    try:
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    except:
        return "0 B"

def load_logo(size=(64, 64)):
    """Load application logo."""
    try:
        from PIL import Image
        if os.path.exists("AutoCleanerLogo.png"):
            return Image.open("AutoCleanerLogo.png").resize(size)
        elif os.path.exists("AutoCleanerLogo.ico"):
            return Image.open("AutoCleanerLogo.ico").resize(size)
    except:
        pass
    return None

def show_notification(title, message, duration=5):
    """Show Windows notification using native API."""
    try:
        # Try winotify first (most reliable)
        from winotify import Notification
        
        icon_path = ""
        if os.path.exists(os.path.abspath("AutoCleanerLogo.ico")):
            icon_path = os.path.abspath("AutoCleanerLogo.ico")
            
        toast = Notification(
            app_id="AutoCleaner Demo",
            title=title,
            msg=message,
            duration="short" if duration <= 5 else "long",
            icon=icon_path
        )
        
        toast.show()
        return True
        
    except ImportError:
        # Fallback to win10toast if winotify not available
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                duration=duration,
                threaded=True
            )
            return True
        except:
            pass
    
    except Exception as e:
        logger.error(f"Failed to show notification: {e}")
    
    # Last resort: Windows MessageBox (blocking but always works)
    try:
        import ctypes
        MB_ICONINFORMATION = 0x40
        ctypes.windll.user32.MessageBoxW(0, message, title, MB_ICONINFORMATION)
        return True
    except:
        pass
    
    return False
