import os
import sys
import time
import threading
import subprocess
import ctypes
import tempfile
from win10toast_persist import ToastNotifier
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import messagebox

# Initialisation
notifier = ToastNotifier()
deleted_files = 0
errors = 0

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def clear_temp_folder(path):
    global deleted_files, errors
    count = 0
    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                try:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                    count += 1
                except Exception:
                    errors += 1
    except Exception:
        pass
    deleted_files += count
    return count

def clear_logs():
    global errors
    for log in ['Application', 'System', 'Security']:
        try:
            subprocess.run(['wevtutil', 'cl', log], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            errors += 1

def clear_dns():
    global errors
    try:
        subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        errors += 1

def perform_cleanup():
    temp1 = tempfile.gettempdir()
    temp2 = "C:\\Windows\\Temp"

    count1 = clear_temp_folder(temp1)
    count2 = clear_temp_folder(temp2)
    clear_logs()
    clear_dns()

    total = count1 + count2
    notifier.show_toast("Nettoyage terminé",
                        f"{total} fichiers supprimés, {errors} erreurs",
                        duration=5, threaded=True)

def schedule_cleanup():
    while True:
        perform_cleanup()
        time.sleep(300)  # Toutes les 5 minutes

def show_stats():
    root = tk.Tk()
    root.title("AutoCleaner - Statistiques")
    root.geometry("300x150")
    root.resizable(False, False)

    lbl1 = tk.Label(root, text=f"Fichiers supprimés : {deleted_files}", font=("Segoe UI", 11))
    lbl1.pack(pady=10)

    lbl2 = tk.Label(root, text=f"Erreurs rencontrées : {errors}", font=("Segoe UI", 11))
    lbl2.pack(pady=5)

    def force_clean():
        perform_cleanup()
        lbl1.config(text=f"Fichiers supprimés : {deleted_files}")
        lbl2.config(text=f"Erreurs rencontrées : {errors}")
        messagebox.showinfo("Nettoyage forcé", "Nettoyage terminé.")

    btn = tk.Button(root, text="Nettoyer maintenant", command=force_clean)
    btn.pack(pady=10)

    root.mainloop()

def create_image():
    image_path = os.path.join(os.path.dirname(__file__), "AutoCleanerLogo.ico")
    if os.path.exists(image_path):
        return Image.open(image_path).resize((64, 64))
    else:
        img = Image.new('RGB', (64, 64), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.rectangle((16, 16, 48, 48), fill=(0, 122, 204))
        return img

def quit_app(icon, item):
    icon.stop()
    sys.exit()

def add_to_startup():
    try:
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        script_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        shortcut_path = os.path.join(startup_path, "AutoCleaner.lnk")
        import pythoncom
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.save()
    except Exception as e:
        print(f"Erreur ajout démarrage: {e}")

def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        return

    # Notification de démarrage
    notifier.show_toast("AutoCleaner", "Le programme est lancé ✅", duration=5, threaded=True)

    add_to_startup()
    threading.Thread(target=schedule_cleanup, daemon=True).start()

    icon = Icon("AutoCleaner")
    icon.icon = create_image()
    icon.menu = Menu(
        MenuItem("Statistiques", lambda: threading.Thread(target=show_stats).start()),
        MenuItem("Quitter", quit_app)
    )
    icon.run()

if __name__ == "__main__":
    main()
