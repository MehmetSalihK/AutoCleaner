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

# Dossiers et fichiers à exclure du nettoyage
EXCLUDED_PATHS = [
    # Chrome
    "Google\\Chrome\\User Data\\Default\\History",
    "Google\\Chrome\\User Data\\Default\\Cookies",
    "Google\\Chrome\\User Data\\Default\\Login Data",
    "Google\\Chrome\\User Data\\Default\\Bookmarks",
    "Google\\Chrome\\User Data\\Default\\Preferences",
    "Google\\Chrome\\User Data\\Default\\Sessions",
    "Google\\Chrome\\User Data\\Default\\Current Session",
    "Google\\Chrome\\User Data\\Default\\Current Tabs",
    
    # Firefox
    "Mozilla\\Firefox\\Profiles",
    
    # Edge
    "Microsoft\\Edge\\User Data\\Default\\History",
    "Microsoft\\Edge\\User Data\\Default\\Cookies",
    "Microsoft\\Edge\\User Data\\Default\\Login Data",
    
    # Explorer et système
    "Microsoft\\Windows\\Explorer",
    "Microsoft\\Windows\\Recent",
    "Microsoft\\Windows\\PowerShell\\PSReadLine",
    
    # Autres applications importantes
    "Adobe",
    "Microsoft\\Office",
    "Microsoft\\Teams",
    "Skype",
    "Discord",
    "Spotify",
    "Steam",
    "Epic Games"
]

def hide_console():
    """Cache la fenêtre console au démarrage"""
    if os.name == 'nt':
        import win32gui
        import win32con
        try:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        except:
            pass

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_path_excluded(file_path):
    """Vérifie si un chemin doit être exclu du nettoyage"""
    file_path_upper = file_path.upper()
    for excluded in EXCLUDED_PATHS:
        if excluded.upper() in file_path_upper:
            return True
    return False

def is_important_file(file_path):
    """Vérifie si c'est un fichier système ou important à garder"""
    important_extensions = ['.dll', '.exe', '.sys', '.ini', '.cfg', '.json']
    important_names = ['desktop.ini', 'thumbs.db', '.gitignore', 'readme']
    
    filename = os.path.basename(file_path).lower()
    
    # Vérifier les extensions importantes
    for ext in important_extensions:
        if filename.endswith(ext):
            return True
    
    # Vérifier les noms de fichiers importants
    for name in important_names:
        if name in filename:
            return True
    
    return False

def clear_temp_folder(path):
    global deleted_files, errors
    count = 0
    try:
        for root, dirs, files in os.walk(path):
            # Exclure certains dossiers entiers
            dirs[:] = [d for d in dirs if not any(excluded.split('\\')[-1].upper() == d.upper() 
                      for excluded in EXCLUDED_PATHS)]
            
            for name in files:
                try:
                    file_path = os.path.join(root, name)
                    
                    # Vérifier si le fichier doit être exclu
                    if is_path_excluded(file_path) or is_important_file(file_path):
                        continue
                    
                    # Vérifier l'âge du fichier (ne supprimer que les fichiers de plus de 1 jour)
                    file_age = time.time() - os.path.getmtime(file_path)
                    if file_age < 86400:  # 24 heures en secondes
                        continue
                    
                    # Vérifier la taille (ne pas supprimer les gros fichiers sans confirmation)
                    file_size = os.path.getsize(file_path)
                    if file_size > 100 * 1024 * 1024:  # Plus de 100MB
                        continue
                    
                    os.remove(file_path)
                    count += 1
                except (PermissionError, FileNotFoundError, OSError):
                    errors += 1
                except Exception:
                    errors += 1
    except Exception:
        pass
    deleted_files += count
    return count

def clear_logs():
    """Nettoie seulement les logs système, pas les logs d'applications"""
    global errors
    # Ne nettoyer que les logs système moins critiques
    safe_logs = ['Application']  # Retiré 'System' et 'Security' pour plus de sécurité
    
    for log in safe_logs:
        try:
            subprocess.run(['wevtutil', 'cl', log], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         timeout=30)
        except Exception:
            errors += 1

def clear_dns():
    global errors
    try:
        subprocess.run(["ipconfig", "/flushdns"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      timeout=10)
    except Exception:
        errors += 1

def clear_browser_cache_safe():
    """Nettoie le cache des navigateurs sans toucher aux données importantes"""
    global deleted_files, errors
    
    cache_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles\*\cache2")
    ]
    
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                count = 0
                for root, dirs, files in os.walk(cache_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            # Seulement les fichiers cache temporaires
                            if any(ext in file.lower() for ext in ['.tmp', '.cache', '.dat']):
                                os.remove(file_path)
                                count += 1
                        except:
                            errors += 1
                deleted_files += count
            except:
                errors += 1

def perform_cleanup():
    temp1 = tempfile.gettempdir()
    temp2 = "C:\\Windows\\Temp"

    count1 = clear_temp_folder(temp1)
    count2 = clear_temp_folder(temp2)
    
    # Nettoyage sécurisé du cache navigateur
    clear_browser_cache_safe()
    
    # Nettoyage système limité
    clear_logs()
    clear_dns()

    total = count1 + count2
    
    # Notification discrète (plus courte)
    notifier.show_toast("AutoCleaner",
                        f"✅ {total} fichiers nettoyés",
                        duration=3, threaded=True)

def schedule_cleanup():
    while True:
        perform_cleanup()
        time.sleep(600)  # Toutes les 10 minutes (moins fréquent)

def show_stats():
    root = tk.Tk()
    root.title("AutoCleaner - Statistiques")
    root.geometry("350x200")
    root.resizable(False, False)
    
    # Centrer la fenêtre
    root.eval('tk::PlaceWindow . center')

    lbl1 = tk.Label(root, text=f"Fichiers supprimés : {deleted_files}", font=("Segoe UI", 11))
    lbl1.pack(pady=10)

    lbl2 = tk.Label(root, text=f"Erreurs rencontrées : {errors}", font=("Segoe UI", 11))
    lbl2.pack(pady=5)
    
    lbl3 = tk.Label(root, text="Mode discret activé 🔒", font=("Segoe UI", 9), fg="green")
    lbl3.pack(pady=5)

    def force_clean():
        perform_cleanup()
        lbl1.config(text=f"Fichiers supprimés : {deleted_files}")
        lbl2.config(text=f"Erreurs rencontrées : {errors}")
        messagebox.showinfo("Nettoyage forcé", "Nettoyage sécurisé terminé.")

    btn = tk.Button(root, text="Nettoyer maintenant", command=force_clean)
    btn.pack(pady=10)
    
    btn2 = tk.Button(root, text="Fermer", command=root.destroy)
    btn2.pack(pady=5)

    root.mainloop()

def create_image():
    image_path = os.path.join(os.path.dirname(__file__), "AutoCleanerLogo.ico")
    if os.path.exists(image_path):
        return Image.open(image_path).resize((64, 64))
    else:
        # Icône plus discrète
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((16, 16, 48, 48), fill=(34, 139, 34, 180))  # Vert discret
        d.text((24, 28), "AC", fill=(255, 255, 255, 255))
        return img

def quit_app(icon, item):
    icon.stop()
    sys.exit()

def add_to_startup():
    try:
        # Clé de registre pour démarrage automatique (plus discret)
        import winreg
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
            script_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(reg_key, "AutoCleaner", 0, winreg.REG_SZ, script_path)
    except Exception as e:
        # Fallback vers la méthode raccourci si registre échoue
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
            shortcut.WindowStyle = 7  # Mode minimisé
            shortcut.save()
        except Exception:
            pass

def main():
    # Cacher la console dès le démarrage
    hide_console()
    
    if not is_admin():
        # Relancer en mode admin mais de façon discrète
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 0)
        return

    # Notification de démarrage plus discrète
    notifier.show_toast("AutoCleaner", 
                        "🛡️ Protection activée", 
                        duration=2, threaded=True)

    # Ajouter au démarrage automatique
    add_to_startup()
    
    # Démarrer le nettoyage automatique en arrière-plan
    threading.Thread(target=schedule_cleanup, daemon=True).start()

    # Créer l'icône système discrète
    icon = Icon("AutoCleaner")
    icon.icon = create_image()
    icon.menu = Menu(
        MenuItem("📊 Statistiques", lambda: threading.Thread(target=show_stats).start()),
        MenuItem("🧹 Nettoyer maintenant", lambda: threading.Thread(target=perform_cleanup).start()),
        MenuItem("❌ Quitter", quit_app)
    )
    
    # Lancer l'icône en mode silencieux
    icon.run()

if __name__ == "__main__":
    main()