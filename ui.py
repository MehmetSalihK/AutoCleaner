import webbrowser
import customtkinter as ctk
import threading
import time
from PIL import Image
import pystray
from pystray import MenuItem as item

from config import load_config, save_config, APP_NAME, VERSION
from utils import load_logo, format_file_size
from monitor import get_system_info
from ui_components import StatCard, ToggleCard, ModernButton, FeedbackDialog
from logs import logger
from tools import ProcessManager, StartupManager, AppManager, SystemInfo, SystemOptimizer, DiskAnalyzer

ctk.set_default_color_theme("blue")

class ModernApp(ctk.CTk):
    def __init__(self, cleaner_instance, on_close_callback):
        super().__init__()
        self.cleaner = cleaner_instance
        self.on_close_callback = on_close_callback
        
        try:
            self.config = load_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {}

        # Window Configuration
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1200x800")
        self.minsize(1100, 750)
        
        # Set Window Icon
        try:
            self.iconbitmap("AutoCleanerLogo.ico")
        except:
            pass
        
        try:
            self.set_theme(self.config.get("theme", "dark"))
        except:
            ctk.set_appearance_mode("Dark")

        # Main Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        try:
            self.create_sidebar()
            self.create_content_area()
            self.update_stats_loop()
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
        except Exception as e:
            logger.error(f"Failed to create UI: {e}")
            raise

    def open_feedback(self):
        """Open feedback dialog."""
        FeedbackDialog(self)

    def set_theme(self, theme_mode):
        if theme_mode.lower() == "system":
            ctk.set_appearance_mode("System")
        elif theme_mode.lower() == "light":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def create_sidebar(self):
        print("Creating sidebar...")
        # Modern Sidebar with Gradient Effect
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=("#e8eef5", "#1a1a2e"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Logo Section
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(40, 20), sticky="ew")
        
        try:
            # Load Logo Image
            img = Image.open("AutoCleanerLogo.ico")
            logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
            
            ctk.CTkLabel(
                logo_frame, 
                text="", 
                image=logo_img
            ).pack(pady=(0, 10))
        except:
            # Fallback
            ctk.CTkLabel(
                logo_frame, 
                text="🛡️", 
                font=("Segoe UI", 60)
            ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            logo_frame, 
            text=APP_NAME, 
            font=("Segoe UI", 22, "bold"),
            text_color=("#1a1a2e", "#00d4aa")
        ).pack()
        
        ctk.CTkLabel(
            logo_frame, 
            text="Professional Edition", 
            font=("Segoe UI", 11),
            text_color="gray"
        ).pack()

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊", "Tableau de Bord"),
            ("cleaner", "🧹", "Nettoyage"),
            ("tools", "🛠️", "Outils"),
            ("logs", "📜", "Historique"),
            ("settings", "⚙️", "Paramètres")
        ]
        
        for i, (key, icon, text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {text}",
                height=55,
                corner_radius=12,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("#d0d9e5", "#2a2a3e"),
                anchor="w",

                font=("Segoe UI", 16, "bold"),
                command=lambda k=key: self.show_view(k)
            )
            btn.grid(row=i+1, column=0, padx=15, pady=8, sticky="ew")
            self.nav_buttons[key] = btn

            self.nav_buttons[key] = btn
            
        # Feedback Button (CTA)
        ctk.CTkButton(
            self.sidebar,
            text="✉️  Donner votre Avis",
            height=45,
            corner_radius=22,
            fg_color=("#e0e0e0", "#252535"),
            text_color=("#333", "#fff"),
            border_width=1,
            border_color=("#ccc", "#3a3a4e"),
            hover_color=("#d0d9e5", "#303045"),
            anchor="center",
            font=("Segoe UI", 13, "bold"),
            command=self.open_feedback
        ).grid(row=6, column=0, padx=25, pady=(30, 0), sticky="ew")

        # Version Footer
        version_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        version_frame.grid(row=7, column=0, pady=20)
        ctk.CTkLabel(
            version_frame, 
            text=f"Version {VERSION}", 
            text_color="gray",
            font=("Segoe UI", 10)
        ).pack()

    def create_content_area(self):
        print("Creating content area...")
        # Content Area with Modern Background
        self.content = ctk.CTkFrame(
            self, 
            corner_radius=0, 
            fg_color=("#f5f7fa", "#0f0f1e")
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Create Views
        self.views = {
            "dashboard": DashboardView(self.content, self.cleaner),
            "cleaner": CleanerView(self.content, self.cleaner),
            "tools": ToolsView(self.content),
            "logs": LogsView(self.content),
            "settings": SettingsView(self.content, self.config, self.save_config)
        }
        self.show_view("dashboard")

    def show_view(self, name):
        for view in self.views.values():
            view.pack_forget()
        
        for k, btn in self.nav_buttons.items():
            if k == name:
                btn.configure(fg_color=("#00d4aa", "#00d4aa"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        
        self.views[name].pack(fill="both", expand=True, padx=30, pady=30)

    def save_config(self):
        save_config(self.config)

    def update_stats_loop(self):
        try:
            if hasattr(self, 'views') and "dashboard" in self.views:
                if isinstance(self.views["dashboard"], DashboardView):
                    self.views["dashboard"].update_stats()
        except Exception as e:
            logger.error(f"Stats update failed: {e}")
        
        try:
            self.after(2000, self.update_stats_loop)
        except:
            pass

    def on_closing(self):
        if self.config.get("minimize_to_tray", True):
            self.withdraw()
            from utils import show_notification
            show_notification(
                "AutoCleaner Demo",
                "L'application continue en arrière-plan. Cliquez sur l'icône dans la barre des tâches pour l'ouvrir.",
                duration=3
            )
        else:
            self.on_close_callback()

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, cleaner):
        super().__init__(parent, fg_color="transparent")
        self.cleaner = cleaner
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))
        
        ctk.CTkLabel(
            header, 
            text="Tableau de Bord", 
            font=("Segoe UI", 42, "bold"),
            text_color=("#1a1a2e", "#ffffff")
        ).pack(side="left")
        
        # Status Badge
        status_badge = ctk.CTkFrame(header, corner_radius=20, fg_color=("#00d4aa", "#00d4aa"))
        status_badge.pack(side="right", padx=10)
        ctk.CTkLabel(
            status_badge,
            text="🛡️ Système Protégé",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        ).pack(padx=20, pady=10)

        # Stats Grid (4 Cards)
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="x", pady=(0, 25))
        self.grid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.cards = {
            "cpu": StatCard(self.grid_frame, "CPU", "🧠", "#667eea"),
            "ram": StatCard(self.grid_frame, "RAM", "💾", "#764ba2"),
            "disk": StatCard(self.grid_frame, "Disque", "💿", "#f093fb"),
            "gpu": StatCard(self.grid_frame, "GPU", "🎮", "#4facfe")
        }
        
        for i, (k, card) in enumerate(self.cards.items()):
            card.grid(row=0, column=i, padx=8, sticky="ew")

        # Bottom Section (2 Columns)
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="both", expand=True)
        bottom.grid_columnconfigure((0, 1), weight=1)

        # Network Card
        net_card = ctk.CTkFrame(bottom, corner_radius=20, fg_color=("#ffffff", "#1a1a2e"))
        net_card.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        
        ctk.CTkLabel(
            net_card, 
            text="📡 Réseau", 
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 15))
        
        self.net_label = ctk.CTkLabel(
            net_card, 
            text="⬇️ 0 MB/s   ⬆️ 0 MB/s", 
            font=("Segoe UI", 18)
        )
        self.net_label.pack(pady=20)

        # Actions Card
        action_card = ctk.CTkFrame(bottom, corner_radius=20, fg_color=("#ffffff", "#1a1a2e"))
        action_card.grid(row=0, column=1, padx=(12, 0), sticky="nsew")
        
        ctk.CTkLabel(
            action_card, 
            text="⚡ Actions Rapides", 
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 15))
        
        ModernButton(
            action_card, 
            "🚀 Optimiser RAM", 
            self.optimize_ram,
            "primary"
        ).pack(fill="x", padx=25, pady=(12, 0))

        self.clean_btn = ModernButton(
            action_card, 
            "🧹 Nettoyer Maintenant", 
            self.start_cleanup,
            "primary"
        )
        self.clean_btn.pack(fill="x", padx=25, pady=12)
        
        ModernButton(
            action_card, 
            "🔍 Analyser (Simulation)", 
            self.start_simulation,
            "secondary"
        ).pack(fill="x", padx=25, pady=12)

    def update_stats(self):
        try:
            info = get_system_info()
            if info:
                self.cards["cpu"].update_value(info['cpu_usage'])
                self.cards["ram"].update_value(info['memory_usage'])
                self.cards["disk"].update_value(info['disk_usage'])
                self.cards["gpu"].update_value(info['gpu_usage'])
                self.net_label.configure(text=f"⬇️ {info['download_speed']}   ⬆️ {info['upload_speed']}")
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")

    def optimize_ram(self):
        from tkinter import messagebox
        success, msg = SystemOptimizer.optimize_ram()
        if success:
            messagebox.showinfo("Optimisation", msg)
            self.update_stats() # Immediate refresh
        else:
            messagebox.showerror("Erreur", msg)

    def start_cleanup(self):
        def cleanup_with_feedback():
            from tkinter import messagebox
            try:
                # Update UI to loading state
                self.clean_btn.configure(state="disabled", text="⏳ Nettoyage en cours...")
                
                result = self.cleaner.perform_cleanup(simulation=False)
                
                # Restore UI
                self.clean_btn.configure(state="normal", text="🧹 Nettoyer Maintenant")
                
                messagebox.showinfo(
                    "Nettoyage Terminé",
                    f"✅ Nettoyage réussi !\n\n"
                    f"📁 Fichiers supprimés : {result['files_cleaned']}\n"
                    f"💾 Espace libéré : {format_file_size(result['space_freed'])}\n"
                    f"⚠️ Erreurs : {result['errors']}"
                )
            except Exception as e:
                self.clean_btn.configure(state="normal", text="🧹 Nettoyer Maintenant")
                messagebox.showerror("Erreur", f"Erreur lors du nettoyage :\n{str(e)}")
        
        threading.Thread(target=cleanup_with_feedback, daemon=True).start()
    
    def start_simulation(self):
        def simulation_with_feedback():
            from tkinter import messagebox
            try:
                result = self.cleaner.perform_cleanup(simulation=True)
                messagebox.showinfo(
                    "Analyse Terminée (Simulation)",
                    f"🔍 Analyse terminée !\n\n"
                    f"📁 Fichiers qui seraient supprimés : {result['files_cleaned']}\n"
                    f"💾 Espace qui serait libéré : {format_file_size(result['space_freed'])}\n\n"
                    f"ℹ️ Aucun fichier n'a été supprimé (mode simulation)."
                )
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'analyse :\n{str(e)}")
        
        threading.Thread(target=simulation_with_feedback, daemon=True).start()

class CleanerView(ctk.CTkFrame):
    def __init__(self, parent, cleaner):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(
            self, 
            text="🧹 Nettoyage Avancé", 
            font=("Segoe UI", 36, "bold")
        ).pack(anchor="w", pady=(0, 25))
        
        self.scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            corner_radius=20
        )
        self.scroll.pack(fill="both", expand=True)
        
        categories = [
            ("Système", [
                "Fichiers Temporaires (%TEMP%)",
                "Cache Windows",
                "Logs Windows",
                "Crash Dumps (.dmp)",
                "Prefetch"
            ]),
            ("Navigateurs", [
                "Cache Chrome",
                "Cache Edge",
                "Cache Brave",
                "Cache Opera / Opera GX",
                "Cache Vivaldi",
                "Cache Yandex"
            ]),
            ("Gaming", [
                "Cache Steam",
                "Cache NVIDIA",
                "Cache AMD",
                "Logs Discord",
                "Logs Epic Games",
                "Logs Riot Games"
            ]),
            ("Applications", [
                "Cache Spotify",
                "Cache Adobe",
                "Cache Microsoft Teams",
                "Cache Slack",
                "Cache Telegram"
            ]),
            ("Développement", [
                "Cache VS Code",
                "Cache JetBrains (PyCharm...)",
                "Cache Android Studio"
            ])
        ]
        
        for title, items in categories:
            # Category Card
            cat_frame = ctk.CTkFrame(self.scroll, corner_radius=15, fg_color=("#ffffff", "#1a1a2e"))
            cat_frame.pack(fill="x", pady=12)
            
            ctk.CTkLabel(
                cat_frame, 
                text=title, 
                font=("Segoe UI", 22, "bold"),
                text_color=("#00d4aa", "#00d4aa")
            ).pack(anchor="w", padx=25, pady=(20, 15))
            
            for item in items:
                switch = ctk.CTkSwitch(
                    cat_frame, 
                    text=item,
                    font=("Segoe UI", 14)
                )
                switch.select()
                switch.pack(anchor="w", pady=8, padx=25)

class ToolsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(
            self, 
            text="🛠️ Gestion du Système", 
            font=("Segoe UI", 36, "bold")
        ).pack(anchor="w", pady=(0, 20))
        
        # Tabs for Tools
        self.tabview = ctk.CTkTabview(self, corner_radius=15, fg_color=("white", "#1a1a2e"))
        self.tabview.pack(fill="both", expand=True)
        
        self.tabview.add("Processus")
        self.tabview.add("Démarrage")
        self.tabview.add("Applications")
        self.tabview.add("Système")
        self.tabview.add("Disque")
        
        self.setup_process_tab()
        self.setup_startup_tab()
        self.setup_apps_tab()
        self.setup_system_tab()
        self.setup_disk_tab()

    def setup_process_tab(self):
        tab = self.tabview.tab("Processus")
        
        # Simple Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", pady=10)
        
        ModernButton(header, "🔄 Actualiser", self.refresh_processes, "secondary").pack(side="left")
        
        # Process List (Scrollable)
        self.proc_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.proc_scroll.pack(fill="both", expand=True, pady=10)
        
        self.refresh_processes()

    def refresh_processes(self):
        for widget in self.proc_scroll.winfo_children():
            widget.destroy()
            
        procs = ProcessManager.get_processes(limit=20, sort_by='memory')
        
        # Headers
        headers = ctk.CTkFrame(self.proc_scroll, fg_color="transparent")
        headers.pack(fill="x")
        ctk.CTkLabel(headers, text="Nom", width=200, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(headers, text="PID", width=80, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(headers, text="RAM (MB)", width=100, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        
        for p in procs:
            row = ctk.CTkFrame(self.proc_scroll, fg_color=("gray90", "#2b2b40"))
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=p['name'], width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(p['pid']), width=80, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{p['memory']:.1f}", width=100, anchor="w").pack(side="left", padx=5)
            
            ctk.CTkButton(
                row, 
                text="❌", 
                width=30, 
                fg_color="#ff4444", 
                hover_color="#cc0000",
                command=lambda pid=p['pid']: self.kill_proc(pid)
            ).pack(side="right", padx=5)

    def kill_proc(self, pid):
        success, msg = ProcessManager.kill_process(pid)
        from tkinter import messagebox
        if success:
            messagebox.showinfo("Succès", msg)
            self.refresh_processes()
        else:
            messagebox.showerror("Erreur", msg)

    def setup_startup_tab(self):
        tab = self.tabview.tab("Démarrage")
        
        ctk.CTkLabel(tab, text="Programmes au démarrage", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        items = StartupManager.get_startup_items()
        
        if not items:
            ctk.CTkLabel(scroll, text="Aucun item de démarrage trouvé.").pack()
            
        for item in items:
            frame = ctk.CTkFrame(scroll, fg_color=("gray90", "#2b2b40"))
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(frame, text=item['name'], font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=(5,0))
            ctk.CTkLabel(frame, text=item['path'], font=("Segoe UI", 10), text_color="gray").pack(anchor="w", padx=10)
            ctk.CTkLabel(frame, text=item['source'], font=("Segoe UI", 10, "italic")).pack(anchor="w", padx=10, pady=(0,5))
            
            ctk.CTkButton(
                frame,
                text="🗑️",
                width=40,
                fg_color="#ff4444",
                hover_color="#cc0000",
                command=lambda i=item: self.delete_startup(i)
            ).pack(side="right", padx=10, pady=10)

    def delete_startup(self, item):
        from tkinter import messagebox
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer cet élément du démarrage ?\n\n{item['name']}"):
            success, msg = StartupManager.delete_item(item)
            if success:
                messagebox.showinfo("Succès", msg)
                self.setup_startup_tab() # Refresh
            else:
                messagebox.showerror("Erreur", msg)

    def setup_apps_tab(self):
        tab = self.tabview.tab("Applications")
        
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", pady=10)
        
        ModernButton(header, "🔄 Actualiser", self.refresh_apps, "secondary").pack(side="left")
        
        # Headers
        headers = ctk.CTkFrame(tab, fg_color="transparent")
        headers.pack(fill="x", pady=(10,0))
        ctk.CTkLabel(headers, text="Nom", width=300, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(headers, text="Version", width=100, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(headers, text="Taille", width=80, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)

        self.apps_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.apps_scroll.pack(fill="both", expand=True, pady=5)
        
        self.refresh_apps()

    def refresh_apps(self):
        for widget in self.apps_scroll.winfo_children():
            widget.destroy()
            
        apps = AppManager.get_installed_apps()
        
        if not apps:
            ctk.CTkLabel(self.apps_scroll, text="Aucune application trouvée.").pack()
            
        for app in apps:
            row = ctk.CTkFrame(self.apps_scroll, fg_color=("gray90", "#2b2b40"))
            row.pack(fill="x", pady=2)
            
            # Smart truncate for long names
            name = app['name']
            if len(name) > 40:
                name = name[:37] + "..."
                
            ctk.CTkLabel(row, text=name, width=300, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=app['version'], width=100, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=app['size'], width=80, anchor="w").pack(side="left", padx=10)
            
            if app.get('uninstall_string'):
                ctk.CTkButton(
                    row, 
                    text="❌", 
                    width=30, 
                    fg_color="transparent", 
                    text_color="red",
                    hover_color="#ffebee",
                    command=lambda a=app: self.uninstall_app(a)
                ).pack(side="right", padx=10)

    def uninstall_app(self, app):
        from tkinter import messagebox
        if messagebox.askyesno("Désinstallation", f"Lancer le désinstallateur pour {app['name']} ?"):
            success, msg = AppManager.uninstall_app(app)
            if not success:
                messagebox.showerror("Erreur", msg)

    def setup_disk_tab(self):
        tab = self.tabview.tab("Disque")
        
        # Controls
        ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl.pack(fill="x", pady=10)
        
        ModernButton(ctrl, "🔍 Scanner Gros Fichiers (>100 Mo)", self.scan_disk, "secondary").pack(side="left")
        
        self.disk_status = ctk.CTkLabel(ctrl, text="")
        self.disk_status.pack(side="left", padx=20)
        
        # Results
        self.disk_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.disk_scroll.pack(fill="both", expand=True)

    def scan_disk(self):
        self.disk_status.configure(text="Scan en cours...")
        self.update_idletasks()
        
        def run_scan():
            files = DiskAnalyzer.scan_large_files()
            self.after(0, lambda: self.show_disk_results(files))
            
        threading.Thread(target=run_scan, daemon=True).start()
        
    def show_disk_results(self, files):
        self.disk_status.configure(text=f"Trouvé: {len(files)} fichiers")
        for w in self.disk_scroll.winfo_children():
            w.destroy()
            
        for f in files:
            row = ctk.CTkFrame(self.disk_scroll, fg_color=("gray90", "#2b2b40"))
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=f.get('name', '?'), width=300, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f.get('size_fmt', '?'), width=100, anchor="w").pack(side="left", padx=10)
            
            ctk.CTkButton(
                row,
                text="🗑️",
                width=40,
                fg_color="#ff4444",
                hover_color="#cc0000",
                command=lambda p=f['path']: self.delete_large_file(p)
            ).pack(side="right", padx=10, pady=5)
            
    def delete_large_file(self, path):
        from tkinter import messagebox
        import os
        if messagebox.askyesno("Suppression", f"Supprimer définitivement ce fichier ?\n\n{path}"):
            try:
                os.remove(path)
                messagebox.showinfo("Succès", "Fichier supprimé.")
                self.scan_disk() # Refresh
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                


    def setup_system_tab(self):
        tab = self.tabview.tab("Système")
        
        info = SystemInfo.get_info()
        
        # Grid layout for system info
        grid = ctk.CTkFrame(tab, fg_color="transparent")
        grid.pack(fill="both", expand=True, pady=20, padx=20)
        
        details = [
            ("🖥️ Système", info['os']),
            ("🔢 Version", info['version']),
            ("🧠 Processeur", info['cpu']),
            ("⚡ Coeurs", info['cpu_cores']),
            ("💾 Mémoire RAM", f"{info['ram_total']} (Utilisé: {info['ram_used']})"),
            ("🎮 Carte Graphique", info['gpu'])
        ]
        
        for i, (label, value) in enumerate(details):
            card = ctk.CTkFrame(grid, fg_color=("gray90", "#2b2b40"))
            card.pack(fill="x", pady=8)
            
            ctk.CTkLabel(
                card, 
                text=label, 
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w", padx=15, pady=(10, 0))
            
            ctk.CTkLabel(
                card, 
                text=value, 
                font=("Segoe UI", 12),
                text_color="gray"
            ).pack(anchor="w", padx=15, pady=(0, 10))

class LogsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(
            self, 
            text="📜 Historique des Nettoyages", 
            font=("Segoe UI", 36, "bold")
        ).pack(anchor="w", pady=(0, 25))
        
        # Actions
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 15))
        
        ModernButton(
            actions, 
            "🔄 Actualiser", 
            self.load_logs, 
            "secondary"
        ).pack(side="left", padx=(0, 10))
        
        ModernButton(
            actions, 
            "💾 Exporter CSV", 
            self.export_csv, 
            "primary"
        ).pack(side="left")
        
        # Log Viewer
        self.log_text = ctk.CTkTextbox(
            self, 
            font=("Consolas", 12),
            corner_radius=15
        )
        self.log_text.pack(fill="both", expand=True)
        
        self.load_logs()

    def load_logs(self):
        self.log_text.delete("0.0", "end")
        from logs import DELETIONS_LOG
        import os, json
        
        if not os.path.exists(DELETIONS_LOG):
            self.log_text.insert("0.0", "Aucun historique disponible.")
            return

        try:
            with open(DELETIONS_LOG, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-100:]):
                    try:
                        data = json.loads(line)
                        timestamp = data.get("timestamp_iso", "").split(".")[0].replace("T", " ")
                        action = "✅" if data.get("action") == "deleted" else "⚠️"
                        self.log_text.insert("end", f"{timestamp} | {action} | {data.get('category')} | {data.get('path')}\n")
                    except:
                        pass
        except Exception as e:
            self.log_text.insert("0.0", f"Erreur de lecture: {e}")

    def export_csv(self):
        from logs import ActionLogger
        import os
        path = os.path.join(os.path.expanduser("~"), "Desktop", "autocleaner_export.csv")
        if ActionLogger.export_to_csv(path):
            from tkinter import messagebox
            messagebox.showinfo("Export", f"Logs exportés sur le bureau :\n{path}")

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, config, save_cb):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.save_cb = save_cb
        
        ctk.CTkLabel(
            self, 
            text="⚙️ Paramètres", 
            font=("Segoe UI", 36, "bold")
        ).pack(anchor="w", pady=(0, 25))
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        # Toggles
        self.add_toggle(scroll, "Lancer au démarrage", "startup_enabled")
        self.add_toggle(scroll, "Minimiser dans la Tray", "minimize_to_tray")
        self.add_toggle(scroll, "Notifications", "notifications_enabled")
        self.add_toggle(scroll, "Sons", "sound_enabled")
        self.add_toggle(scroll, "Mode Furtif", "stealth_mode")
        self.add_toggle(scroll, "Mode Simulation (Sécurité)", "simulation_mode")
        
        # Auto-Clean Interval
        interval_frame = ctk.CTkFrame(scroll, corner_radius=15, fg_color=("#ffffff", "#1a1a2e"))
        interval_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            interval_frame, 
            text="⏱️ Intervalle de Nettoyage Automatique", 
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 15))
        
        interval_options = {
            "5 minutes": 5,
            "10 minutes": 10,
            "15 minutes": 15,
            "30 minutes": 30,
            "45 minutes": 45,
            "1 heure": 60,
            "2 heures": 120,
            "3 heures": 180
        }
        
        current_interval = self.config.get("auto_clean_interval_minutes", 30)
        current_label = next((k for k, v in interval_options.items() if v == current_interval), "30 minutes")
        
        self.interval_var = ctk.StringVar(value=current_label)
        interval_menu = ctk.CTkOptionMenu(
            interval_frame,
            variable=self.interval_var,
            values=list(interval_options.keys()),
            command=lambda choice: self.update_interval(interval_options[choice]),
            font=("Segoe UI", 14),
            width=250,
            corner_radius=10
        )
        interval_menu.pack(anchor="w", padx=25, pady=(0, 25))
        
        # Test Notification
        test_frame = ctk.CTkFrame(scroll, corner_radius=15, fg_color=("#ffffff", "#1a1a2e"))
        test_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            test_frame, 
            text="🔔 Tester les Notifications", 
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 15))
        
        ModernButton(
            test_frame, 
            "📢 Envoyer une Notification de Test", 
            self.test_notification,
            "secondary"
        ).pack(fill="x", padx=25, pady=(0, 25))

    def add_toggle(self, parent, text, key):
        var = ctk.BooleanVar(value=self.config.get(key, False))
        ToggleCard(parent, text, "", var, lambda: self.update(key, var.get())).pack(fill="x", pady=8)

    def update(self, key, val):
        self.config[key] = val
        self.save_cb()
    
    def update_interval(self, minutes):
        self.config["auto_clean_interval_minutes"] = minutes
        self.save_cb()
        from tkinter import messagebox
        messagebox.showinfo(
            "Intervalle Modifié",
            f"✅ L'intervalle de nettoyage automatique a été défini sur {minutes} minute(s).\n\n"
            f"Le nouveau délai sera appliqué au prochain cycle."
        )
    
    def test_notification(self):
        from utils import show_notification
        from tkinter import messagebox
        
        success = show_notification(
            "AutoCleaner Demo - Test",
            "🎉 Notification de test !\n\nSi vous voyez ce message, les notifications fonctionnent correctement.",
            duration=5
        )
        
        if success:
            messagebox.showinfo(
                "Test Réussi",
                "✅ La notification a été envoyée !\n\nVérifiez le Centre de notifications Windows (coin bas-droit)."
            )
        else:
            messagebox.showerror(
                "Erreur",
                "❌ Impossible d'afficher la notification.\n\nVérifiez que winotify est installé :\npip install winotify"
            )

class SystemTray:
    def __init__(self, show_cb, exit_cb):
        self.show_cb = show_cb
        self.exit_cb = exit_cb
        self.icon = None

    def run(self):
        try:
            image = load_logo((64, 64)) or Image.new('RGB', (64, 64), (0, 212, 170))
            menu = (
                item('Ouvrir', self.show_cb, default=True),
                item('Quitter', self.exit_cb)
            )
            self.icon = pystray.Icon("AutoCleanerDemo", image, "AutoCleaner Demo", menu)
            self.icon.run()
        except Exception as e:
            logger.error(f"Tray icon failed: {e}")

    def stop(self):
        if self.icon:
            self.icon.stop()
