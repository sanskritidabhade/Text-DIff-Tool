import tkinter as tk
from tkinter import ttk, filedialog
import difflib

# ── Theme definitions ─────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "BG":           "#0f0f14",
        "SURFACE":      "#1a1a24",
        "SURFACE2":     "#22222f",
        "BORDER":       "#2e2e40",
        "ACCENT":       "#7c6af7",
        "ACCENT2":      "#a78bfa",
        "TEXT":         "#e2e1f0",
        "TEXT_DIM":     "#6b6a82",
        "ADD_BG":       "#1a2e1a",
        "ADD_FG":       "#6ee06e",
        "DEL_BG":       "#2e1a1a",
        "DEL_FG":       "#f47a7a",
        "SAME_FG":      "#9997b8",
        "WORD_ADD":     "#1e3d1e",
        "WORD_DEL":     "#3d1e1e",
        "WORD_TXT_ADD": "#aaf0aa",
        "WORD_TXT_DEL": "#f0aaaa",
        "ENTRY_BG":     "#22222f",
        "SCROLLBAR_BG": "#22222f",
        "SCROLLBAR_TR": "#1a1a24",
        "LABEL_ICON":   "Moon",
        "LABEL_TEXT":   "Dark",
    },
    "light": {
        "BG":           "#f4f4f8",
        "SURFACE":      "#ffffff",
        "SURFACE2":     "#e8e8f0",
        "BORDER":       "#d0cfe8",
        "ACCENT":       "#5b48e8",
        "ACCENT2":      "#4533cc",
        "TEXT":         "#1a1928",
        "TEXT_DIM":     "#7370a0",
        "ADD_BG":       "#e6f9e6",
        "ADD_FG":       "#1a6b1a",
        "DEL_BG":       "#fde8e8",
        "DEL_FG":       "#b52222",
        "SAME_FG":      "#4a4870",
        "WORD_ADD":     "#c8f0c8",
        "WORD_DEL":     "#f8d0d0",
        "WORD_TXT_ADD": "#0f4f0f",
        "WORD_TXT_DEL": "#8b0000",
        "ENTRY_BG":     "#ffffff",
        "SCROLLBAR_BG": "#d8d8e8",
        "SCROLLBAR_TR": "#ebebf5",
        "LABEL_ICON":   "Sun",
        "LABEL_TEXT":   "Light",
    },
}

FONT_MONO  = ("Courier New", 11)
FONT_UI    = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_LABEL = ("Segoe UI", 9)
FONT_COUNT = ("Courier New", 9)


class DiffApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Diff - Word-Level Highlighter")
        self.geometry("1400x860")
        self.minsize(900, 600)

        self._theme_name = "dark"
        self._T = THEMES["dark"]

        self._file1       = tk.StringVar(value="")
        self._file2       = tk.StringVar(value="")
        self._word_count1 = tk.StringVar(value="")
        self._word_count2 = tk.StringVar(value="")
        self._status      = tk.StringVar(value="Load two files and press Compare")
        self._diff_mode   = tk.StringVar(value="side")

        # Registries for live re-theming
        self._tk_widgets    = []   # (widget, role)
        self._entry_widgets = []
        self._pill_widgets  = []   # (frame, label, role)
        self._text_widgets  = []   # tk.Text instances

        self._build_ui()
        self._apply_ttk_style()

    # ─────────────────────────────────────────────────────────────────────────
    # Theme helpers
    # ─────────────────────────────────────────────────────────────────────────
    def t(self, key):
        return self._T[key]

    def _apply_ttk_style(self):
        T = self._T
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",            background=T["BG"])
        s.configure("TLabel",            background=T["BG"],      foreground=T["TEXT"],     font=FONT_UI)
        s.configure("Dim.TLabel",        background=T["BG"],      foreground=T["TEXT_DIM"], font=FONT_LABEL)
        s.configure("Count.TLabel",      background=T["SURFACE2"],foreground=T["ACCENT2"],  font=FONT_COUNT, padding=(8,3))
        s.configure("TButton",           background=T["ACCENT"],  foreground="#ffffff",
                    font=("Segoe UI",10,"bold"), borderwidth=0, focusthickness=0, padding=(14,7))
        s.map("TButton",
              background=[("active", T["ACCENT2"]), ("pressed", T["ACCENT"])],
              foreground=[("active","#ffffff")])
        s.configure("Ghost.TButton",     background=T["SURFACE2"],foreground=T["TEXT_DIM"],
                    font=("Segoe UI",9),  borderwidth=0, padding=(10,5))
        s.map("Ghost.TButton",
              background=[("active", T["BORDER"])],
              foreground=[("active", T["TEXT"])])
        s.configure("Seg.TButton",       background=T["SURFACE2"],foreground=T["TEXT_DIM"],
                    font=("Segoe UI",9,"bold"), borderwidth=0, padding=(10,5))
        s.map("Seg.TButton",
              background=[("active", T["ACCENT"])],
              foreground=[("active","#ffffff")])
        s.configure("Active.Seg.TButton",background=T["ACCENT"], foreground="#ffffff",
                    font=("Segoe UI",9,"bold"), borderwidth=0, padding=(10,5))
        s.configure("Theme.TButton",     background=T["SURFACE2"],foreground=T["ACCENT2"],
                    font=("Segoe UI",9,"bold"), borderwidth=0, padding=(8,5))
        s.map("Theme.TButton",
              background=[("active", T["BORDER"])],
              foreground=[("active", T["ACCENT"])])
        s.configure("TScrollbar",        background=T["SCROLLBAR_BG"],
                    troughcolor=T["SCROLLBAR_TR"], borderwidth=0, arrowsize=12)
        s.map("TScrollbar", background=[("active", T["BORDER"])])

    def _retint_widget(self, w, role):
        T = self._T
        cfg = {}
        if   role == "BG":                   cfg = dict(bg=T["BG"])
        elif role == "SURFACE":              cfg = dict(bg=T["SURFACE"])
        elif role == "SURFACE2":             cfg = dict(bg=T["SURFACE2"])
        elif role == "BORDER_LINE":          cfg = dict(bg=T["BORDER"])
        elif role == "TITLE_LBL":            cfg = dict(bg=T["BG"],       fg=T["ACCENT2"])
        elif role == "DIM_LBL":              cfg = dict(bg=T["BG"],       fg=T["TEXT_DIM"])
        elif role == "SURFACE_ACCENT_LBL":   cfg = dict(bg=T["SURFACE2"], fg=T["ACCENT2"])
        elif role == "STATUS_LBL":           cfg = dict(bg=T["SURFACE"],  fg=T["TEXT_DIM"])
        try:
            w.configure(**cfg)
        except Exception:
            pass

    def _toggle_theme(self):
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        self._T = THEMES[self._theme_name]
        self.configure(bg=self._T["BG"])
        self._apply_ttk_style()
        for w, role in self._tk_widgets:
            self._retint_widget(w, role)
        T = self._T
        for e in self._entry_widgets:
            try:
                e.configure(bg=T["ENTRY_BG"], fg=T["TEXT"],
                            insertbackground=T["ACCENT"],
                            highlightbackground=T["BORDER"],
                            highlightcolor=T["ACCENT"])
            except Exception:
                pass
        for frame, lbl, role in self._pill_widgets:
            bg_key = role + "_BG"
            fg_key = role + "_FG"
            bg = T[bg_key]
            fg = T[fg_key]
            try:
                frame.configure(bg=bg)
                lbl.configure(bg=bg, fg=fg)
            except Exception:
                pass
        try:
            icon = "☀" if self._theme_name == "light" else ")"
            label = T["LABEL_TEXT"]
            self._theme_btn.configure(text=f"[ {label} ]")
        except Exception:
            pass
        for t in self._text_widgets:
            try:
                t.configure(bg=T["SURFACE"], fg=T["SAME_FG"])
                self._configure_tags(t)
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────────────
    def _reg(self, widget, role):
        self._tk_widgets.append((widget, role))
        return widget

    def _build_ui(self):
        T = self._T
        self.configure(bg=T["BG"])

        # ── Top bar ──────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=T["BG"], pady=14, padx=20)
        top.pack(fill="x")
        self._reg(top, "BG")

        title_lbl = tk.Label(top, text="<> Diff", bg=T["BG"], fg=T["ACCENT2"],
                             font=("Courier New", 18, "bold"))
        title_lbl.pack(side="left")
        self._reg(title_lbl, "TITLE_LBL")

        sub_lbl = tk.Label(top, text="  Word-Level File Comparison",
                           bg=T["BG"], fg=T["TEXT_DIM"], font=("Segoe UI", 11))
        sub_lbl.pack(side="left", padx=(4, 0))
        self._reg(sub_lbl, "DIM_LBL")

        # Right side of top bar
        right_top = tk.Frame(top, bg=T["BG"])
        right_top.pack(side="right")
        self._reg(right_top, "BG")

        # Theme toggle
        self._theme_btn = ttk.Button(
            right_top,
            text="[ Dark ]",
            style="Theme.TButton",
            command=self._toggle_theme)
        self._theme_btn.pack(side="left", padx=(0, 16))

        # View mode toggle
        tog = tk.Frame(right_top, bg=T["BG"])
        tog.pack(side="left")
        self._reg(tog, "BG")

        view_lbl = tk.Label(tog, text="View:", bg=T["BG"], fg=T["TEXT_DIM"], font=FONT_LABEL)
        view_lbl.pack(side="left", padx=(0, 6))
        self._reg(view_lbl, "DIM_LBL")

        self._btn_side = ttk.Button(tog, text="Side by Side", style="Active.Seg.TButton",
                                    command=lambda: self._set_mode("side"))
        self._btn_unified = ttk.Button(tog, text="Unified", style="Seg.TButton",
                                       command=lambda: self._set_mode("unified"))
        self._btn_side.pack(side="left")
        self._btn_unified.pack(side="left", padx=(2, 0))

        # ── Separator ────────────────────────────────────────────────────────
        sep1 = tk.Frame(self, bg=T["BORDER"], height=1)
        sep1.pack(fill="x")
        self._reg(sep1, "BORDER_LINE")

        # ── File picker row ───────────────────────────────────────────────────
        file_row = tk.Frame(self, bg=T["BG"], pady=12, padx=20)
        file_row.pack(fill="x")
        self._reg(file_row, "BG")
        for c, w in enumerate([1, 0, 1, 0, 0]):
            file_row.columnconfigure(c, weight=w)

        self._build_file_picker(file_row, "File 1", self._file1,
                                self._word_count1, self._pick_file1, col=0)

        vs_lbl = tk.Label(file_row, text="vs", bg=T["BG"], fg=T["TEXT_DIM"],
                          font=("Segoe UI", 12))
        vs_lbl.grid(row=0, column=1, padx=20, rowspan=2)
        self._reg(vs_lbl, "DIM_LBL")

        self._build_file_picker(file_row, "File 2", self._file2,
                                self._word_count2, self._pick_file2, col=2)

        btn_frame = tk.Frame(file_row, bg=T["BG"])
        btn_frame.grid(row=0, column=4, rowspan=2, padx=(20, 0), sticky="ns")
        self._reg(btn_frame, "BG")
        ttk.Button(btn_frame, text="Compare ->", command=self._compare).pack(pady=(2, 6))
        ttk.Button(btn_frame, text="Clear", command=self._clear,
                   style="Ghost.TButton").pack()

        # ── Separator ────────────────────────────────────────────────────────
        sep2 = tk.Frame(self, bg=T["BORDER"], height=1)
        sep2.pack(fill="x")
        self._reg(sep2, "BORDER_LINE")

        # ── Legend ───────────────────────────────────────────────────────────
        leg = tk.Frame(self, bg=T["BG"], pady=8, padx=20)
        leg.pack(fill="x")
        self._reg(leg, "BG")

        self._build_legend_pill(leg, "  Added / Changed  ",   "ADD")
        self._build_legend_pill(leg, "  Removed / Changed  ", "DEL")
        self._build_legend_pill(leg, "  Word-level add  ",    "WORD_ADD")
        self._build_legend_pill(leg, "  Word-level del  ",    "WORD_DEL")

        unch_lbl = tk.Label(leg, text="(unchanged lines have no highlight)",
                            bg=T["BG"], fg=T["TEXT_DIM"], font=FONT_LABEL)
        unch_lbl.pack(side="left", padx=(14, 0))
        self._reg(unch_lbl, "DIM_LBL")

        # ── Diff area ─────────────────────────────────────────────────────────
        self._diff_frame = tk.Frame(self, bg=T["BG"])
        self._diff_frame.pack(fill="both", expand=True)
        self._reg(self._diff_frame, "BG")
        self._build_side_view()

        # ── Status bar ────────────────────────────────────────────────────────
        sep3 = tk.Frame(self, bg=T["BORDER"], height=1)
        sep3.pack(fill="x")
        self._reg(sep3, "BORDER_LINE")

        self._status_bar = tk.Frame(self, bg=T["SURFACE"], pady=5, padx=16)
        self._status_bar.pack(fill="x")
        self._reg(self._status_bar, "SURFACE")

        self._status_lbl = tk.Label(self._status_bar, textvariable=self._status,
                                    bg=T["SURFACE"], fg=T["TEXT_DIM"], font=FONT_LABEL)
        self._status_lbl.pack(side="left")
        self._reg(self._status_lbl, "STATUS_LBL")

    def _build_legend_pill(self, parent, text, role):
        T = self._T
        bg = T[role + "_BG"]
        fg = T[role + "_FG"]
        frame = tk.Frame(parent, bg=bg, padx=6, pady=2)
        frame.pack(side="left", padx=(0, 6))
        lbl = tk.Label(frame, text=text, bg=bg, fg=fg, font=FONT_LABEL)
        lbl.pack()
        self._pill_widgets.append((frame, lbl, role))

    def _build_file_picker(self, parent, label, var, count_var, cmd, col):
        T = self._T
        hdr = tk.Label(parent, text=label, bg=T["BG"], fg=T["TEXT_DIM"],
                       font=("Segoe UI", 9, "bold"))
        hdr.grid(row=0, column=col, sticky="w")
        self._reg(hdr, "DIM_LBL")

        row = tk.Frame(parent, bg=T["BG"])
        row.grid(row=1, column=col, sticky="ew", pady=(2, 0))
        row.columnconfigure(0, weight=1)
        self._reg(row, "BG")

        entry = tk.Entry(row, textvariable=var,
                         bg=T["ENTRY_BG"], fg=T["TEXT"],
                         insertbackground=T["ACCENT"],
                         relief="flat", font=("Segoe UI", 9), bd=0,
                         highlightthickness=1,
                         highlightbackground=T["BORDER"],
                         highlightcolor=T["ACCENT"])
        entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 6))
        self._entry_widgets.append(entry)

        ttk.Button(row, text="Browse", command=cmd,
                   style="Ghost.TButton").grid(row=0, column=1)

        count_lbl = ttk.Label(row, textvariable=count_var, style="Count.TLabel")
        count_lbl.grid(row=0, column=2, padx=(6, 0))

    # ─────────────────────────────────────────────────────────────────────────
    # Diff pane builders
    # ─────────────────────────────────────────────────────────────────────────
    def _build_side_view(self):
        self._text_widgets.clear()
        for w in self._diff_frame.winfo_children():
            w.destroy()

        T = self._T
        outer = tk.Frame(self._diff_frame, bg=T["BG"])
        outer.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self._reg(outer, "BG")
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(1, weight=1)

        for col, txt in enumerate(["File 1", "File 2"]):
            h = tk.Frame(outer, bg=T["SURFACE2"], pady=6, padx=10)
            pad = (0, 4) if col == 0 else (4, 0)
            h.grid(row=0, column=col, sticky="ew", padx=pad, pady=(0, 2))
            self._reg(h, "SURFACE2")
            lbl = tk.Label(h, text=txt, bg=T["SURFACE2"], fg=T["ACCENT2"],
                           font=("Segoe UI", 9, "bold"))
            lbl.pack(side="left")
            self._reg(lbl, "SURFACE_ACCENT_LBL")

        left_frame  = tk.Frame(outer, bg=T["BG"])
        right_frame = tk.Frame(outer, bg=T["BG"])
        left_frame.grid(row=1,  column=0, sticky="nsew", padx=(0, 4))
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 0))
        self._reg(left_frame,  "BG")
        self._reg(right_frame, "BG")
        for f in (left_frame, right_frame):
            f.rowconfigure(0, weight=1)
            f.columnconfigure(0, weight=1)

        yscroll   = ttk.Scrollbar(outer, orient="vertical")
        xscroll_l = ttk.Scrollbar(left_frame,  orient="horizontal")
        xscroll_r = ttk.Scrollbar(right_frame, orient="horizontal")
        yscroll.grid(row=1, column=2, sticky="ns")

        self._txt_left  = self._make_text(left_frame,  xscroll_l,
                                          yscrollcommand=self._sync_scroll_y)
        self._txt_right = self._make_text(right_frame, xscroll_r,
                                          yscrollcommand=self._sync_scroll_y)
        xscroll_l.config(command=self._txt_left.xview)
        xscroll_r.config(command=self._txt_right.xview)
        yscroll.config(command=self._scroll_both_y)
        xscroll_l.grid(row=1, column=0, sticky="ew")
        xscroll_r.grid(row=1, column=0, sticky="ew")
        self._yscroll = yscroll

        self._configure_tags(self._txt_left)
        self._configure_tags(self._txt_right)
        self._text_widgets.extend([self._txt_left, self._txt_right])

    def _build_unified_view(self):
        self._text_widgets.clear()
        for w in self._diff_frame.winfo_children():
            w.destroy()

        T = self._T
        outer = tk.Frame(self._diff_frame, bg=T["BG"])
        outer.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self._reg(outer, "BG")
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        h = tk.Frame(outer, bg=T["SURFACE2"], pady=6, padx=10)
        h.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 2))
        self._reg(h, "SURFACE2")
        lbl = tk.Label(h, text="Unified Diff  (- removed  + added)",
                       bg=T["SURFACE2"], fg=T["ACCENT2"], font=("Segoe UI", 9, "bold"))
        lbl.pack(side="left")
        self._reg(lbl, "SURFACE_ACCENT_LBL")

        uni_frame = tk.Frame(outer, bg=T["BG"])
        uni_frame.grid(row=1, column=0, sticky="nsew")
        uni_frame.rowconfigure(0, weight=1)
        uni_frame.columnconfigure(0, weight=1)
        self._reg(uni_frame, "BG")

        yscroll = ttk.Scrollbar(outer, orient="vertical")
        xscroll = ttk.Scrollbar(uni_frame, orient="horizontal")
        yscroll.grid(row=1, column=1, sticky="ns")

        self._txt_unified = self._make_text(uni_frame, xscroll,
                                            yscrollcommand=yscroll.set)
        yscroll.config(command=self._txt_unified.yview)
        xscroll.config(command=self._txt_unified.xview)
        xscroll.grid(row=1, column=0, sticky="ew")

        self._configure_tags(self._txt_unified)
        self._text_widgets.append(self._txt_unified)

    def _make_text(self, parent, xscroll, yscrollcommand=None):
        T = self._T
        t = tk.Text(parent,
                    bg=T["SURFACE"], fg=T["SAME_FG"],
                    insertbackground=T["ACCENT"],
                    relief="flat", bd=0, font=FONT_MONO,
                    wrap="none", state="disabled", cursor="arrow",
                    selectbackground=T["BORDER"], selectforeground=T["TEXT"],
                    xscrollcommand=xscroll.set,
                    yscrollcommand=yscrollcommand,
                    highlightthickness=1,
                    highlightbackground=T["BORDER"],
                    highlightcolor=T["ACCENT"],
                    padx=8, pady=6, spacing1=1, spacing3=1)
        t.grid(row=0, column=0, sticky="nsew")
        return t

    def _configure_tags(self, t):
        T = self._T
        t.tag_configure("same",     foreground=T["SAME_FG"])
        t.tag_configure("add_line", background=T["ADD_BG"],  foreground=T["ADD_FG"])
        t.tag_configure("del_line", background=T["DEL_BG"],  foreground=T["DEL_FG"])
        t.tag_configure("add_word", background=T["WORD_ADD"],foreground=T["WORD_TXT_ADD"])
        t.tag_configure("del_word", background=T["WORD_DEL"],foreground=T["WORD_TXT_DEL"])
        t.tag_configure("ln",       foreground=T["TEXT_DIM"], font=FONT_COUNT)

    # ─────────────────────────────────────────────────────────────────────────
    # Scroll sync
    # ─────────────────────────────────────────────────────────────────────────
    def _sync_scroll_y(self, *args):
        self._yscroll.set(*args)
        if hasattr(self, "_txt_left"):  self._txt_left.yview_moveto(args[0])
        if hasattr(self, "_txt_right"): self._txt_right.yview_moveto(args[0])

    def _scroll_both_y(self, *args):
        if hasattr(self, "_txt_left"):  self._txt_left.yview(*args)
        if hasattr(self, "_txt_right"): self._txt_right.yview(*args)

    # ─────────────────────────────────────────────────────────────────────────
    # File picking
    # ─────────────────────────────────────────────────────────────────────────
    def _pick(self, var, count_var):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt *.md *.csv *.log *.py *.js *.html"),
                       ("All files", "*.*")])
        if path:
            var.set(path)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    words = f.read().split()
                count_var.set(f"{len(words):,} words")
            except Exception:
                count_var.set("?")

    def _pick_file1(self): self._pick(self._file1, self._word_count1)
    def _pick_file2(self): self._pick(self._file2, self._word_count2)

    # ─────────────────────────────────────────────────────────────────────────
    # Mode switch
    # ─────────────────────────────────────────────────────────────────────────
    def _set_mode(self, mode):
        self._diff_mode.set(mode)
        if mode == "side":
            self._btn_side.configure(style="Active.Seg.TButton")
            self._btn_unified.configure(style="Seg.TButton")
            self._build_side_view()
        else:
            self._btn_side.configure(style="Seg.TButton")
            self._btn_unified.configure(style="Active.Seg.TButton")
            self._build_unified_view()
        self._status.set("View changed. Press Compare to refresh results.")

    # ─────────────────────────────────────────────────────────────────────────
    # Clear
    # ─────────────────────────────────────────────────────────────────────────
    def _clear(self):
        self._file1.set("")
        self._file2.set("")
        self._word_count1.set("")
        self._word_count2.set("")
        self._set_mode("side")
        self._status.set("Cleared. Load two files and press Compare.")

    # ─────────────────────────────────────────────────────────────────────────
    # Compare
    # ─────────────────────────────────────────────────────────────────────────
    def _compare(self):
        p1, p2 = self._file1.get().strip(), self._file2.get().strip()
        if not p1 or not p2:
            self._status.set("Warning: Please select both files first.")
            return
        try:
            with open(p1, "r", encoding="utf-8", errors="replace") as f:
                lines1 = f.readlines()
            with open(p2, "r", encoding="utf-8", errors="replace") as f:
                lines2 = f.readlines()
        except Exception as e:
            self._status.set(f"Error reading files: {e}")
            return

        if self._diff_mode.get() == "side":
            self._render_side(lines1, lines2)
        else:
            self._render_unified(lines1, lines2)

    # ─────────────────────────────────────────────────────────────────────────
    # Word-level diff
    # ─────────────────────────────────────────────────────────────────────────
    def _word_diff(self, a, b):
        wa = a.split()
        wb = b.split()
        sm = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
        result_a, result_b = [], []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            seg_a = (" ".join(wa[i1:i2]) + " ") if i2 > i1 else ""
            seg_b = (" ".join(wb[j1:j2]) + " ") if j2 > j1 else ""
            if op == "equal":
                if seg_a: result_a.append(("same", seg_a))
                if seg_b: result_b.append(("same", seg_b))
            elif op == "insert":
                if seg_b: result_b.append(("add_word", seg_b))
            elif op == "delete":
                if seg_a: result_a.append(("del_word", seg_a))
            elif op == "replace":
                if seg_a: result_a.append(("del_word", seg_a))
                if seg_b: result_b.append(("add_word", seg_b))
        return result_a, result_b

    # ─────────────────────────────────────────────────────────────────────────
    # Side-by-side renderer
    # ─────────────────────────────────────────────────────────────────────────
    def _render_side(self, lines1, lines2):
        tl, tr = self._txt_left, self._txt_right
        for t in (tl, tr):
            t.config(state="normal")
            t.delete("1.0", "end")

        sm = difflib.SequenceMatcher(None, lines1, lines2, autojunk=False)
        changed = 0

        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    tl.insert("end", f"{ln:>4}  ", "ln")
                    tl.insert("end", line.rstrip("\n") + "\n", "same")
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    tr.insert("end", f"{ln:>4}  ", "ln")
                    tr.insert("end", line.rstrip("\n") + "\n", "same")

            elif op == "replace":
                max_len = max(i2 - i1, j2 - j1)
                l_lines = lines1[i1:i2]
                r_lines = lines2[j1:j2]
                for k in range(max_len):
                    changed += 1
                    if k < len(l_lines):
                        ln     = i1 + k + 1
                        line_a = l_lines[k]
                        if k < len(r_lines):
                            line_b = r_lines[k]
                            parts_a, _ = self._word_diff(line_a.rstrip("\n"),
                                                          line_b.rstrip("\n"))
                            tl.insert("end", f"{ln:>4}  ", "ln")
                            for tag, seg in parts_a:
                                tl.insert("end", seg, tag)
                            tl.insert("end", "\n")
                        else:
                            tl.insert("end", f"{ln:>4}  ", "ln")
                            tl.insert("end", line_a.rstrip("\n") + "\n", "del_line")
                    else:
                        tl.insert("end", "       \n", "same")

                    if k < len(r_lines):
                        ln     = j1 + k + 1
                        line_b = r_lines[k]
                        if k < len(l_lines):
                            line_a = l_lines[k]
                            _, parts_b = self._word_diff(line_a.rstrip("\n"),
                                                          line_b.rstrip("\n"))
                            tr.insert("end", f"{ln:>4}  ", "ln")
                            for tag, seg in parts_b:
                                tr.insert("end", seg, tag)
                            tr.insert("end", "\n")
                        else:
                            tr.insert("end", f"{ln:>4}  ", "ln")
                            tr.insert("end", line_b.rstrip("\n") + "\n", "add_line")
                    else:
                        tr.insert("end", "       \n", "same")

            elif op == "delete":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    tl.insert("end", f"{ln:>4}  ", "ln")
                    tl.insert("end", line.rstrip("\n") + "\n", "del_line")
                    tr.insert("end", "       \n", "same")
                changed += i2 - i1

            elif op == "insert":
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    tr.insert("end", f"{ln:>4}  ", "ln")
                    tr.insert("end", line.rstrip("\n") + "\n", "add_line")
                    tl.insert("end", "       \n", "same")
                changed += j2 - j1

        for t in (tl, tr):
            t.config(state="disabled")

        total = max(len(lines1), len(lines2))
        pct   = 100 * changed / total if total else 0
        self._status.set(
            f"Done  |  {changed} changed lines  |  {total} total  |  "
            f"{pct:.1f}% differ  |  "
            f"File 1: {len(lines1)} lines   File 2: {len(lines2)} lines")

    # ─────────────────────────────────────────────────────────────────────────
    # Unified renderer
    # ─────────────────────────────────────────────────────────────────────────
    def _render_unified(self, lines1, lines2):
        t = self._txt_unified
        t.config(state="normal")
        t.delete("1.0", "end")

        sm      = difflib.SequenceMatcher(None, lines1, lines2, autojunk=False)
        changed = 0

        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    t.insert("end", f"{ln:>4}   ", "ln")
                    t.insert("end", "  " + line.rstrip("\n") + "\n", "same")
            elif op == "replace":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    t.insert("end", f"{ln:>4} - ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "del_line")
                    changed += 1
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    t.insert("end", f"{ln:>4} + ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "add_line")
            elif op == "delete":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    t.insert("end", f"{ln:>4} - ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "del_line")
                    changed += 1
            elif op == "insert":
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    t.insert("end", f"{ln:>4} + ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "add_line")
                    changed += 1

        t.config(state="disabled")
        total = max(len(lines1), len(lines2))
        pct   = 100 * changed / total if total else 0
        self._status.set(
            f"Done  |  {changed} changed lines  |  {total} total  |  {pct:.1f}% differ")


if __name__ == "__main__":
    app = DiffApp()
    app.mainloop()