import customtkinter as ctk

class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, icon, color):
        # Ultimate Design: Border matches accent color with low opacity feel (simulated by hex)
        super().__init__(parent, corner_radius=20, fg_color=("#ffffff", "#212130"), border_width=2, border_color=color)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self, 
            text=icon, 
            font=("Segoe UI", 40)
        )
        self.icon_label.pack(pady=(20, 5))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=("Segoe UI", 14, "bold"),
            text_color="gray"
        )
        self.title_label.pack()
        
        # Value
        self.value_label = ctk.CTkLabel(
            self, 
            text="0%", 
            font=("Segoe UI", 42, "bold"),
            text_color=color
        )
        self.value_label.pack(pady=(5, 10))
        
        # Progress Bar
        self.progress = ctk.CTkProgressBar(
            self, 
            width=180, 
            height=8,
            corner_radius=4,
            progress_color=color
        )
        self.progress.pack(pady=(0, 20))
        self.progress.set(0)
        
        self.color = color

    def update_value(self, value):
        try:
            val = float(value)
            self.value_label.configure(text=f"{val:.1f}%")
            self.progress.set(val / 100)
        except:
            self.value_label.configure(text="N/A")
            self.progress.set(0)

class ToggleCard(ctk.CTkFrame):
    def __init__(self, parent, title, description, variable, command):
        super().__init__(parent, corner_radius=15, fg_color=("#ffffff", "#1a1a2e"))
        
        self.grid_columnconfigure(0, weight=1)
        
        # Text Container
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w", padx=25, pady=20)
        
        ctk.CTkLabel(
            text_frame, 
            text=title, 
            font=("Segoe UI", 16, "bold"),
            anchor="w"
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                text_frame, 
                text=description, 
                font=("Segoe UI", 12),
                text_color="gray",
                anchor="w"
            ).pack(anchor="w")
        
        # Switch
        switch = ctk.CTkSwitch(
            self,
            text="",
            variable=variable,
            command=command,
            width=50,
            progress_color="#00d4aa"
        )
        switch.grid(row=0, column=1, padx=25, pady=20)

class ModernButton(ctk.CTkButton):
    def __init__(self, parent, text, command, style="primary"):
        if style == "primary":
            fg_color = ("#00d4aa", "#00d4aa")
            hover_color = ("#00b894", "#00b894")
            text_color = "white"
            border_color = "#00b894"
        elif style == "outline":
            # Ghost Button Style
            fg_color = "transparent"
            hover_color = ("#e0e0e0", "#2a2a3e")
            text_color = ("#333", "gray80")
            border_color = "gray50"
        else:
            fg_color = ("#e8eef5", "#2a2a3e")
            hover_color = ("#d0d9e5", "#3a3a4e")
            text_color = ("#1a1a2e", "#ffffff")
            border_color = "#3a3a4e"

        super().__init__(
            parent,
            text=text,
            command=command,
            height=50,
            corner_radius=12,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            border_width=1 if style == "outline" else 0,
            border_color=border_color,
            font=("Segoe UI", 15, "bold")
        )

class FeedbackDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Envoyer un Avis / Feedback")
        self.geometry("400x450")
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 225
        self.geometry(f"+{x}+{y}")
        
        self.grab_set() # Modal
        self.focus_force()
        
        # Surface Card (Depth)
        surface = ctk.CTkFrame(self, fg_color=("#f8f9fa", "#1e1e2d"), corner_radius=20, border_width=1, border_color=("#e0e0e0", "#333"))
        surface.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(surface, text="✨ Votre avis nous intéresse !", font=("Segoe UI", 18, "bold"), text_color=("#333", "#fff")).pack(pady=(25, 20))
        
        # Subject
        ctk.CTkLabel(surface, text="Sujet", font=("Segoe UI", 12, "bold"), text_color="gray", anchor="w").pack(fill="x", padx=25, pady=(5, 0))
        self.subject = ctk.CTkEntry(surface, placeholder_text="Bug, Suggestion...", height=40, border_width=0, fg_color=("#fff", "#252535"))
        self.subject.pack(fill="x", padx=25, pady=(5, 15))
        
        # Message
        ctk.CTkLabel(surface, text="Message", font=("Segoe UI", 12, "bold"), text_color="gray", anchor="w").pack(fill="x", padx=25)
        self.message = ctk.CTkTextbox(surface, height=120, border_width=0, fg_color=("#fff", "#252535"))
        self.message.pack(fill="x", padx=25, pady=(5, 20))
        
        # Buttons
        self.send_btn = ModernButton(surface, "Envoyer l'Avis", self.send_feedback, "primary")
        self.send_btn.pack(fill="x", padx=25, pady=(0, 10))
        
        ModernButton(surface, "Annuler", self.destroy, "outline").pack(fill="x", padx=25, pady=(0, 20))
        
    def send_feedback(self):
        subj = self.subject.get()
        msg = self.message.get("1.0", "end-1c")
        
        if not subj.strip() or not msg.strip():
            from tkinter import messagebox
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs.")
            return
            
        self.send_btn.configure(state="disabled", text="Envoi en cours...")
        
        import threading
        threading.Thread(target=self._send_logic, args=(subj, msg), daemon=True).start()
        
    def _send_logic(self, subj, msg):
        import requests
        import json
        from config import FEEDBACK_WEBHOOK_URL, VERSION
        from tkinter import messagebox
        
        payload = {
            "content": f"**Nouveau Feedback (v{VERSION})**\n**Sujet:** {subj}\n\n{msg}"
        }
        
        # If using Formspree, structure might differ slightly (email/message fields)
        # But this structure works for Discord. For Formspree, we adapt if URL detect.
        
        if "formspree" in FEEDBACK_WEBHOOK_URL:
            payload = {"email": "user@autocleaner.app", "message": f"[{subj}] {msg}"}
            
        try:
            if not FEEDBACK_WEBHOOK_URL:
                raise ValueError("Aucune URL de Webhook configurée.")
                
            response = requests.post(FEEDBACK_WEBHOOK_URL, json=payload)
            
            if response.status_code in [200, 204]:
                self.after(0, lambda: self._success())
            else:
                raise Exception(f"Erreur HTTP {response.status_code}")
        except Exception as e:
            self.after(0, lambda: self._error(str(e)))
            
    def _success(self):
        from tkinter import messagebox
        messagebox.showinfo("Merci !", "Votre message a bien été envoyé.")
        self.destroy()
        
    def _error(self, err):
        from tkinter import messagebox
        messagebox.showerror("Erreur", f"Échec de l'envoi : {err}\n\nVérifiez votre connexion ou la configuration.")
        self.send_btn.configure(state="normal", text="Réessayer")
