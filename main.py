import tkinter as tk
from tkinter import ttk, filedialog, font
import difflib
import os

# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#0f0f14"
SURFACE   = "#1a1a24"
SURFACE2  = "#22222f"
BORDER    = "#2e2e40"
ACCENT    = "#7c6af7"
ACCENT2   = "#a78bfa"
TEXT      = "#e2e1f0"
TEXT_DIM  = "#6b6a82"
ADD_BG    = "#1a2e1a"
ADD_FG    = "#6ee06e"
DEL_BG    = "#2e1a1a"
DEL_FG    = "#f47a7a"
SAME_FG   = "#9997b8"
WORD_ADD  = "#1e3d1e"
WORD_DEL  = "#3d1e1e"
WORD_TXT_ADD = "#aaf0aa"
WORD_TXT_DEL = "#f0aaaa"

FONT_MONO = ("Courier New", 11)
FONT_UI   = ("Segoe UI", 10)
FONT_TITLE= ("Segoe UI", 13, "bold")
FONT_LABEL= ("Segoe UI", 9)
FONT_COUNT= ("Courier New", 9)


class DiffApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Diff — Word-Level Highlighter")
        self.configure(bg=BG)
        self.geometry("1400x860")
        self.minsize(900, 600)

        self._file1 = tk.StringVar(value="")
        self._file2 = tk.StringVar(value="")
        self._word_count1 = tk.StringVar(value="")
        self._word_count2 = tk.StringVar(value="")
        self._status   = tk.StringVar(value="Load two files and press Compare")
        self._diff_mode = tk.StringVar(value="side")   # "side" | "unified"

        self._build_ui()
        self._apply_style()

    # ── Style ─────────────────────────────────────────────────────────────────
    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",     background=BG)
        s.configure("TLabel",     background=BG, foreground=TEXT, font=FONT_UI)
        s.configure("Dim.TLabel", background=BG, foreground=TEXT_DIM, font=FONT_LABEL)
        s.configure("Title.TLabel",background=BG, foreground=ACCENT2, font=FONT_TITLE)
        s.configure("Count.TLabel",background=SURFACE2, foreground=ACCENT2, font=FONT_COUNT,
                    padding=(8,3))
        s.configure("TButton", background=ACCENT, foreground="#ffffff",
                    font=("Segoe UI", 10, "bold"), borderwidth=0, focusthickness=0,
                    padding=(14, 7))
        s.map("TButton",
              background=[("active", ACCENT2), ("pressed", "#5b4ed4")],
              foreground=[("active", "#ffffff")])
        s.configure("Ghost.TButton", background=SURFACE2, foreground=TEXT_DIM,
                    font=("Segoe UI", 9), borderwidth=0, padding=(10, 5))
        s.map("Ghost.TButton",
              background=[("active", BORDER)],
              foreground=[("active", TEXT)])
        s.configure("Seg.TButton", background=SURFACE2, foreground=TEXT_DIM,
                    font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(10, 5))
        s.map("Seg.TButton",
              background=[("active", ACCENT)],
              foreground=[("active", "#ffffff")])
        s.configure("Active.Seg.TButton", background=ACCENT, foreground="#ffffff",
                    font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(10, 5))
        s.configure("TScrollbar", background=SURFACE2, troughcolor=SURFACE,
                    borderwidth=0, arrowsize=12)
        s.map("TScrollbar", background=[("active", BORDER)])

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg=BG, pady=14, padx=20)
        top.pack(fill="x")
        tk.Label(top, text="⟨⟩ Diff", bg=BG, fg=ACCENT2,
                 font=("Courier New", 18, "bold")).pack(side="left")
        tk.Label(top, text=" Word-Level File Comparison", bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 11)).pack(side="left", padx=(4,0))

        # Mode toggle
        tog = tk.Frame(top, bg=BG)
        tog.pack(side="right", padx=(0,10))
        tk.Label(tog, text="View:", bg=BG, fg=TEXT_DIM, font=FONT_LABEL).pack(side="left", padx=(0,6))
        self._btn_side    = ttk.Button(tog, text="Side by Side", style="Active.Seg.TButton",
                                       command=lambda: self._set_mode("side"))
        self._btn_unified = ttk.Button(tog, text="Unified",     style="Seg.TButton",
                                       command=lambda: self._set_mode("unified"))
        self._btn_side.pack(side="left")
        self._btn_unified.pack(side="left", padx=(2,0))

        # Separator line
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # File picker row
        file_row = tk.Frame(self, bg=BG, pady=12, padx=20)
        file_row.pack(fill="x")
        file_row.columnconfigure(0, weight=1)
        file_row.columnconfigure(1, weight=0)
        file_row.columnconfigure(2, weight=1)
        file_row.columnconfigure(3, weight=0)
        file_row.columnconfigure(4, weight=0)

        self._build_file_picker(file_row, "File 1", self._file1, self._word_count1,
                                self._pick_file1, col=0)
        tk.Label(file_row, text="vs", bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 12)).grid(row=0, column=1, padx=20, rowspan=2)
        self._build_file_picker(file_row, "File 2", self._file2, self._word_count2,
                                self._pick_file2, col=2)

        btn_frame = tk.Frame(file_row, bg=BG)
        btn_frame.grid(row=0, column=4, rowspan=2, padx=(20,0), sticky="ns")
        ttk.Button(btn_frame, text="Compare →", command=self._compare).pack(pady=(2,6))
        ttk.Button(btn_frame, text="Clear",     command=self._clear, style="Ghost.TButton").pack()

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Legend
        leg = tk.Frame(self, bg=BG, pady=8, padx=20)
        leg.pack(fill="x")
        self._legend_pill(leg, "  Added / Changed  ", ADD_BG, ADD_FG)
        self._legend_pill(leg, "  Removed / Changed  ", DEL_BG, DEL_FG)
        self._legend_pill(leg, "  Word-level add  ", WORD_ADD, WORD_TXT_ADD)
        self._legend_pill(leg, "  Word-level del  ", WORD_DEL, WORD_TXT_DEL)
        tk.Label(leg, text="(unchanged lines have no highlight)",
                 bg=BG, fg=TEXT_DIM, font=FONT_LABEL).pack(side="left", padx=(14,0))

        # Diff area
        self._diff_frame = tk.Frame(self, bg=BG)
        self._diff_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self._build_side_view()

        # Status bar
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        status_bar = tk.Frame(self, bg=SURFACE, pady=5, padx=16)
        status_bar.pack(fill="x")
        tk.Label(status_bar, textvariable=self._status, bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_LABEL).pack(side="left")

    def _legend_pill(self, parent, text, bg, fg):
        pill = tk.Frame(parent, bg=bg, padx=6, pady=2)
        pill.pack(side="left", padx=(0,6))
        tk.Label(pill, text=text, bg=bg, fg=fg, font=FONT_LABEL).pack()

    def _build_file_picker(self, parent, label, var, count_var, cmd, col):
        tk.Label(parent, text=label, bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=col, sticky="w")
        row = tk.Frame(parent, bg=BG)
        row.grid(row=1, column=col, sticky="ew", pady=(2,0))
        row.columnconfigure(0, weight=1)
        path_box = tk.Entry(row, textvariable=var, bg=SURFACE2, fg=TEXT,
                            insertbackground=ACCENT, relief="flat",
                            font=("Segoe UI", 9), bd=0, highlightthickness=1,
                            highlightbackground=BORDER, highlightcolor=ACCENT)
        path_box.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0,6))
        ttk.Button(row, text="Browse", command=cmd, style="Ghost.TButton").grid(row=0, column=1)
        count_lbl = ttk.Label(row, textvariable=count_var, style="Count.TLabel")
        count_lbl.grid(row=0, column=2, padx=(6,0))

    # ── Side-by-side view ─────────────────────────────────────────────────────
    def _build_side_view(self):
        for w in self._diff_frame.winfo_children():
            w.destroy()

        outer = tk.Frame(self._diff_frame, bg=BG)
        outer.pack(fill="both", expand=True, padx=12, pady=(6,12))
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(1, weight=1)

        # Headers
        for col, txt in enumerate(["File 1", "File 2"]):
            h = tk.Frame(outer, bg=SURFACE2, pady=6, padx=10)
            h.grid(row=0, column=col, sticky="ew", padx=(0,4) if col==0 else (4,0), pady=(0,2))
            tk.Label(h, text=txt, bg=SURFACE2, fg=ACCENT2,
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        # Text areas + shared scrollbar
        left_frame  = tk.Frame(outer, bg=BG)
        right_frame = tk.Frame(outer, bg=BG)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0,4))
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(4,0))
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        yscroll = ttk.Scrollbar(outer, orient="vertical")
        xscroll_l = ttk.Scrollbar(left_frame,  orient="horizontal")
        xscroll_r = ttk.Scrollbar(right_frame, orient="horizontal")
        yscroll.grid(row=1, column=2, sticky="ns")

        self._txt_left = self._make_text(left_frame, xscroll_l,
                                         yscrollcommand=self._sync_scroll_y)
        self._txt_right= self._make_text(right_frame, xscroll_r,
                                         yscrollcommand=self._sync_scroll_y)

        xscroll_l.config(command=self._txt_left.xview)
        xscroll_r.config(command=self._txt_right.xview)
        yscroll.config(command=self._scroll_both_y)
        xscroll_l.grid(row=1, column=0, sticky="ew")
        xscroll_r.grid(row=1, column=0, sticky="ew")

        self._yscroll = yscroll
        self._configure_tags(self._txt_left)
        self._configure_tags(self._txt_right)

    def _build_unified_view(self):
        for w in self._diff_frame.winfo_children():
            w.destroy()

        outer = tk.Frame(self._diff_frame, bg=BG)
        outer.pack(fill="both", expand=True, padx=12, pady=(6,12))
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        h = tk.Frame(outer, bg=SURFACE2, pady=6, padx=10)
        h.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,2))
        tk.Label(h, text="Unified Diff  (− removed · + added)",
                 bg=SURFACE2, fg=ACCENT2, font=("Segoe UI", 9, "bold")).pack(side="left")

        uni_frame = tk.Frame(outer, bg=BG)
        uni_frame.grid(row=1, column=0, sticky="nsew")
        uni_frame.rowconfigure(0, weight=1)
        uni_frame.columnconfigure(0, weight=1)

        yscroll  = ttk.Scrollbar(outer, orient="vertical")
        xscroll  = ttk.Scrollbar(uni_frame, orient="horizontal")
        yscroll.grid(row=1, column=1, sticky="ns")

        self._txt_unified = self._make_text(uni_frame, xscroll,
                                            yscrollcommand=yscroll.set)
        yscroll.config(command=self._txt_unified.yview)
        xscroll.config(command=self._txt_unified.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        self._configure_tags(self._txt_unified)

    def _make_text(self, parent, xscroll, yscrollcommand=None):
        t = tk.Text(parent, bg=SURFACE, fg=SAME_FG, insertbackground=ACCENT,
                    relief="flat", bd=0, font=FONT_MONO,
                    wrap="none", state="disabled", cursor="arrow",
                    selectbackground=BORDER, selectforeground=TEXT,
                    xscrollcommand=xscroll.set,
                    yscrollcommand=yscrollcommand,
                    highlightthickness=1, highlightbackground=BORDER,
                    highlightcolor=ACCENT, padx=8, pady=6,
                    spacing1=1, spacing3=1)
        t.grid(row=0, column=0, sticky="nsew")
        return t

    def _configure_tags(self, t):
        t.tag_configure("same",     foreground=SAME_FG)
        t.tag_configure("add_line", background=ADD_BG,  foreground=ADD_FG)
        t.tag_configure("del_line", background=DEL_BG,  foreground=DEL_FG)
        t.tag_configure("add_word", background=WORD_ADD, foreground=WORD_TXT_ADD)
        t.tag_configure("del_word", background=WORD_DEL, foreground=WORD_TXT_DEL)
        t.tag_configure("ln",       foreground=TEXT_DIM, font=FONT_COUNT)

    # ── Scroll sync ───────────────────────────────────────────────────────────
    def _sync_scroll_y(self, *args):
        self._yscroll.set(*args)
        if hasattr(self, "_txt_left")  and str(self._txt_left.yview())  != str(args):
            self._txt_left.yview_moveto(args[0])
        if hasattr(self, "_txt_right") and str(self._txt_right.yview()) != str(args):
            self._txt_right.yview_moveto(args[0])

    def _scroll_both_y(self, *args):
        if hasattr(self, "_txt_left"):  self._txt_left.yview(*args)
        if hasattr(self, "_txt_right"): self._txt_right.yview(*args)

    # ── File picking ──────────────────────────────────────────────────────────
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

    # ── Mode switch ───────────────────────────────────────────────────────────
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
        self._status.set("Load two files and press Compare")

    # ── Clear ─────────────────────────────────────────────────────────────────
    def _clear(self):
        self._file1.set("")
        self._file2.set("")
        self._word_count1.set("")
        self._word_count2.set("")
        self._set_mode("side")
        self._status.set("Cleared. Load two files and press Compare.")

    # ── Compare ───────────────────────────────────────────────────────────────
    def _compare(self):
        p1, p2 = self._file1.get().strip(), self._file2.get().strip()
        if not p1 or not p2:
            self._status.set("⚠  Please select both files first.")
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

    # ── Word-level diff helper ────────────────────────────────────────────────
    def _word_diff(self, a, b):
        """
        Returns list of (tag, text) tuples for inline word-level diff.
        tag is 'same', 'add_word', 'del_word'.
        """
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

    # ── Side-by-side renderer ─────────────────────────────────────────────────
    def _render_side(self, lines1, lines2):
        tl, tr = self._txt_left, self._txt_right
        for t in (tl, tr):
            t.config(state="normal")
            t.delete("1.0", "end")

        sm = difflib.SequenceMatcher(None, lines1, lines2, autojunk=False)
        changed = replaced = 0

        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    tl.insert("end", f"{ln:>4}  ", "ln")
                    tl.insert("end", line.rstrip("\n") + "\n", "same")
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    tr.insert("end", f"{ln:>4}  ", "ln")
                    tr.insert("end", line.rstrip("\n") + "\n", "same")

            elif op == "replace":
                max_len = max(i2-i1, j2-j1)
                l_lines = lines1[i1:i2]
                r_lines = lines2[j1:j2]
                for k in range(max_len):
                    changed += 1
                    if k < len(l_lines):
                        ln = i1 + k + 1
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
                        replaced += 1
                    else:
                        tl.insert("end", "       \n", "same")

                    if k < len(r_lines):
                        ln = j1 + k + 1
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
                changed += i2-i1

            elif op == "insert":
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    tr.insert("end", f"{ln:>4}  ", "ln")
                    tr.insert("end", line.rstrip("\n") + "\n", "add_line")
                    tl.insert("end", "       \n", "same")
                changed += j2-j1

        for t in (tl, tr):
            t.config(state="disabled")

        total = max(len(lines1), len(lines2))
        pct = 100 * changed / total if total else 0
        self._status.set(
            f"✓  Done  ·  {changed} changed lines  ·  {total} total  ·  "
            f"{pct:.1f}% differ  ·  "
            f"File 1: {len(lines1)} lines   File 2: {len(lines2)} lines")

    # ── Unified renderer ──────────────────────────────────────────────────────
    def _render_unified(self, lines1, lines2):
        t = self._txt_unified
        t.config(state="normal")
        t.delete("1.0", "end")

        sm = difflib.SequenceMatcher(None, lines1, lines2, autojunk=False)
        changed = 0

        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    t.insert("end", f"{ln:>4}   ", "ln")
                    t.insert("end", "  " + line.rstrip("\n") + "\n", "same")

            elif op == "replace":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    t.insert("end", f"{ln:>4} − ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "del_line")
                    changed += 1
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    t.insert("end", f"{ln:>4} + ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "add_line")

            elif op == "delete":
                for ln, line in enumerate(lines1[i1:i2], start=i1+1):
                    t.insert("end", f"{ln:>4} − ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "del_line")
                    changed += 1

            elif op == "insert":
                for ln, line in enumerate(lines2[j1:j2], start=j1+1):
                    t.insert("end", f"{ln:>4} + ", "ln")
                    t.insert("end", line.rstrip("\n") + "\n", "add_line")
                    changed += 1

        t.config(state="disabled")
        total = max(len(lines1), len(lines2))
        pct = 100 * changed / total if total else 0
        self._status.set(
            f"✓  Done  ·  {changed} changed lines  ·  {total} total  ·  {pct:.1f}% differ")


if __name__ == "__main__":
    app = DiffApp()
    app.mainloop()