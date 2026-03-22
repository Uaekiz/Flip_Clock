import tkinter as tk
from time import strftime
import ctypes

class MiniFlipClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Flip Clock")
        try:
            self.root.iconbitmap("clock_logo.ico")
        except:
            pass 
            
        self.root.overrideredirect(True)
        
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        
        self.themes = [
            {"bg": "#111111", "card": "#202022", "flap": "#151517", "text": "#E5E5E5", "line": "#111111", "date": "#999999", "close": "#AAAAAA", "hover": "#FFFFFF", "menu": "#111111"},
            {"bg": "#EAEAEA", "card": "#FFFFFF", "flap": "#F5F5F5", "text": "#333333", "line": "#EAEAEA", "date": "#666666", "close": "#888888", "hover": "#333333", "menu": "#EAEAEA"},
            {"bg": "#FCE4EC", "card": "#F8BBD0", "flap": "#F48FB1", "text": "#880E4F", "line": "#FCE4EC", "date": "#C2185B", "close": "#AD1457", "hover": "#4A0024", "menu": "#D81B60"},
            {"bg": "#FFF3E0", "card": "#FFE0B2", "flap": "#FFCC80", "text": "#E65100", "line": "#FFF3E0", "date": "#EF6C00", "close": "#E65100", "hover": "#BF360C", "menu": "#F57C00"},
            {"bg": "#E8F5E9", "card": "#C8E6C9", "flap": "#A5D6A7", "text": "#1B5E20", "line": "#E8F5E9", "date": "#2E7D32", "close": "#1B5E20", "hover": "#003300", "menu": "#388E3C"},
            {"bg": "#B71C1C", "card": "#E53935", "flap": "#D32F2F", "text": "#FFFFFF", "line": "#B71C1C", "date": "#FFCDD2", "close": "#FFFFFF", "hover": "#FFCDD2", "menu": "#B71C1C"}
        ]
        self.current_theme_index = 0
        self.apply_theme_colors()
        
        self.root.configure(bg=self.bg_color)
        
        self.width_normal = 210
        self.height_normal = 100
        self.current_w = self.width_normal
        self.current_h = self.height_normal
        
        self.palette_menu_open = False
        self.palette_menu_items = []
        
        self.settings_menu_open = False
        self.settings_menu_items = []
        self.language = "EN"
        self.use_ampm = False
        
        self.scale = 1.0
        self.is_fullscreen = False
        self.normal_geometry = ""
        
        self.root.geometry(f"{self.current_w}x{self.current_h}")
        
        self.start_x = 0
        self.start_y = 0
        self.is_hovering = False
        
        self.current_hour = ""
        self.current_minute = ""
        self.current_second = ""
        
        self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        
        self.create_widgets()
        
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Enter>", self.on_enter)
        self.root.bind("<Leave>", self.on_leave)
        
        self.update_time_loop()

    def apply_theme_colors(self):
        theme = self.themes[self.current_theme_index]
        self.bg_color = theme["bg"]
        self.card_color = theme["card"]
        self.flap_color = theme["flap"]
        self.text_color = theme["text"]
        self.line_color = theme["line"]
        self.date_color = theme["date"]
        self.close_color = theme["close"]
        self.hover_color = theme.get("hover", "#FFFFFF")

    def toggle_palette_menu(self, event=None):
        if self.palette_menu_open:
            self.close_palette_menu()
        else:
            self.open_palette_menu()

    def open_palette_menu(self):
        if self.palette_menu_open: return
        self.close_settings_menu()
        self.palette_menu_open = True
        
        num_themes = len(self.themes)
        box_w = 26 * num_themes + 10
        box_h = 26
        
        box_x1 = 35
        box_x2 = box_x1 + box_w
        box_y1 = self.current_h - 35
        box_y2 = box_y1 + box_h
        
        bg_rect = self.round_rectangle(self.canvas, box_x1, box_y1, box_x2, box_y2, radius=6, fill=self.card_color, outline="", tags="gui_overlay")
        self.palette_menu_items.append(bg_rect)
        
        for i, theme in enumerate(self.themes):
            cx = box_x1 + 18 + i * 26
            cy = box_y1 + 13
            size = 8
            
            if i == self.current_theme_index:
                sel_ring = self.canvas.create_rectangle(cx-size-3, cy-size-3, cx+size+3, cy+size+3, fill="", outline=self.text_color, width=2, state="normal", tags="gui_overlay")
                self.palette_menu_items.append(sel_ring)
            
            color_rect = self.canvas.create_rectangle(cx-size, cy-size, cx+size, cy+size, fill=theme.get("menu", theme["bg"]), outline="", state="normal", tags="gui_overlay")
            click_rect = self.canvas.create_rectangle(cx-13, cy-13, cx+13, cy+13, fill="", outline="", state="normal", tags="gui_overlay")
            
            def make_select_func(idx):
                def select_theme(e):
                    self.set_theme(idx)
                return select_theme
                
            func = make_select_func(i)
            self.canvas.tag_bind(color_rect, "<Button-1>", func)
            self.canvas.tag_bind(click_rect, "<Button-1>", func)
            
            def on_enter_sq(e, item=color_rect, idx=i):
                if idx != self.current_theme_index:
                    self.canvas.itemconfig(item, outline="#FFD700")
                self.root.config(cursor="hand2")
                
            def on_leave_sq(e, item=color_rect, idx=i):
                if idx != self.current_theme_index:
                    self.canvas.itemconfig(item, outline="")
                self.root.config(cursor="")

            self.canvas.tag_bind(click_rect, "<Enter>", on_enter_sq)
            self.canvas.tag_bind(click_rect, "<Leave>", on_leave_sq)
            self.canvas.tag_bind(color_rect, "<Enter>", on_enter_sq)
            self.canvas.tag_bind(color_rect, "<Leave>", on_leave_sq)
            
            self.palette_menu_items.append(color_rect)
            self.palette_menu_items.append(click_rect)

    def close_palette_menu(self):
        if not self.palette_menu_open: return
        self.palette_menu_open = False
        for item in self.palette_menu_items:
            self.canvas.delete(item)
        self.palette_menu_items = []

    def toggle_settings_menu(self, event=None):
        if self.settings_menu_open:
            self.close_settings_menu()
        else:
            self.open_settings_menu()

    def open_settings_menu(self):
        if self.settings_menu_open: return
        self.close_palette_menu()
        self.settings_menu_open = True
        
        box_w = 140
        box_h = 60
        box_x2 = self.current_w - 5
        box_x1 = box_x2 - box_w
        box_y1 = self.current_h - 95
        box_y2 = box_y1 + box_h
        
        bg_rect = self.round_rectangle(self.canvas, box_x1, box_y1, box_x2, box_y2, radius=6, fill=self.card_color, outline="", tags="gui_overlay")
        self.settings_menu_items.append(bg_rect)
        
        font_sm = ("Segoe UI", 10, "bold")
        
        langs = ["EN", "TR", "DE"]
        for i, lang in enumerate(langs):
            cx = box_x1 + 30 + i * 40
            cy = box_y1 + 18
            
            color = self.text_color if self.language == lang else self.date_color
            txt = self.canvas.create_text(cx, cy, text=lang, font=font_sm, fill=color, state="normal", tags="gui_overlay")
            click_rect = self.canvas.create_rectangle(cx-18, cy-12, cx+18, cy+12, fill="", outline="", state="normal", tags="gui_overlay")
            
            def make_set_lang(l):
                def set_lang(e):
                    self.language = l
                    self.current_hour = "" # trigger refresh
                    self.update_times()
                    self.close_settings_menu()
                    self.open_settings_menu()
                return set_lang
                
            func = make_set_lang(lang)
            self.canvas.tag_bind(txt, "<Button-1>", func)
            self.canvas.tag_bind(click_rect, "<Button-1>", func)
            
            def on_enter_l(e, item=txt, l=lang):
                if self.language != l:
                    self.canvas.itemconfig(item, fill=self.hover_color)
                self.root.config(cursor="hand2")
                
            def on_leave_l(e, item=txt, l=lang):
                if self.language != l:
                    self.canvas.itemconfig(item, fill=self.date_color)
                self.root.config(cursor="")
                
            self.canvas.tag_bind(click_rect, "<Enter>", on_enter_l)
            self.canvas.tag_bind(click_rect, "<Leave>", on_leave_l)
            self.canvas.tag_bind(txt, "<Enter>", on_enter_l)
            self.canvas.tag_bind(txt, "<Leave>", on_leave_l)
            
            self.settings_menu_items.extend([txt, click_rect])
            
        formats = [("12H", True), ("24H", False)]
        for i, (fmt_name, is_ampm) in enumerate(formats):
            cx = box_x1 + 45 + i * 50
            cy = box_y1 + 42
            
            color = self.text_color if self.use_ampm == is_ampm else self.date_color
            txt = self.canvas.create_text(cx, cy, text=fmt_name, font=font_sm, fill=color, state="normal", tags="gui_overlay")
            click_rect = self.canvas.create_rectangle(cx-20, cy-12, cx+20, cy+12, fill="", outline="", state="normal", tags="gui_overlay")
            
            def make_set_fmt(a):
                def set_fmt(e):
                    self.use_ampm = a
                    self.current_hour = "" 
                    self.update_times()
                    self.close_settings_menu()
                    self.open_settings_menu()
                return set_fmt
                
            func = make_set_fmt(is_ampm)
            self.canvas.tag_bind(txt, "<Button-1>", func)
            self.canvas.tag_bind(click_rect, "<Button-1>", func)
            
            def on_enter_f(e, item=txt, a=is_ampm):
                if self.use_ampm != a:
                    self.canvas.itemconfig(item, fill=self.hover_color)
                self.root.config(cursor="hand2")
                
            def on_leave_f(e, item=txt, a=is_ampm):
                if self.use_ampm != a:
                    self.canvas.itemconfig(item, fill=self.date_color)
                self.root.config(cursor="")
                
            self.canvas.tag_bind(click_rect, "<Enter>", on_enter_f)
            self.canvas.tag_bind(click_rect, "<Leave>", on_leave_f)
            self.canvas.tag_bind(txt, "<Enter>", on_enter_f)
            self.canvas.tag_bind(txt, "<Leave>", on_leave_f)
            
            self.settings_menu_items.extend([txt, click_rect])

    def close_settings_menu(self):
        if not self.settings_menu_open: return
        self.settings_menu_open = False
        for item in self.settings_menu_items:
            self.canvas.delete(item)
        self.settings_menu_items = []

    def set_theme(self, idx):
        self.current_theme_index = idx
        self.apply_theme_colors()
        self.root.configure(bg=self.bg_color)
        self.canvas.configure(bg=self.bg_color)
        
        self.palette_menu_open = False
        self.palette_menu_items = []
        self.settings_menu_open = False
        self.settings_menu_items = []
        
        self.current_hour = ""
        self.current_minute = ""
        self.current_second = ""
        self.create_widgets()

    def create_widgets(self):
        self.canvas.delete("all")
        self.palette_menu_open = False
        self.palette_menu_items = []
        
        base_w = 210
        base_h = 100
        
        scaled_w = base_w * self.scale
        scaled_h = base_h * self.scale
        
        self.offset_x = (self.current_w - scaled_w) / 2
        self.offset_y = (self.current_h - scaled_h) / 2
        
        def s(val): return val * self.scale
        
        # Coordinates for Hour and Minute cards
        self.h_coords = (self.offset_x + s(10), self.offset_y + s(10), self.offset_x + s(80), self.offset_y + s(65))
        self.m_coords = (self.offset_x + s(90), self.offset_y + s(10), self.offset_x + s(160), self.offset_y + s(65))
        
        self.round_rectangle(self.canvas, *self.h_coords, radius=s(8), fill=self.card_color, outline="")
        self.round_rectangle(self.canvas, *self.m_coords, radius=s(8), fill=self.card_color, outline="")
        
        font_time = ("Arial", int(36 * self.scale), "bold")
        font_sec = ("Arial", int(20 * self.scale), "bold")
        font_date = ("Segoe UI", int(10 * self.scale), "normal")
        
        # Flaps text
        self.hour_text = self.canvas.create_text(self.offset_x + s(45), self.offset_y + s(37), text=self.current_hour, font=font_time, fill=self.text_color)
        self.minute_text = self.canvas.create_text(self.offset_x + s(125), self.offset_y + s(37), text=self.current_minute, font=font_time, fill=self.text_color)
        
        # Second text (no card or split, just plain digital text)
        self.second_text = self.canvas.create_text(self.offset_x + s(182), self.offset_y + s(45), text=self.current_second, font=font_sec, fill=self.text_color)
        
        # Date text
        self.date_text = self.canvas.create_text(self.offset_x + s(105), self.offset_y + s(87), text="", font=font_date, fill=self.date_color)
        
        # AM/PM text
        font_ampm = ("Segoe UI", int(10 * self.scale), "bold")
        self.ampm_text = self.canvas.create_text(self.offset_x + s(182), self.offset_y + s(65), text="", font=font_ampm, fill=self.date_color)
        
        # Split lines for the flip mechanism look (only on H and M)
        self.canvas.create_line(self.offset_x + s(9), self.offset_y + s(37), self.offset_x + s(81), self.offset_y + s(37), fill=self.line_color, width=max(1, int(1*self.scale)), tags="split_line")
        self.canvas.create_line(self.offset_x + s(89), self.offset_y + s(37), self.offset_x + s(161), self.offset_y + s(37), fill=self.line_color, width=max(1, int(1*self.scale)), tags="split_line")
        
        self.canvas.tag_raise("split_line")
        
        # UI Buttons at Top Right
        btn_font = ("Segoe UI", 14, "normal")
        
        # Close Button
        self.close_btn = self.canvas.create_text(self.current_w - 15, 12, text="✕", font=btn_font, fill=self.close_color, state="hidden")
        self.close_box = self.canvas.create_rectangle(self.current_w - 30, 0, self.current_w, 25, fill="", outline="", state="hidden")
        
        # Maximize Button
        max_icon = "🗗" if self.is_fullscreen else "◻"
        self.max_btn = self.canvas.create_text(self.current_w - 45, 12, text=max_icon, font=btn_font, fill=self.close_color, state="hidden")
        self.max_box = self.canvas.create_rectangle(self.current_w - 60, 0, self.current_w - 30, 25, fill="", outline="", state="hidden")
      
        settings_btn_font = ("Segoe UI", 12, "normal") # Ayarlar ikonu iri durduğu için onu 2 punto küçültüyoruz
        
        # Palette Button
        self.palette_btn = self.canvas.create_text(20, self.current_h - 20, text="🎨", font=btn_font, fill=self.close_color, state="hidden")
        self.palette_box = self.canvas.create_rectangle(5, self.current_h - 35, 35, self.current_h - 5, fill="", outline="", state="hidden")
        
        # Settings Button
        self.settings_btn = self.canvas.create_text(self.current_w - 20, self.current_h - 16, text="⚙", font=settings_btn_font, fill=self.close_color, state="hidden")
        self.settings_box = self.canvas.create_rectangle(self.current_w - 35, self.current_h - 35, self.current_w - 5, self.current_h - 5, fill="", outline="", state="hidden")
        
        # Bindings for Close
        self.canvas.tag_bind(self.close_btn, "<Button-1>", self.exit_app)
        self.canvas.tag_bind(self.close_box, "<Button-1>", self.exit_app)
        self.canvas.tag_bind(self.close_btn, "<Enter>", lambda e: self.on_btn_hover(self.close_btn))
        self.canvas.tag_bind(self.close_box, "<Enter>", lambda e: self.on_btn_hover(self.close_btn))
        self.canvas.tag_bind(self.close_btn, "<Leave>", lambda e: self.on_btn_leave(self.close_btn))
        self.canvas.tag_bind(self.close_box, "<Leave>", lambda e: self.on_btn_leave(self.close_btn))
        
        # Bindings for Maximize
        self.canvas.tag_bind(self.max_btn, "<Button-1>", self.toggle_fullscreen)
        self.canvas.tag_bind(self.max_box, "<Button-1>", self.toggle_fullscreen)
        self.canvas.tag_bind(self.max_btn, "<Enter>", lambda e: self.on_btn_hover(self.max_btn))
        self.canvas.tag_bind(self.max_box, "<Enter>", lambda e: self.on_btn_hover(self.max_btn))
        self.canvas.tag_bind(self.max_btn, "<Leave>", lambda e: self.on_btn_leave(self.max_btn))
        self.canvas.tag_bind(self.max_box, "<Leave>", lambda e: self.on_btn_leave(self.max_btn))
        
        # Bindings for Palette
        self.canvas.tag_bind(self.palette_btn, "<Button-1>", self.toggle_palette_menu)
        self.canvas.tag_bind(self.palette_box, "<Button-1>", self.toggle_palette_menu)
        self.canvas.tag_bind(self.palette_btn, "<Enter>", lambda e: self.on_btn_hover(self.palette_btn))
        self.canvas.tag_bind(self.palette_box, "<Enter>", lambda e: self.on_btn_hover(self.palette_btn))
        self.canvas.tag_bind(self.palette_btn, "<Leave>", lambda e: self.on_btn_leave(self.palette_btn))
        self.canvas.tag_bind(self.palette_box, "<Leave>", lambda e: self.on_btn_leave(self.palette_btn))
        
        # Bindings for Settings
        self.canvas.tag_bind(self.settings_btn, "<Button-1>", self.toggle_settings_menu)
        self.canvas.tag_bind(self.settings_box, "<Button-1>", self.toggle_settings_menu)
        self.canvas.tag_bind(self.settings_btn, "<Enter>", lambda e: self.on_btn_hover(self.settings_btn))
        self.canvas.tag_bind(self.settings_box, "<Enter>", lambda e: self.on_btn_hover(self.settings_btn))
        self.canvas.tag_bind(self.settings_btn, "<Leave>", lambda e: self.on_btn_leave(self.settings_btn))
        self.canvas.tag_bind(self.settings_box, "<Leave>", lambda e: self.on_btn_leave(self.settings_btn))
        
        # Update immediately to populate texts
        self.current_hour = "" # force refresh
        self.current_minute = ""
        self.current_second = ""
        self.update_times()

    def toggle_fullscreen(self, event=None):
        if not self.is_fullscreen:
            self.normal_geometry = self.root.geometry()
            
            # Get current monitor geometry
            user32 = ctypes.windll.user32
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
            class MONITORINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", RECT), ("rcWork", RECT), ("dwFlags", ctypes.c_ulong)]
            
            x = self.root.winfo_x() + (self.width_normal // 2)
            y = self.root.winfo_y() + (self.height_normal // 2)
            
            monitor = user32.MonitorFromPoint(POINT(x, y), 2) # 2 = MONITOR_DEFAULTTONEAREST
            
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            
            if user32.GetMonitorInfoW(monitor, ctypes.byref(mi)):
                screen_x = mi.rcMonitor.left
                screen_y = mi.rcMonitor.top
                screen_w = mi.rcMonitor.right - mi.rcMonitor.left
                screen_h = mi.rcMonitor.bottom - mi.rcMonitor.top
            else:
                screen_x = 0
                screen_y = 0
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()

            self.current_w = screen_w
            self.current_h = screen_h
            
            # Scale to fit about 50% of screen size to look elegant
            self.scale = min(screen_w / 210, screen_h / 100) * 0.6
            self.is_fullscreen = True
            
            self.root.geometry(f"{screen_w}x{screen_h}+{screen_x}+{screen_y}")
            
        else:
            self.current_w = self.width_normal
            self.current_h = self.height_normal
            self.scale = 1.0
            self.is_fullscreen = False
            self.root.geometry(self.normal_geometry)
            
        # Ensure we recreate the Canvas cleanly at the new size
        self.canvas.config(width=self.current_w, height=self.current_h)
        self.create_widgets()
        
        # Since clicking max happens while hovering, ensure buttons are visible
        self.canvas.itemconfig(self.close_btn, state="normal")
        self.canvas.itemconfig(self.close_box, state="normal")
        self.canvas.itemconfig(self.max_btn, state="normal")
        self.canvas.itemconfig(self.max_box, state="normal")
        self.canvas.itemconfig(self.palette_btn, state="normal")
        self.canvas.itemconfig(self.palette_box, state="normal")
        self.canvas.itemconfig(self.settings_btn, state="normal")
        self.canvas.itemconfig(self.settings_box, state="normal")
        self.is_hovering = True

    def on_btn_hover(self, btn_item):
        self.canvas.itemconfig(btn_item, fill=self.hover_color)
        self.root.config(cursor="hand2")

    def on_btn_leave(self, btn_item):
        self.canvas.itemconfig(btn_item, fill=self.close_color)
        self.root.config(cursor="")

    def on_enter(self, event):
        self.is_hovering = True
        self.canvas.itemconfig(self.close_btn, state="normal")
        self.canvas.itemconfig(self.close_box, state="normal")
        self.canvas.itemconfig(self.max_btn, state="normal")
        self.canvas.itemconfig(self.max_box, state="normal")
        self.canvas.itemconfig(self.palette_btn, state="normal")
        self.canvas.itemconfig(self.palette_box, state="normal")
        self.canvas.itemconfig(self.settings_btn, state="normal")
        self.canvas.itemconfig(self.settings_box, state="normal")

    def on_leave(self, event):
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        if x < 0 or y < 0 or x >= self.current_w or y >= self.current_h:
            self.is_hovering = False
            self.canvas.itemconfig(self.close_btn, state="hidden")
            self.canvas.itemconfig(self.close_box, state="hidden")
            self.canvas.itemconfig(self.max_btn, state="hidden")
            self.canvas.itemconfig(self.max_box, state="hidden")
            self.canvas.itemconfig(self.palette_btn, state="hidden")
            self.canvas.itemconfig(self.palette_box, state="hidden")
            self.canvas.itemconfig(self.settings_btn, state="hidden")
            self.canvas.itemconfig(self.settings_box, state="hidden")
            self.close_palette_menu()
            self.close_settings_menu()

    def round_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1,
                  x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2,
                  x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,
                  x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def trigger_flip(self, coords, text_item, new_val):
        x1, y1, x2, y2 = coords
        mid_y = self.offset_y + 37 * self.scale
        
        flap = self.canvas.create_rectangle(x1, y1, x2, y1, fill=self.flap_color, outline="")
        
        def animate(step):
            total_steps = 10
            half_steps = total_steps // 2
            
            if step < half_steps:
                current_y2 = y1 + (mid_y - y1) * (step + 1) / half_steps
                self.canvas.coords(flap, x1, y1, x2, current_y2)
                self.root.after(15, lambda: animate(step + 1))
            elif step == half_steps:
                self.canvas.itemconfig(text_item, text=new_val)
                self.canvas.coords(flap, x1, mid_y, x2, y2)
                self.canvas.create_line(x1-1, mid_y, x2+1, mid_y, fill=self.line_color, width=max(1, int(1*self.scale)), tags="temp_line")
                self.root.after(15, lambda: animate(step + 1))
            elif step <= total_steps:
                current_y1 = mid_y + (y2 - mid_y) * (step - half_steps) / half_steps
                self.canvas.coords(flap, x1, current_y1, x2, y2)
                if step < total_steps:
                    self.root.after(15, lambda: animate(step + 1))
                else:
                    self.canvas.delete(flap)
                    self.canvas.delete("temp_line")
                    
        animate(0)

    def get_localized_date_string(self):
        import time
        t = time.localtime()
        wday = t.tm_wday # 0=Monday
        mon = t.tm_mon # 1-12
        mday = t.tm_mday
        year = t.tm_year

        days = {
            "EN": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "TR": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
            "DE": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        }
        months = {
            "EN": ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            "TR": ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
            "DE": ["", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
        }
        
        d = days.get(self.language, days["EN"])[wday]
        m = months.get(self.language, months["EN"])[mon]
        
        if self.language == "DE":
            return f"{d}, {mday}. {m} {year}"
        elif self.language == "TR":
            return f"{d}, {mday} {m} {year}"
        else:
            return f"{d}, {m} {mday}, {year}"

    def update_times(self):
        import time
        t = time.localtime()
        
        if self.use_ampm:
            h = t.tm_hour % 12
            if h == 0: h = 12
            hours = f"{h:02d}"
            ampm = "AM" if t.tm_hour < 12 else "PM"
        else:
            hours = f"{t.tm_hour:02d}"
            ampm = ""
            
        minutes = f"{t.tm_min:02d}"
        seconds = f"{t.tm_sec:02d}"
        
        date_string = self.get_localized_date_string()
        self.canvas.itemconfig(self.date_text, text=date_string)
        self.canvas.itemconfig(self.ampm_text, text=ampm)
        
        if self.current_hour != hours:
            if self.current_hour == "":
                self.canvas.itemconfig(self.hour_text, text=hours)
            else:
                self.trigger_flip(self.h_coords, self.hour_text, hours)
            self.current_hour = hours
            
        if self.current_minute != minutes:
            if self.current_minute == "":
                self.canvas.itemconfig(self.minute_text, text=minutes)
            else:
                self.trigger_flip(self.m_coords, self.minute_text, minutes)
            self.current_minute = minutes
            
        if self.current_second != seconds:
            self.canvas.itemconfig(self.second_text, text=seconds)
            self.current_second = seconds

    def update_time_loop(self):
        self.update_times()
        self.canvas.tag_raise("split_line")
        self.canvas.tag_raise("gui_overlay")
        self.root.after(1000, self.update_time_loop)

    def start_move(self, event):
        # Allow dragging only if not in fullscreen
        if not self.is_fullscreen:
            self.start_x = event.x
            self.start_y = event.y

    def do_move(self, event):
        if not self.is_fullscreen:
            x = self.root.winfo_x() - self.start_x + event.x
            y = self.root.winfo_y() - self.start_y + event.y
            self.root.geometry(f"+{x}+{y}")

    def exit_app(self, event=None):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    x = screen_width - 230
    y = 40
    root.geometry(f"+{x}+{y}")
    app = MiniFlipClock(root)
    root.mainloop()
