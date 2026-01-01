import threading
import time
import sys
import os
import ctypes
import multiprocessing
from tkinter import messagebox

from config import load_config
from logs import logger
from utils import is_admin, hide_console, format_file_size
from cleaner import Cleaner
from ui import ModernApp, SystemTray

def check_single_instance():
    """Ensure only one instance is running using a named mutex."""
    mutex_name = "AutoCleaner_v7_Mutex"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    
    if last_error == 183:  # ERROR_ALREADY_EXISTS
        return False, mutex
    return True, mutex

def background_auto_clean(cleaner):
    """Background thread for automatic cleaning with notifications."""
    while True:
        config = load_config()
        interval_minutes = config.get("auto_clean_interval_minutes", 30)
        time.sleep(interval_minutes * 60)  # Convert minutes to seconds
        
        if config.get("startup_enabled", True):
            logger.info("Starting automatic background cleanup...")
            try:
                result = cleaner.perform_cleanup(simulation=False)
                
                # Send notification if enabled
                if config.get("notifications_enabled", True):
                    from utils import show_notification
                    show_notification(
                        "AutoCleaner Pro - Nettoyage Automatique",
                        f"✅ Nettoyage terminé !\n"
                        f"📁 {result['files_cleaned']} fichiers supprimés\n"
                        f"💾 {format_file_size(result['space_freed'])} libérés",
                        duration=5
                    )
            except Exception as e:
                logger.error(f"Auto-clean failed: {e}")

def main():
    try:
        # 0. Single Instance Check
        logger.info("Checking instance...")
        is_unique, mutex = check_single_instance()
        if not is_unique:
            logger.info("Already running! Exiting.")
            sys.exit(0)
            
        logger.info("Instance is unique. Starting setup...")

        # 1. Setup
        hide_console()
        logger.info("AutoCleaner Demo v1.0 Starting...")
        
        if not is_admin():
            # Re-run with admin privileges
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()
            except Exception as e:
                logger.error(f"Failed to elevate privileges: {e}")
                from tkinter import messagebox
                messagebox.showerror("Error", "AutoCleaner needs Administrator privileges to run correctly.")
                return

        config = load_config()
        # 2. Initialize Components
        logger.info("Initializing Cleaner...")
        cleaner = Cleaner()
        logger.info("Cleaner initialized.")

        # System Tray
        logger.info("Initializing Tray...")
        tray = None

        # 2. UI & System Tray Setup
        def show_dashboard():
            try:
                app.deiconify()
                app.lift()
                app.focus_force()
            except Exception as e:
                logger.error(f"Failed to show dashboard: {e}")

        def exit_app():
            try:
                if 'tray' in locals():
                    tray.stop()
                if 'app' in locals():
                    app.quit()
            except:
                pass
            sys.exit()

        # Initialize System Tray FIRST (in background) - with error handling
        tray = None
        try:
            tray = SystemTray(show_dashboard, exit_app)
            tray_thread = threading.Thread(target=tray.run, daemon=True)
            tray_thread.start()
            logger.info("Tray thread started.")
            time.sleep(0.5)  # Allow tray to initialize
        except Exception as e:
            logger.error(f"Failed to initialize tray: {e}")
            # Continue without tray

        # Initialize Dashboard
        try:
            logger.info("Initializing ModernApp...")
            app = ModernApp(cleaner, exit_app)
            logger.info("ModernApp initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize UI: {e}")
            from tkinter import messagebox
            messagebox.showerror("Erreur Critique", f"Impossible de démarrer l'interface:\n{str(e)}")
            sys.exit(1)
        
        # 3. Start Background Auto-Clean Thread
        try:
            if config.get("startup_enabled", True):
                auto_clean_thread = threading.Thread(target=background_auto_clean, args=(cleaner,), daemon=True)
                auto_clean_thread.start()
        except Exception as e:
            logger.error(f"Failed to start auto-clean thread: {e}")

        # Run App
        try:
            app.mainloop()
        except KeyboardInterrupt:
            exit_app()
        except Exception as e:
            logger.error(f"App crashed: {e}")
            exit_app()
            
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        try:
            from tkinter import messagebox
            messagebox.showerror("Erreur Critique", f"AutoCleaner a rencontré une erreur:\n{str(e)}")
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
