import customtkinter as ctk

class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, icon, color):
        super().__init__(parent, corner_radius=20, fg_color=("#ffffff", "#1a1a2e"))
        
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
            font=("Segoe UI", 32, "bold"),
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
        else:
            fg_color = ("#e8eef5", "#2a2a3e")
            hover_color = ("#d0d9e5", "#3a3a4e")
            text_color = ("#1a1a2e", "#ffffff")
        
        super().__init__(
            parent,
            text=text,
            command=command,
            height=50,
            corner_radius=12,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=("Segoe UI", 15, "bold")
        )
