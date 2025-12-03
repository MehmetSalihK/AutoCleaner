import os
import sys
import time
import threading
import subprocess
import ctypes
import tempfile
import json
import webbrowser
from pathlib import Path
from win10toast_persist import ToastNotifier
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter import font as tkFont
import datetime

# Configuration et initialisation
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".autocleaner_config.json")
notifier = ToastNotifier()
deleted_files = 0
errors = 0
last_cleanup = None
total_space_freed = 0
cleanup_history = []

# Configuration par défaut
DEFAULT_CONFIG = {
    "auto_cleanup_interval": 600,  # 10 minutes
    "notifications_enabled": True,
    "deep_clean_enabled": False,
    "startup_enabled": True,
    "theme": "dark",
    "language": "fr"
}

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
    global last_cleanup, total_space_freed
    
    # Calculer l'espace avant nettoyage
    space_before = get_total_temp_size()
    
    temp1 = tempfile.gettempdir()
    temp2 = "C:\\Windows\\Temp"

    count1 = clear_temp_folder(temp1)
    count2 = clear_temp_folder(temp2)
    
    # Nettoyage sécurisé du cache navigateur
    clear_browser_cache_safe()
    
    # Nettoyage système limité
    clear_logs()
    clear_dns()

    # Calculer l'espace libéré
    space_after = get_total_temp_size()
    space_freed_this_session = max(0, space_before - space_after)
    total_space_freed += space_freed_this_session
    
    total = count1 + count2
    last_cleanup = datetime.datetime.now()
    
    # Charger la configuration pour les notifications
    config = load_config()
    if config.get('notifications_enabled', True):
        # Notification discrète améliorée
        notifier.show_toast("AutoCleaner Pro",
                            f"✅ {total} fichiers nettoyés\n💾 {format_file_size(space_freed_this_session)} libérés",
                            duration=4, threaded=True)

def get_total_temp_size():
    """Calcule la taille totale des fichiers temporaires"""
    total_size = 0
    temp_dirs = [tempfile.gettempdir(), "C:\\Windows\\Temp"]
    
    for temp_dir in temp_dirs:
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        if not is_path_excluded(file_path) and not is_important_file(file_path):
                            total_size += os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            continue
    
    return total_size

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

def load_config():
    """Charge la configuration depuis le fichier JSON"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Sauvegarde la configuration dans le fichier JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def get_system_info():
    """Récupère les informations système détaillées"""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': format_file_size(memory.available)
        }
    except ImportError:
        return None

def show_stats():
    config = load_config()
    
    root = tk.Tk()
    root.title("AutoCleaner - Dashboard Avancé")
    root.geometry("700x800")
    root.resizable(True, True)
    root.minsize(600, 700)
    
    # Thème adaptatif
    if config.get('theme') == 'dark':
        bg_color = '#1e1e1e'
        card_color = '#2d2d2d'
        accent_color = '#00d4aa'
        text_color = '#ffffff'
        secondary_text = '#b0b0b0'
    else:
        bg_color = '#f5f5f5'
        card_color = '#ffffff'
        accent_color = '#007acc'
        text_color = '#333333'
        secondary_text = '#666666'
    
    root.configure(bg=bg_color)
    
    # Centrer la fenêtre
    root.eval('tk::PlaceWindow . center')
    
    # Style moderne adaptatif
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Title.TLabel', background=bg_color, foreground=text_color, font=('Segoe UI', 16, 'bold'))
    style.configure('Subtitle.TLabel', background=bg_color, foreground=secondary_text, font=('Segoe UI', 10))
    style.configure('Stats.TLabel', background=card_color, foreground=text_color, font=('Segoe UI', 11))
    style.configure('Modern.TButton', font=('Segoe UI', 10))
    
    # Scrollable main frame
    main_canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
    scrollable_frame = tk.Frame(main_canvas, bg=bg_color)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)
    
    main_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Header avec logo amélioré
    header_frame = tk.Frame(scrollable_frame, bg=bg_color, height=100)
    header_frame.pack(fill='x', padx=20, pady=(20, 10))
    header_frame.pack_propagate(False)
    
    # Charger le logo
    logo_tk = load_logo()
    
    if logo_tk:
        logo_label = tk.Label(header_frame, image=logo_tk, bg=bg_color)
        logo_label.image = logo_tk  # Garder une référence
        logo_label.pack(side='left', padx=(0, 15))
    
    # Titre et sous-titre
    title_frame = tk.Frame(header_frame, bg=bg_color)
    title_frame.pack(side='left', fill='y')
    
    title_label = tk.Label(title_frame, text="AutoCleaner Pro", 
                          font=('Segoe UI', 20, 'bold'), 
                          fg=accent_color, bg=bg_color)
    title_label.pack(anchor='w')
    
    subtitle_label = tk.Label(title_frame, text="Maintenance Système Intelligente & Sécurisée", 
                             font=('Segoe UI', 10), 
                             fg=secondary_text, bg=bg_color)
    subtitle_label.pack(anchor='w')
    
    # Bouton paramètres dans le header
    settings_btn = tk.Button(header_frame, text="⚙️", 
                            font=('Segoe UI', 16),
                            bg=card_color, fg=text_color,
                            relief='flat', bd=0,
                            padx=10, pady=5,
                            cursor='hand2',
                            command=lambda: show_settings(root, config))
    settings_btn.pack(side='right', padx=(0, 10))
    
    # Status en temps réel avec design amélioré
    status_frame = tk.Frame(scrollable_frame, bg=card_color, relief='solid', bd=1)
    status_frame.pack(fill='x', padx=20, pady=10)
    
    status_title = tk.Label(status_frame, text="🛡️ Status en Temps Réel", 
                           font=('Segoe UI', 14, 'bold'), 
                           fg=accent_color, bg=card_color)
    status_title.pack(pady=(15, 10))
    
    # Indicateurs de status avec grid layout
    status_grid = tk.Frame(status_frame, bg=card_color)
    status_grid.pack(fill='x', padx=15, pady=10)
    
    # Protection status
    protection_frame = tk.Frame(status_grid, bg=card_color)
    protection_frame.pack(fill='x', pady=5)
    
    protection_indicator = tk.Label(protection_frame, text="●", 
                                   font=('Segoe UI', 16), 
                                   fg='#00ff00', bg=card_color)
    protection_indicator.pack(side='left')
    
    protection_text = tk.Label(protection_frame, text="Protection Active - Mode Intelligent", 
                              font=('Segoe UI', 11, 'bold'), 
                              fg=text_color, bg=card_color)
    protection_text.pack(side='left', padx=(8, 0))
    
    # Informations système en temps réel
    system_info = get_system_info()
    if system_info:
        sys_info_frame = tk.Frame(status_grid, bg=card_color)
        sys_info_frame.pack(fill='x', pady=5)
        
        cpu_label = tk.Label(sys_info_frame, 
                             text=f"CPU: {system_info['cpu_usage']:.1f}%", 
                             font=('Segoe UI', 9), 
                             fg=secondary_text, bg=card_color)
        cpu_label.pack(side='left')
        
        memory_label = tk.Label(sys_info_frame, 
                               text=f"RAM: {system_info['memory_usage']:.1f}% | Disponible: {system_info['memory_available']}", 
                               font=('Segoe UI', 9), 
                               fg=secondary_text, bg=card_color)
        memory_label.pack(side='left', padx=(20, 0))
    
    # Dernier nettoyage avec plus d'informations
    cleanup_info_frame = tk.Frame(status_grid, bg=card_color)
    cleanup_info_frame.pack(fill='x', pady=(10, 15))
    
    if last_cleanup:
        last_clean_text = f"Dernier nettoyage: {last_cleanup.strftime('%d/%m/%Y à %H:%M:%S')}"
        time_diff = datetime.datetime.now() - last_cleanup
        if time_diff.seconds < 3600:
            time_ago = f"il y a {time_diff.seconds // 60} minutes"
        else:
            time_ago = f"il y a {time_diff.seconds // 3600} heures"
        last_clean_text += f" ({time_ago})"
    else:
        last_clean_text = "Aucun nettoyage effectué depuis le démarrage"
    
    last_clean_label = tk.Label(cleanup_info_frame, text=last_clean_text, 
                               font=('Segoe UI', 10), 
                               fg=secondary_text, bg=card_color)
    last_clean_label.pack(anchor='w')
    
    if total_space_freed > 0:
        space_freed_label = tk.Label(cleanup_info_frame, 
                                    text=f"Espace total libéré: {format_file_size(total_space_freed)}", 
                                    font=('Segoe UI', 9), 
                                    fg=accent_color, bg=card_color)
        space_freed_label.pack(anchor='w', pady=(2, 0))

    # Statistiques principales avec design en cartes
    stats_frame = tk.Frame(scrollable_frame, bg=card_color, relief='solid', bd=1)
    stats_frame.pack(fill='x', padx=20, pady=10)
    
    stats_title = tk.Label(stats_frame, text="📊 Statistiques de Performance", 
                          font=('Segoe UI', 14, 'bold'), 
                          fg=accent_color, bg=card_color)
    stats_title.pack(pady=(15, 10))

    # Grid pour les stats avec design moderne
    stats_grid = tk.Frame(stats_frame, bg=card_color)
    stats_grid.pack(fill='x', padx=15, pady=10)
    
    # Configuration du grid
    stats_grid.grid_columnconfigure(0, weight=1)
    stats_grid.grid_columnconfigure(1, weight=1)
    stats_grid.grid_columnconfigure(2, weight=1)
    
    # Fichiers supprimés
    files_frame = tk.Frame(stats_grid, bg=bg_color, relief='solid', bd=2)
    files_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    
    files_icon = tk.Label(files_frame, text="🗑️", font=('Segoe UI', 24), bg=bg_color)
    files_icon.pack(pady=(15, 5))
    
    files_number = tk.Label(files_frame, text=str(deleted_files), 
                           font=('Segoe UI', 24, 'bold'), 
                           fg=accent_color, bg=bg_color)
    files_number.pack()
    
    files_label = tk.Label(files_frame, text="Fichiers\nSupprimés", 
                          font=('Segoe UI', 10), 
                          fg=text_color, bg=bg_color)
    files_label.pack(pady=(5, 15))
    
    # Espace libéré
    space_frame = tk.Frame(stats_grid, bg=bg_color, relief='solid', bd=2)
    space_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    
    space_icon = tk.Label(space_frame, text="💾", font=('Segoe UI', 24), bg=bg_color)
    space_icon.pack(pady=(15, 5))
    
    space_number = tk.Label(space_frame, text=format_file_size(total_space_freed), 
                           font=('Segoe UI', 18, 'bold'), 
                           fg=accent_color, bg=bg_color)
    space_number.pack()
    
    space_label = tk.Label(space_frame, text="Espace\nLibéré", 
                          font=('Segoe UI', 10), 
                          fg=text_color, bg=bg_color)
    space_label.pack(pady=(5, 15))
    
    # Erreurs
    errors_frame = tk.Frame(stats_grid, bg=bg_color, relief='solid', bd=2)
    errors_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
    
    error_icon = tk.Label(errors_frame, text="⚠️" if errors > 0 else "✅", 
                         font=('Segoe UI', 24), bg=bg_color)
    error_icon.pack(pady=(15, 5))
    
    errors_number = tk.Label(errors_frame, text=str(errors), 
                            font=('Segoe UI', 24, 'bold'), 
                            fg='#ff6b6b' if errors > 0 else '#00ff00', bg=bg_color)
    errors_number.pack()
    
    errors_label = tk.Label(errors_frame, text="Erreurs\nRencontrées", 
                           font=('Segoe UI', 10), 
                           fg=text_color, bg=bg_color)
    errors_label.pack(pady=(5, 15))

    # Informations système avec graphique de progression
    disk_info = get_disk_usage()
    if disk_info:
        disk_frame = tk.Frame(scrollable_frame, bg=card_color, relief='solid', bd=1)
        disk_frame.pack(fill='x', padx=20, pady=10)
        
        disk_title = tk.Label(disk_frame, text="💾 Espace Disque Système", 
                             font=('Segoe UI', 14, 'bold'), 
                             fg=accent_color, bg=card_color)
        disk_title.pack(pady=(15, 10))
        
        # Barre de progression pour l'espace disque
        progress_frame = tk.Frame(disk_frame, bg=card_color)
        progress_frame.pack(fill='x', padx=15, pady=10)
        
        progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        progress_bar['value'] = disk_info['percent']
        progress_bar.pack(pady=5)
        
        disk_details = tk.Label(progress_frame, 
                               text=f"Utilisé: {disk_info['used']} / {disk_info['total']} ({disk_info['percent']}%) | Disponible: {disk_info['free']}", 
                               font=('Segoe UI', 10),
                               fg=text_color, bg=card_color)
        disk_details.pack(pady=(5, 15))
    
    # Historique des nettoyages
    if cleanup_history:
        history_frame = tk.Frame(scrollable_frame, bg=card_color, relief='solid', bd=1)
        history_frame.pack(fill='x', padx=20, pady=10)
        
        history_title = tk.Label(history_frame, text="📈 Historique des Nettoyages", 
                                font=('Segoe UI', 14, 'bold'), 
                                fg=accent_color, bg=card_color)
        history_title.pack(pady=(15, 10))
        
        # Afficher les 5 derniers nettoyages
        for i, cleanup in enumerate(cleanup_history[-5:]):
            cleanup_item = tk.Label(history_frame, 
                                   text=f"• {cleanup['date']} - {cleanup['files']} fichiers ({cleanup['size']})", 
                                   font=('Segoe UI', 9), 
                                   fg=secondary_text, bg=card_color)
            cleanup_item.pack(anchor='w', padx=15, pady=2)
        
        tk.Label(history_frame, text="", bg=card_color).pack(pady=5)  # Espacement

    # Boutons d'action modernes avec design amélioré
    buttons_frame = tk.Frame(scrollable_frame, bg=bg_color)
    buttons_frame.pack(fill='x', padx=20, pady=20)

    def force_clean():
        # Animation de nettoyage avec progress
        clean_btn.configure(text="🧹 Nettoyage en cours...", state='disabled')
        progress_btn.configure(text="⏳ Analyse...")
        root.update()
        
        # Sauvegarder l'état avant nettoyage
        files_before = deleted_files
        
        perform_cleanup()
        
        # Calculer les fichiers nettoyés dans cette session
        files_cleaned = deleted_files - files_before
        
        # Ajouter à l'historique
        cleanup_entry = {
            'date': datetime.datetime.now().strftime('%d/%m %H:%M'),
            'files': files_cleaned,
            'size': format_file_size(total_space_freed)
        }
        cleanup_history.append(cleanup_entry)
        
        # Mettre à jour les affichages
        files_number.config(text=str(deleted_files))
        space_number.config(text=format_file_size(total_space_freed))
        errors_number.config(text=str(errors), 
                            fg='#ff6b6b' if errors > 0 else '#00ff00')
        error_icon.config(text="⚠️" if errors > 0 else "✅")
        
        if last_cleanup:
            time_diff = datetime.datetime.now() - last_cleanup
            if time_diff.seconds < 3600:
                time_ago = f"il y a {time_diff.seconds // 60} minutes"
            else:
                time_ago = f"il y a {time_diff.seconds // 3600} heures"
            last_clean_label.config(text=f"Dernier nettoyage: {last_cleanup.strftime('%d/%m/%Y à %H:%M:%S')} ({time_ago})")
        
        clean_btn.configure(text="🧹 Nettoyer Maintenant", state='normal')
        progress_btn.configure(text="📊 Analyse Terminée")
        
        # Notification de succès améliorée
        if files_cleaned > 0:
            messagebox.showinfo("✅ Nettoyage Terminé", 
                               f"Nettoyage intelligent terminé avec succès!\n\n"
                               f"📁 Fichiers supprimés: {files_cleaned}\n"
                               f"💾 Espace libéré: {format_file_size(total_space_freed)}\n"
                               f"⚠️ Erreurs: {errors}\n\n"
                               f"Votre système est maintenant optimisé!")
        else:
            messagebox.showinfo("ℹ️ Nettoyage Terminé", 
                               "Aucun fichier temporaire trouvé.\n\n"
                               "Votre système est déjà optimisé!")

    # Grid pour organiser les boutons
    buttons_frame.grid_columnconfigure(0, weight=1)
    buttons_frame.grid_columnconfigure(1, weight=1)
    buttons_frame.grid_columnconfigure(2, weight=1)
    buttons_frame.grid_columnconfigure(3, weight=1)
    
    # Bouton nettoyage principal
    clean_btn = tk.Button(buttons_frame, text="🧹 Nettoyer Maintenant", 
                         command=force_clean,
                         font=('Segoe UI', 12, 'bold'),
                         bg=accent_color, fg='white', 
                         relief='flat', bd=0,
                         padx=20, pady=12,
                         cursor='hand2')
    clean_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    
    # Bouton analyse
    def quick_analysis():
        progress_btn.configure(text="🔍 Analyse...")
        root.update()
        # Simulation d'analyse rapide
        temp_size = sum(os.path.getsize(os.path.join(tempfile.gettempdir(), f)) 
                       for f in os.listdir(tempfile.gettempdir()) 
                       if os.path.isfile(os.path.join(tempfile.gettempdir(), f)))
        progress_btn.configure(text="📊 Analyser")
        messagebox.showinfo("📊 Analyse Rapide", 
                           f"Fichiers temporaires détectés: ~{format_file_size(temp_size)}\n\n"
                           f"Recommandation: {'Nettoyage conseillé' if temp_size > 100*1024*1024 else 'Système propre'}")
    
    progress_btn = tk.Button(buttons_frame, text="📊 Analyser", 
                            command=quick_analysis,
                            font=('Segoe UI', 11),
                            bg=card_color, fg=text_color, 
                            relief='solid', bd=1,
                            padx=20, pady=12,
                            cursor='hand2')
    progress_btn.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    
    # Bouton planification
    def show_scheduler():
        messagebox.showinfo("⏰ Planification", 
                           f"Nettoyage automatique: {'Activé' if config.get('startup_enabled') else 'Désactivé'}\n"
                           f"Intervalle: {config.get('auto_cleanup_interval', 600)//60} minutes\n\n"
                           f"Utilisez les paramètres pour modifier la planification.")
    
    schedule_btn = tk.Button(buttons_frame, text="⏰ Planifier", 
                            command=show_scheduler,
                            font=('Segoe UI', 11),
                            bg=card_color, fg=text_color, 
                            relief='solid', bd=1,
                            padx=20, pady=12,
                            cursor='hand2')
    schedule_btn.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
    
    # Bouton fermer
    close_btn = tk.Button(buttons_frame, text="❌ Fermer", 
                         command=root.destroy,
                         font=('Segoe UI', 11),
                         bg='#ff6b6b', fg='white',
                         relief='flat', bd=0,
                         padx=20, pady=12,
                         cursor='hand2')
    close_btn.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

    # Footer moderne
    footer_frame = tk.Frame(scrollable_frame, bg=bg_color, height=50)
    footer_frame.pack(fill='x', pady=(20, 0))
    footer_frame.pack_propagate(False)
    
    footer_content = tk.Frame(footer_frame, bg=bg_color)
    footer_content.pack(expand=True, fill='both')
    
    # Ligne de séparation
    separator = tk.Frame(footer_content, bg=secondary_text, height=1)
    separator.pack(fill='x', padx=20, pady=(10, 15))
    
    footer_info = tk.Frame(footer_content, bg=bg_color)
    footer_info.pack(expand=True)
    
    version_label = tk.Label(footer_info, text="AutoCleaner Pro v3.0", 
                           font=('Segoe UI', 9, 'bold'), 
                           fg=accent_color, bg=bg_color)
    version_label.pack(side='left', padx=(20, 0))
    
    status_label = tk.Label(footer_info, text="Protection Intelligente Activée 🛡️", 
                           font=('Segoe UI', 8), 
                           fg=secondary_text, bg=bg_color)
    status_label.pack(side='right', padx=(0, 20))

    # Actualisation automatique toutes les 5 secondes
    def update_stats():
        if last_cleanup:
            time_diff = datetime.datetime.now() - last_cleanup
            if time_diff.seconds < 3600:
                time_ago = f"il y a {time_diff.seconds // 60} minutes"
            else:
                time_ago = f"il y a {time_diff.seconds // 3600} heures"
            last_clean_label.config(text=f"Dernier nettoyage: {last_cleanup.strftime('%d/%m/%Y à %H:%M:%S')} ({time_ago})")
        
        # Mettre à jour les informations système
        system_info = get_system_info()
        if system_info:
            try:
                cpu_label.config(text=f"CPU: {system_info['cpu_usage']:.1f}%")
                memory_label.config(text=f"RAM: {system_info['memory_usage']:.1f}% | Disponible: {system_info['memory_available']}")
            except:
                pass
        
        root.after(5000, update_stats)
    
    update_stats()
    
    # Gestion du scroll avec la molette
    def on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    main_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    root.mainloop()

def show_settings(parent, current_config):
    """Affiche la fenêtre de paramètres"""
    settings_window = tk.Toplevel(parent)
    settings_window.title("AutoCleaner - Paramètres")
    settings_window.geometry("500x600")
    settings_window.resizable(False, False)
    settings_window.configure(bg='#1e1e1e')
    
    # Centrer la fenêtre
    settings_window.transient(parent)
    settings_window.grab_set()
    
    # Variables de configuration
    auto_cleanup_var = tk.BooleanVar(value=current_config.get('startup_enabled', True))
    notifications_var = tk.BooleanVar(value=current_config.get('notifications_enabled', True))
    deep_clean_var = tk.BooleanVar(value=current_config.get('deep_clean_enabled', False))
    interval_var = tk.IntVar(value=current_config.get('auto_cleanup_interval', 600) // 60)
    theme_var = tk.StringVar(value=current_config.get('theme', 'dark'))
    
    # Header
    header = tk.Label(settings_window, text="⚙️ Paramètres AutoCleaner", 
                     font=('Segoe UI', 16, 'bold'), 
                     fg='#00d4aa', bg='#1e1e1e')
    header.pack(pady=(20, 30))
    
    # Section Nettoyage Automatique
    auto_frame = tk.LabelFrame(settings_window, text="🔄 Nettoyage Automatique", 
                              font=('Segoe UI', 12, 'bold'),
                              fg='#ffffff', bg='#2d2d2d', bd=2)
    auto_frame.pack(fill='x', padx=20, pady=10)
    
    tk.Checkbutton(auto_frame, text="Activer le nettoyage automatique au démarrage", 
                  variable=auto_cleanup_var, 
                  font=('Segoe UI', 10),
                  fg='#ffffff', bg='#2d2d2d', 
                  selectcolor='#2d2d2d').pack(anchor='w', padx=15, pady=10)
    
    interval_frame = tk.Frame(auto_frame, bg='#2d2d2d')
    interval_frame.pack(fill='x', padx=15, pady=(0, 15))
    
    tk.Label(interval_frame, text="Intervalle de nettoyage (minutes):", 
            font=('Segoe UI', 10), fg='#ffffff', bg='#2d2d2d').pack(side='left')
    
    interval_spinbox = tk.Spinbox(interval_frame, from_=5, to=1440, 
                                 textvariable=interval_var, width=10,
                                 font=('Segoe UI', 10))
    interval_spinbox.pack(side='right', padx=(10, 0))
    
    # Section Interface
    ui_frame = tk.LabelFrame(settings_window, text="🎨 Interface", 
                            font=('Segoe UI', 12, 'bold'),
                            fg='#ffffff', bg='#2d2d2d', bd=2)
    ui_frame.pack(fill='x', padx=20, pady=10)
    
    tk.Checkbutton(ui_frame, text="Activer les notifications", 
                  variable=notifications_var, 
                  font=('Segoe UI', 10),
                  fg='#ffffff', bg='#2d2d2d', 
                  selectcolor='#2d2d2d').pack(anchor='w', padx=15, pady=10)
    
    theme_frame = tk.Frame(ui_frame, bg='#2d2d2d')
    theme_frame.pack(fill='x', padx=15, pady=(0, 15))
    
    tk.Label(theme_frame, text="Thème:", 
            font=('Segoe UI', 10), fg='#ffffff', bg='#2d2d2d').pack(side='left')
    
    theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, 
                              values=['dark', 'light'], state='readonly', width=10)
    theme_combo.pack(side='right', padx=(10, 0))
    
    # Section Avancé
    advanced_frame = tk.LabelFrame(settings_window, text="🔧 Options Avancées", 
                                  font=('Segoe UI', 12, 'bold'),
                                  fg='#ffffff', bg='#2d2d2d', bd=2)
    advanced_frame.pack(fill='x', padx=20, pady=10)
    
    tk.Checkbutton(advanced_frame, text="Nettoyage en profondeur (plus agressif)", 
                  variable=deep_clean_var, 
                  font=('Segoe UI', 10),
                  fg='#ffffff', bg='#2d2d2d', 
                  selectcolor='#2d2d2d').pack(anchor='w', padx=15, pady=10)
    
    warning_label = tk.Label(advanced_frame, 
                           text="⚠️ Le nettoyage en profondeur peut supprimer des fichiers importants", 
                           font=('Segoe UI', 8), fg='#ff6b6b', bg='#2d2d2d')
    warning_label.pack(anchor='w', padx=15, pady=(0, 15))
    
    # Boutons
    buttons_frame = tk.Frame(settings_window, bg='#1e1e1e')
    buttons_frame.pack(fill='x', padx=20, pady=20)
    
    def save_settings():
        new_config = {
            'auto_cleanup_interval': interval_var.get() * 60,
            'notifications_enabled': notifications_var.get(),
            'deep_clean_enabled': deep_clean_var.get(),
            'startup_enabled': auto_cleanup_var.get(),
            'theme': theme_var.get(),
            'language': current_config.get('language', 'fr')
        }
        save_config(new_config)
        messagebox.showinfo("✅ Paramètres", "Paramètres sauvegardés avec succès!\n\nRedémarrez l'application pour appliquer tous les changements.")
        settings_window.destroy()
    
    def reset_settings():
        if messagebox.askyesno("🔄 Réinitialiser", "Voulez-vous vraiment réinitialiser tous les paramètres?"):
            save_config(DEFAULT_CONFIG)
            messagebox.showinfo("✅ Réinitialisation", "Paramètres réinitialisés aux valeurs par défaut.")
            settings_window.destroy()
    
    save_btn = tk.Button(buttons_frame, text="💾 Sauvegarder", 
                        command=save_settings,
                        font=('Segoe UI', 11, 'bold'),
                        bg='#00d4aa', fg='white', 
                        relief='flat', padx=20, pady=10,
                        cursor='hand2')
    save_btn.pack(side='left', padx=(0, 10))
    
    reset_btn = tk.Button(buttons_frame, text="🔄 Réinitialiser", 
                         command=reset_settings,
                         font=('Segoe UI', 11),
                         bg='#ff6b6b', fg='white', 
                         relief='flat', padx=20, pady=10,
                         cursor='hand2')
    reset_btn.pack(side='left', padx=(0, 10))
    
    cancel_btn = tk.Button(buttons_frame, text="❌ Annuler", 
                          command=settings_window.destroy,
                          font=('Segoe UI', 11),
                          bg='#666666', fg='white', 
                          relief='flat', padx=20, pady=10,
                          cursor='hand2')
    cancel_btn.pack(side='right')

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

def schedule_cleanup_with_config():
    """Nettoyage automatique basé sur la configuration"""
    while True:
        config = load_config()
        interval = config.get('auto_cleanup_interval', 600)
        
        if config.get('startup_enabled', True):
            perform_cleanup()
        
        time.sleep(interval)

def main():
    # Cacher la console dès le démarrage
    hide_console()
    
    # Charger la configuration
    config = load_config()
    
    if not is_admin():
        # Relancer en mode admin mais de façon discrète
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 0)
        return

    # Notification de démarrage basée sur la configuration
    if config.get('notifications_enabled', True):
        notifier.show_toast("AutoCleaner Pro", 
                            "🛡️ Protection intelligente activée\n⚙️ Cliquez sur l'icône pour accéder au dashboard", 
                            duration=3, threaded=True)

    # Ajouter au démarrage automatique si activé
    if config.get('startup_enabled', True):
        add_to_startup()
    
    # Démarrer le nettoyage automatique en arrière-plan
    threading.Thread(target=schedule_cleanup_with_config, daemon=True).start()

    # Créer l'icône système avec menu amélioré
    icon = Icon("AutoCleaner Pro")
    icon.icon = create_image()
    icon.menu = Menu(
        MenuItem("📊 Dashboard Avancé", lambda: threading.Thread(target=show_stats).start()),
        MenuItem("🧹 Nettoyer Maintenant", lambda: threading.Thread(target=perform_cleanup).start()),
        Menu.SEPARATOR,
        MenuItem("⚙️ Paramètres", lambda: threading.Thread(target=lambda: show_settings(None, config)).start()),
        MenuItem("📈 Statistiques", lambda: threading.Thread(target=show_quick_stats).start()),
        Menu.SEPARATOR,
        MenuItem("ℹ️ À Propos", lambda: show_about()),
        MenuItem("❌ Quitter", quit_app)
    )
    
    # Lancer l'icône en mode silencieux
    icon.run()

def show_quick_stats():
    """Affiche des statistiques rapides dans une popup"""
    stats_text = f"""📊 AutoCleaner Pro - Statistiques Rapides

🗑️ Fichiers supprimés: {deleted_files}
💾 Espace total libéré: {format_file_size(total_space_freed)}
⚠️ Erreurs rencontrées: {errors}

📅 Dernier nettoyage: {last_cleanup.strftime('%d/%m/%Y à %H:%M:%S') if last_cleanup else 'Aucun'}
🔄 Nettoyages effectués: {len(cleanup_history)}

🛡️ Protection: Active
⚡ Performance: {'Optimale' if errors == 0 else 'Attention requise'}"""
    
    messagebox.showinfo("📊 Statistiques Rapides", stats_text)

def show_about():
    """Affiche les informations sur l'application"""
    about_text = f"""🛡️ AutoCleaner Pro v3.0

🔧 Nettoyage intelligent et sécurisé
💾 Optimisation système automatique
🎨 Interface moderne et intuitive
⚙️ Configuration avancée

📊 Statistiques actuelles:
• Fichiers nettoyés: {deleted_files}
• Espace libéré: {format_file_size(total_space_freed)}
• Uptime: {datetime.datetime.now().strftime('%H:%M:%S')}

🛡️ Protection intelligente activée
✅ Système optimisé et sécurisé

© 2024 AutoCleaner Pro - Maintenance Système"""
    
    messagebox.showinfo("ℹ️ À Propos d'AutoCleaner Pro", about_text)

if __name__ == "__main__":
    main()