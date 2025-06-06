import os
import sys
import time
import threading
import subprocess
import ctypes
import tempfile
from win10toast_persist import ToastNotifier
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font as tkFont
import datetime

# Initialisation
notifier = ToastNotifier()
deleted_files = 0
errors = 0
last_cleanup = None

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
        try:
            import win32gui
            import win32con
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
    global last_cleanup
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
    last_cleanup = datetime.datetime.now()
    
    # Notification discrète (plus courte)
    notifier.show_toast("AutoCleaner",
                        f"✅ {total} fichiers nettoyés",
                        duration=3, threaded=True)

def schedule_cleanup():
    while True:
        perform_cleanup()
        time.sleep(600)  # Toutes les 10 minutes (moins fréquent)

def format_file_size(size_bytes):
    """Convertit la taille en bytes vers un format lisible"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def get_disk_usage():
    """Récupère l'utilisation du disque système"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:\\")
        return {
            'total': format_file_size(total),
            'used': format_file_size(used),
            'free': format_file_size(free),
            'percent': round((used / total) * 100, 1)
        }
    except:
        return None

def load_logo():
    """Charge le logo depuis AutoCleanerLogo.ico ou .png"""
    logo_paths = [
        os.path.join(os.path.dirname(__file__), "AutoCleanerLogo.ico"),
        os.path.join(os.path.dirname(__file__), "AutoCleanerLogo.png"),
        os.path.join(os.getcwd(), "AutoCleanerLogo.ico"),
        os.path.join(os.getcwd(), "AutoCleanerLogo.png")
    ]
    
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                # Redimensionner pour l'interface
                img_resized = img.resize((48, 48), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img_resized)
            except Exception as e:
                print(f"Erreur lors du chargement du logo {logo_path}: {e}")
                continue
    
    return None

def show_stats():
    root = tk.Tk()
    root.title("AutoCleaner - Dashboard")
    root.geometry("550x650")
    root.resizable(False, False)
    root.configure(bg='#1e1e1e')  # Fond sombre moderne
    
    # Centrer la fenêtre
    root.eval('tk::PlaceWindow . center')
    
    # Style moderne
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Title.TLabel', background='#1e1e1e', foreground='#ffffff', font=('Segoe UI', 16, 'bold'))
    style.configure('Subtitle.TLabel', background='#1e1e1e', foreground='#b0b0b0', font=('Segoe UI', 10))
    style.configure('Stats.TLabel', background='#2d2d2d', foreground='#ffffff', font=('Segoe UI', 11))
    style.configure('Modern.TButton', font=('Segoe UI', 10))

    # Header avec logo amélioré
    header_frame = tk.Frame(root, bg='#1e1e1e', height=80)
    header_frame.pack(fill='x', padx=20, pady=(20, 10))
    header_frame.pack_propagate(False)
    
    # Charger le logo
    logo_tk = load_logo()
    
    if logo_tk:
        logo_label = tk.Label(header_frame, image=logo_tk, bg='#1e1e1e')
        logo_label.image = logo_tk  # Garder une référence
        logo_label.pack(side='left', padx=(0, 15))
    
    # Titre et sous-titre
    title_frame = tk.Frame(header_frame, bg='#1e1e1e')
    title_frame.pack(side='left', fill='y')
    
    title_label = tk.Label(title_frame, text="AutoCleaner", 
                          font=('Segoe UI', 18, 'bold'), 
                          fg='#00d4aa', bg='#1e1e1e')
    title_label.pack(anchor='w')
    
    subtitle_label = tk.Label(title_frame, text="Maintenance Système Intelligente", 
                             font=('Segoe UI', 9), 
                             fg='#888888', bg='#1e1e1e')
    subtitle_label.pack(anchor='w')
    
    # Status en temps réel
    status_frame = tk.Frame(root, bg='#2d2d2d', relief='solid', bd=1)
    status_frame.pack(fill='x', padx=20, pady=10)
    
    status_title = tk.Label(status_frame, text="🛡️ Status en Temps Réel", 
                           font=('Segoe UI', 12, 'bold'), 
                           fg='#00d4aa', bg='#2d2d2d')
    status_title.pack(pady=(10, 5))
    
    # Indicateur de protection
    protection_frame = tk.Frame(status_frame, bg='#2d2d2d')
    protection_frame.pack(fill='x', padx=15, pady=5)
    
    protection_indicator = tk.Label(protection_frame, text="●", 
                                   font=('Segoe UI', 20), 
                                   fg='#00ff00', bg='#2d2d2d')
    protection_indicator.pack(side='left')
    
    protection_text = tk.Label(protection_frame, text="Mode Discret Activé", 
                              font=('Segoe UI', 10), 
                              fg='#ffffff', bg='#2d2d2d')
    protection_text.pack(side='left', padx=(5, 0))
    
    # Dernier nettoyage
    if last_cleanup:
        last_clean_text = f"Dernier nettoyage: {last_cleanup.strftime('%H:%M:%S')}"
    else:
        last_clean_text = "Aucun nettoyage effectué"
    
    last_clean_label = tk.Label(status_frame, text=last_clean_text, 
                               font=('Segoe UI', 9), 
                               fg='#cccccc', bg='#2d2d2d')
    last_clean_label.pack(pady=(0, 10))

    # Statistiques principales
    stats_frame = tk.Frame(root, bg='#2d2d2d', relief='solid', bd=1)
    stats_frame.pack(fill='x', padx=20, pady=10)
    
    stats_title = tk.Label(stats_frame, text="📊 Statistiques de Nettoyage", 
                          font=('Segoe UI', 12, 'bold'), 
                          fg='#00d4aa', bg='#2d2d2d')
    stats_title.pack(pady=(10, 5))

    # Grid pour les stats
    stats_grid = tk.Frame(stats_frame, bg='#2d2d2d')
    stats_grid.pack(fill='x', padx=15, pady=10)
    
    # Fichiers supprimés
    files_frame = tk.Frame(stats_grid, bg='#3d3d3d', relief='solid', bd=1)
    files_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
    
    files_number = tk.Label(files_frame, text=str(deleted_files), 
                           font=('Segoe UI', 20, 'bold'), 
                           fg='#00d4aa', bg='#3d3d3d')
    files_number.pack(pady=(10, 0))
    
    files_label = tk.Label(files_frame, text="Fichiers\nSupprimés", 
                          font=('Segoe UI', 9), 
                          fg='#cccccc', bg='#3d3d3d')
    files_label.pack(pady=(0, 10))
    
    # Erreurs
    errors_frame = tk.Frame(stats_grid, bg='#3d3d3d', relief='solid', bd=1)
    errors_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
    
    errors_number = tk.Label(errors_frame, text=str(errors), 
                            font=('Segoe UI', 20, 'bold'), 
                            fg='#ff6b6b' if errors > 0 else '#00d4aa', bg='#3d3d3d')
    errors_number.pack(pady=(10, 0))
    
    errors_label = tk.Label(errors_frame, text="Erreurs\nRencontrées", 
                           font=('Segoe UI', 9), 
                           fg='#cccccc', bg='#3d3d3d')
    errors_label.pack(pady=(0, 10))

    # Informations système
    disk_info = get_disk_usage()
    if disk_info:
        disk_frame = tk.Frame(root, bg='#2d2d2d', relief='solid', bd=1)
        disk_frame.pack(fill='x', padx=20, pady=10)
        
        disk_title = tk.Label(disk_frame, text="💾 Espace Disque Système", 
                             font=('Segoe UI', 12, 'bold'), 
                             fg='#00d4aa', bg='#2d2d2d')
        disk_title.pack(pady=(10, 5))
        
        disk_details = tk.Label(disk_frame, 
                               text=f"Utilisé: {disk_info['used']} / {disk_info['total']} ({disk_info['percent']}%)\nDisponible: {disk_info['free']}", 
                               font=('Segoe UI', 10), 
                               fg='#ffffff', bg='#2d2d2d')
        disk_details.pack(pady=(0, 10))

    # Boutons d'action PLUS GRANDS
    buttons_frame = tk.Frame(root, bg='#1e1e1e')
    buttons_frame.pack(fill='x', padx=20, pady=20)

    def force_clean():
        # Animation de nettoyage
        clean_btn.configure(text="🧹 Nettoyage...", state='disabled')
        root.update()
        
        perform_cleanup()
        
        # Mettre à jour les affichages
        files_number.config(text=str(deleted_files))
        errors_number.config(text=str(errors), 
                            fg='#ff6b6b' if errors > 0 else '#00d4aa')
        
        if last_cleanup:
            last_clean_label.config(text=f"Dernier nettoyage: {last_cleanup.strftime('%H:%M:%S')}")
        
        clean_btn.configure(text="🧹 Nettoyer Maintenant", state='normal')
        
        # Notification de succès
        messagebox.showinfo("✅ Nettoyage Terminé", 
                           f"Nettoyage sécurisé terminé avec succès!\n\n"
                           f"Fichiers supprimés: {deleted_files}\n"
                           f"Erreurs: {errors}")

    # BOUTONS AGRANDIS avec plus de padding et taille de police plus grande
    clean_btn = tk.Button(buttons_frame, text="🧹 Nettoyer Maintenant", 
                         command=force_clean,
                         font=('Segoe UI', 12, 'bold'),  # Police plus grande
                         bg='#00d4aa', fg='white', 
                         relief='flat', 
                         padx=30, pady=15,  # Padding augmenté
                         cursor='hand2',
                         width=18)  # Largeur fixe
    clean_btn.pack(side='left', padx=(0, 15))
    
    close_btn = tk.Button(buttons_frame, text="❌ Fermer", 
                         command=root.destroy,
                         font=('Segoe UI', 12),  # Police plus grande
                         bg='#ff6b6b', fg='white',
                         relief='flat', 
                         padx=30, pady=15,  # Padding augmenté
                         cursor='hand2',
                         width=12)  # Largeur fixe
    close_btn.pack(side='right')

    # Footer
    footer_frame = tk.Frame(root, bg='#1e1e1e', height=40)
    footer_frame.pack(fill='x', side='bottom')
    footer_frame.pack_propagate(False)
    
    footer_label = tk.Label(footer_frame, text="AutoCleaner v2.0 - Protection Intelligente Activée", 
                           font=('Segoe UI', 8), 
                           fg='#666666', bg='#1e1e1e')
    footer_label.pack(expand=True)

    # Actualisation automatique toutes les 5 secondes
    def update_stats():
        if last_cleanup:
            last_clean_label.config(text=f"Dernier nettoyage: {last_cleanup.strftime('%H:%M:%S')}")
        root.after(5000, update_stats)
    
    update_stats()
    
    root.mainloop()

def create_image():
    """Crée l'icône pour la barre des tâches"""
    # Chercher d'abord le fichier de logo
    logo_paths = [
        os.path.join(os.path.dirname(__file__), "AutoCleanerLogo.ico"),
        os.path.join(os.path.dirname(__file__), "AutoCleanerLogo.png"),
        os.path.join(os.getcwd(), "AutoCleanerLogo.ico"),
        os.path.join(os.getcwd(), "AutoCleanerLogo.png")
    ]
    
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                return Image.open(logo_path).resize((64, 64), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Erreur lors du chargement du logo {logo_path}: {e}")
                continue
    
    # Créer une icône par défaut si aucun logo trouvé
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Design moderne avec dégradé simulé
    d.ellipse((8, 8, 56, 56), fill=(0, 212, 170, 200))  # Cercle principal
    d.ellipse((12, 12, 52, 52), fill=(0, 180, 140, 255))  # Cercle intérieur
    
    # Icône de nettoyage stylisée
    d.text((32, 32), "AC", fill=(255, 255, 255, 255), anchor="mm")
    
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
        MenuItem("📊 Dashboard", lambda: threading.Thread(target=show_stats).start()),
        MenuItem("🧹 Nettoyer maintenant", lambda: threading.Thread(target=perform_cleanup).start()),
        MenuItem("❌ Quitter", quit_app)
    )
    
    # Lancer l'icône en mode silencieux
    icon.run()

if __name__ == "__main__":
    main()