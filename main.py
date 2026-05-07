import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime

DATA_FILE = "activity_records.json"

TIME_SEGMENTS = ["Morning", "Afternoon", "Evening"]
ACTIVITY_TYPES = [
    "Deep Work", "Creative Task", "Routine Task",
    "Physical Task", "Social / Communication", "Rest / Break"
]

TASK_DEMAND = {
    "Deep Work": 4,
    "Creative Task": 3,
    "Routine Task": 2,
    "Physical Task": 3,
    "Social / Communication": 2,
    "Rest / Break": 1
}

# ── Midnight Circadian Palette ─────────────────────────────────────────────
C = {
    "bg":         "#0D0D1A",   # deep midnight canvas
    "surface":    "#141428",   # card/panel surface
    "surface2":   "#1C1C38",   # elevated surface
    "border":     "#2A2A50",   # subtle border
    "border_hi":  "#3D3D70",   # hovered/active border
    "text":       "#E8E8F8",   # primary text
    "text_dim":   "#9090B8",   # secondary/muted text
    "text_ghost": "#555577",   # placeholder text

    # Segment identity colours (dawn → dusk)
    "morning":    "#FFB347",   # warm gold
    "afternoon":  "#FF6B47",   # energetic coral-orange
    "evening":    "#9B59B6",   # rich purple

    # Semantic
    "good":       "#3DD68C",   # fresh green
    "fair":       "#F5C842",   # amber
    "poor":       "#FF5C5C",   # red

    # Accent / CTA
    "accent":     "#FF6B47",
    "accent_hi":  "#FF8C6B",

    # Numeric energy colours (1→5)
    "e1": "#FF4444",
    "e2": "#FF8C00",
    "e3": "#F5C842",
    "e4": "#7BC67E",
    "e5": "#3DD68C",
}

ENERGY_COLORS = [C["e1"], C["e2"], C["e3"], C["e4"], C["e5"]]

SEGMENT_GRADIENT = {
    "Morning":   (C["morning"],   "#FFF0C0"),
    "Afternoon": (C["afternoon"], "#FFD0C0"),
    "Evening":   (C["evening"],   "#E0C0FF"),
}

# Segment emoji icons
SEG_ICON = {"Morning": "☀️", "Afternoon": "🌤", "Evening": "🌙"}
ACT_ICON = {
    "Deep Work": "🧠", "Creative Task": "🎨", "Routine Task": "📋",
    "Physical Task": "💪", "Social / Communication": "💬", "Rest / Break": "😴"
}
FIT_ICON = {"Good Match": "✅", "Fair Match": "⚡", "Poor Match": "❌"}

records = []


# ── File I/O ───────────────────────────────────────────────────────────────

def load_records():
    global records
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            records = [
                r for r in data
                if isinstance(r, dict)
                and {"time", "activity", "energy"}.issubset(r.keys())
            ]
        except Exception:
            records = []


def save_records():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)


# ── Analysis ───────────────────────────────────────────────────────────────

def classify_energy(avg):
    if avg >= 4.2:  return "Peak"
    if avg >= 3.5:  return "High"
    if avg >= 2.5:  return "Moderate"
    if avg >= 1.8:  return "Low"
    return "Depleted"


def energy_color(val):
    """Return color for an energy value 1–5."""
    idx = max(0, min(4, int(val) - 1))
    return ENERGY_COLORS[idx]


def task_fit(activity, energy):
    demand = TASK_DEMAND.get(activity, 2)
    if energy >= demand:     return "Good Match"
    if energy == demand - 1: return "Fair Match"
    return "Poor Match"


def get_averages():
    grouped = {s: [] for s in TIME_SEGMENTS}
    for r in records:
        grouped[r["time"]].append(int(r["energy"]))
    return {s: sum(v) / len(v) for s, v in grouped.items() if v}


def get_fit_counts():
    counts = {"Good Match": 0, "Fair Match": 0, "Poor Match": 0}
    for r in records:
        counts[task_fit(r["activity"], int(r["energy"]))] += 1
    return counts


def analyze_data():
    if not records:
        return None
    avgs = get_averages()
    if not avgs:
        return None
    peak   = max(avgs, key=avgs.get)
    lowest = min(avgs, key=avgs.get)
    fits   = get_fit_counts()

    if peak == lowest:
        reco = (f"Your logs are focused on {peak}. "
                "Log from other time windows to unlock comparative insights.")
    else:
        reco = (f"Your energy peaks at {peak} — this is your prime window for deep, "
                f"demanding work.\n\n"
                f"Reserve {lowest} for lighter tasks, admin, or intentional recovery. "
                "Aligning effort with energy is the simplest productivity upgrade.")

    return peak, lowest, avgs, fits, reco


# ── Widget Helpers ─────────────────────────────────────────────────────────

def card_frame(parent, padx=16, pady=14):
    return tk.Frame(parent, bg=C["surface"],
                    padx=padx, pady=pady,
                    highlightbackground=C["border"],
                    highlightthickness=1)


def section_label(parent, text):
    tk.Label(parent, text=text,
             font=("Consolas", 11, "bold"),
             bg=C["surface"], fg=C["text_dim"],
             letter_spacing=2).pack(anchor="w", pady=(0, 8))


def divider(parent):
    tk.Frame(parent, height=1, bg=C["border"]).pack(fill="x", pady=8)


def badge(parent, text, color):
    """Small coloured pill label."""
    tk.Label(parent, text=text,
             font=("Segoe UI", 8, "bold"),
             bg=color, fg="#0D0D1A",
             padx=6, pady=2).pack(side="left", padx=(0, 4))


def metric_card(parent, icon, title, value="—", color=None):
    box = card_frame(parent, padx=14, pady=12)
    box.pack(side="left", fill="x", expand=True, padx=5)

    top = tk.Frame(box, bg=C["surface"])
    top.pack(fill="x")

    tk.Label(top, text=icon, font=("Segoe UI", 16),
             bg=C["surface"]).pack(side="left", padx=(0, 6))

    tk.Label(top, text=title,
             font=("Segoe UI", 9),
             bg=C["surface"], fg=C["text_dim"]).pack(side="left", anchor="s", pady=(0, 1))

    lbl = tk.Label(box, text=value,
                   font=("Consolas", 18, "bold"),
                   bg=C["surface"], fg=color or C["text"])
    lbl.pack(anchor="w", pady=(6, 0))
    return lbl


def draw_chart(canvas, averages):
    canvas.delete("all")
    w = int(canvas["width"])  if canvas["width"]  != 0 else 860
    h = int(canvas["height"]) if canvas["height"] != 0 else 200

    # Background grid lines
    for i in range(1, 6):
        x = 160 + int((i / 5) * (w - 220))
        canvas.create_line(x, 5, x, h - 30, fill=C["border"], dash=(4, 6))
        canvas.create_text(x, h - 18, text=str(i),
                           fill=C["text_ghost"], font=("Consolas", 8))

    if not averages:
        canvas.create_text(w // 2, h // 2,
                           text="No records yet — start logging!",
                           fill=C["text_dim"], font=("Segoe UI", 11))
        return

    bar_h   = 34
    spacing = 22
    max_w   = w - 280
    start_x = 155
    y       = 18

    for segment in TIME_SEGMENTS:
        avg  = averages.get(segment, 0)
        color, _ = SEGMENT_GRADIENT[segment]
        icon = SEG_ICON[segment]

        # Segment label
        canvas.create_text(10, y + bar_h // 2,
                           text=f"{icon} {segment}",
                           anchor="w",
                           fill=C["text"], font=("Segoe UI", 10, "bold"))

        # Track (background bar)
        canvas.create_rectangle(start_x, y,
                                start_x + max_w, y + bar_h,
                                fill=C["surface2"], outline=C["border"])

        if avg:
            fill_w = int((avg / 5) * max_w)

            # Segmented glow effect: 3 layered rectangles
            for offset, alpha_color in [(0, color), (3, _mix(color, C["surface2"], 0.4))]:
                canvas.create_rectangle(
                    start_x + offset, y + offset,
                    start_x + fill_w, y + bar_h - offset,
                    fill=alpha_color, outline=""
                )

            # Energy value inside bar
            label_x = start_x + fill_w - 44 if fill_w > 70 else start_x + fill_w + 6
            anchor   = "e" if fill_w > 70 else "w"
            canvas.create_text(label_x, y + bar_h // 2,
                               text=f"{avg:.1f}/5  {classify_energy(avg)}",
                               anchor=anchor,
                               fill="#0D0D1A" if fill_w > 70 else C["text"],
                               font=("Consolas", 9, "bold"))
        else:
            canvas.create_text(start_x + 10, y + bar_h // 2,
                               text="No data",
                               anchor="w",
                               fill=C["text_ghost"],
                               font=("Segoe UI", 9, "italic"))

        y += bar_h + spacing


def _mix(hex1, hex2, t):
    """Linearly interpolate between two hex colours."""
    def parse(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r1, g1, b1 = parse(hex1)
    r2, g2, b2 = parse(hex2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Main Application ───────────────────────────────────────────────────────

class CircadianApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Circadian Activity Mapper")
        self.geometry("1060x700")
        self.minsize(900, 620)
        self.configure(bg=C["bg"])

        self.time_var     = tk.StringVar()
        self.activity_var = tk.StringVar()

        self._build_styles()
        self._build_header()
        self._build_tabs()
        self._build_statusbar()

        self.refresh_records()
        self.refresh_insights()
        self.reset_analysis()

    # ── Styles ──────────────────────────────────────────────────────────────

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook",
                        background=C["bg"],
                        borderwidth=0,
                        tabmargins=[0, 0, 0, 0])

        style.configure("TNotebook.Tab",
                        background=C["surface"],
                        foreground=C["text_dim"],
                        font=("Segoe UI", 10, "bold"),
                        padding=[22, 10],
                        borderwidth=0)

        style.map("TNotebook.Tab",
                  background=[("selected", C["surface2"]), ("active", C["surface2"])],
                  foreground=[("selected", C["text"]),     ("active", C["text"])])

        style.configure("Treeview",
                        font=("Segoe UI", 9),
                        rowheight=28,
                        background=C["surface"],
                        fieldbackground=C["surface"],
                        foreground=C["text"],
                        borderwidth=0)

        style.configure("Treeview.Heading",
                        font=("Consolas", 9, "bold"),
                        background=C["surface2"],
                        foreground=C["text_dim"],
                        relief="flat",
                        borderwidth=0)

        style.map("Treeview",
                  background=[("selected", C["surface2"])],
                  foreground=[("selected", C["text"])])

        style.configure("TCombobox",
                        fieldbackground=C["surface2"],
                        background=C["surface2"],
                        foreground=C["text"],
                        selectbackground=C["surface2"],
                        selectforeground=C["text"],
                        bordercolor=C["border"],
                        arrowcolor=C["text_dim"])

        style.map("TCombobox",
                  fieldbackground=[("readonly", C["surface2"])],
                  bordercolor=[("focus", C["accent"])])

    # ── Header ──────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=28, pady=(20, 10))

        left = tk.Frame(hdr, bg=C["bg"])
        left.pack(side="left")

        tk.Label(left,
                 text="◉  CIRCADIAN ACTIVITY MAPPER",
                 font=("Consolas", 15, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")

        tk.Label(left,
                 text="Track your energy rhythms • align effort with biology",
                 font=("Segoe UI", 9),
                 bg=C["bg"], fg=C["text_dim"]).pack(anchor="w", pady=(3, 0))

        # Live clock
        self._clock_var = tk.StringVar()
        tk.Label(hdr,
                 textvariable=self._clock_var,
                 font=("Consolas", 13, "bold"),
                 bg=C["bg"], fg=C["text_dim"]).pack(side="right", anchor="e")

        self._tick_clock()

    def _tick_clock(self):
        now = datetime.now().strftime("%H:%M:%S   %a, %d %b")
        self._clock_var.set(now)
        self.after(1000, self._tick_clock)

    # ── Status Bar ──────────────────────────────────────────────────────────

    def _build_statusbar(self):
        self._status_var = tk.StringVar(value="Ready")
        bar = tk.Frame(self, bg=C["surface2"], height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(bar, textvariable=self._status_var,
                 font=("Segoe UI", 8),
                 bg=C["surface2"], fg=C["text_dim"],
                 anchor="w", padx=16).pack(fill="x")

    def _set_status(self, msg):
        self._status_var.set(f"▸  {msg}")

    # ── Tabs ────────────────────────────────────────────────────────────────

    def _build_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=24, pady=(4, 0))

        self.tab_log      = tk.Frame(self.tabs, bg=C["bg"])
        self.tab_insights = tk.Frame(self.tabs, bg=C["bg"])
        self.tab_analysis = tk.Frame(self.tabs, bg=C["bg"])

        self.tabs.add(self.tab_log,      text="  ✏  Log Activity  ")
        self.tabs.add(self.tab_insights, text="  📊  Insights  ")
        self.tabs.add(self.tab_analysis, text="  🔬  Analysis  ")

        self._build_log_tab()
        self._build_insights_tab()
        self._build_analysis_tab()

    # ── Tab 1: Log ───────────────────────────────────────────────────────────

    def _build_log_tab(self):
        root = tk.Frame(self.tab_log, bg=C["bg"])
        root.pack(fill="both", expand=True, padx=18, pady=18)

        # ── Left: Form ──────────────────────────────────────────────────────
        left = tk.Frame(root, bg=C["bg"], width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        form = card_frame(left, padx=20, pady=20)
        form.pack(fill="x")

        tk.Label(form, text="NEW ENTRY",
                 font=("Consolas", 11, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(anchor="w", pady=(0, 14))

        self._form_field(form, "⏰  Time Segment", self.time_var, TIME_SEGMENTS,
                         icon_map=SEG_ICON)
        self._form_field(form, "🎯  Activity Type", self.activity_var, ACTIVITY_TYPES)

        # Energy Scale
        tk.Label(form, text="⚡  Energy Level",
                 font=("Segoe UI", 10, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(4, 6))

        scale_frame = tk.Frame(form, bg=C["surface"])
        scale_frame.pack(fill="x")

        self.energy_scale = tk.Scale(
            scale_frame,
            from_=1, to=5, orient="horizontal",
            length=230,
            bg=C["surface"],
            troughcolor=C["surface2"],
            activebackground=C["accent"],
            fg=C["text"],
            highlightthickness=0,
            font=("Consolas", 9),
            command=self._on_scale_move
        )
        self.energy_scale.set(3)
        self.energy_scale.pack(side="left")

        # Energy colour indicator
        self._energy_dot = tk.Label(scale_frame, text="●",
                                    font=("Segoe UI", 22),
                                    bg=C["surface"],
                                    fg=ENERGY_COLORS[2])
        self._energy_dot.pack(side="left", padx=(8, 0))

        # Energy labels row
        lbl_row = tk.Frame(form, bg=C["surface"])
        lbl_row.pack(fill="x", pady=(0, 16))
        for i, lbl in enumerate(["Very Low", "", "Moderate", "", "Peak"]):
            anchor = ["w", "center", "center", "center", "e"][i]
            side   = ["left","left","left","left","right"][i]
            tk.Label(lbl_row, text=lbl,
                     font=("Segoe UI", 7),
                     bg=C["surface"],
                     fg=C["text_ghost"]).pack(side=side)

        # Energy level label
        self._energy_label = tk.Label(form, text="Energy: 3 / 5  —  Moderate",
                                      font=("Consolas", 9, "bold"),
                                      bg=C["surface"], fg=ENERGY_COLORS[2])
        self._energy_label.pack(anchor="w", pady=(0, 14))

        divider(form)

        # Add button
        tk.Button(form, text="+ ADD RECORD",
                  command=self.add_record,
                  bg=C["accent"], fg="#0D0D1A",
                  font=("Consolas", 10, "bold"),
                  relief="flat", cursor="hand2",
                  pady=11, activebackground=C["accent_hi"],
                  activeforeground="#0D0D1A").pack(fill="x")

        # ── Demand guide ────────────────────────────────────────────────────
        guide = card_frame(left, padx=18, pady=14)
        guide.pack(fill="x", pady=(12, 0))

        tk.Label(guide, text="TASK DEMAND GUIDE",
                 font=("Consolas", 8, "bold"),
                 bg=C["surface"], fg=C["text_ghost"]).pack(anchor="w", pady=(0, 6))

        for act, demand in TASK_DEMAND.items():
            row = tk.Frame(guide, bg=C["surface"])
            row.pack(fill="x", pady=1)

            tk.Label(row,
                     text=f"{ACT_ICON.get(act,'  ')}  {act}",
                     font=("Segoe UI", 8),
                     bg=C["surface"], fg=C["text_dim"]).pack(side="left")

            # Pip dots for demand level
            pip_frame = tk.Frame(row, bg=C["surface"])
            pip_frame.pack(side="right")
            for i in range(1, 6):
                col = ENERGY_COLORS[i - 1] if i <= demand else C["border"]
                tk.Label(pip_frame, text="●", font=("Segoe UI", 6),
                         bg=C["surface"], fg=col).pack(side="left")

        # ── Right: Records ──────────────────────────────────────────────────
        right = tk.Frame(root, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=(14, 0))

        rec_card = card_frame(right, padx=16, pady=14)
        rec_card.pack(fill="both", expand=True)

        # Header row
        hdr_row = tk.Frame(rec_card, bg=C["surface"])
        hdr_row.pack(fill="x", pady=(0, 10))

        tk.Label(hdr_row, text="RECORDED ENTRIES",
                 font=("Consolas", 11, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(side="left")

        tk.Button(hdr_row, text="🗑  Remove Selected",
                  command=self._delete_selected,
                  bg=C["surface2"], fg=C["poor"],
                  font=("Segoe UI", 8, "bold"),
                  relief="flat", cursor="hand2",
                  padx=10, pady=4,
                  activebackground=C["border"],
                  activeforeground=C["poor"]).pack(side="right", padx=(6, 0))

        tk.Button(hdr_row, text="⬛  Clear All",
                  command=self.clear_records,
                  bg=C["surface2"], fg=C["text_dim"],
                  font=("Segoe UI", 8, "bold"),
                  relief="flat", cursor="hand2",
                  padx=10, pady=4,
                  activebackground=C["border"],
                  activeforeground=C["text"]).pack(side="right")

        # Treeview
        columns = ("Time", "Activity", "Energy", "Task Fit", "Date")
        self.tree = ttk.Treeview(rec_card, columns=columns,
                                 show="headings", height=16)

        col_widths = {"Time": 100, "Activity": 170, "Energy": 80, "Task Fit": 110, "Date": 140}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=col_widths[col])

        # Row tags for fit colouring
        self.tree.tag_configure("good", background=C["surface"],
                                foreground=C["good"])
        self.tree.tag_configure("fair", background=C["surface"],
                                foreground=C["fair"])
        self.tree.tag_configure("poor", background=C["surface"],
                                foreground=C["poor"])
        self.tree.tag_configure("alt",  background=C["surface2"])

        scroll = ttk.Scrollbar(rec_card, orient="vertical",
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True, pady=(4, 0))
        scroll.pack(side="right", fill="y", pady=(4, 0))

    def _form_field(self, parent, label, variable, values, icon_map=None):
        tk.Label(parent, text=label,
                 font=("Segoe UI", 10, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w")

        cb = ttk.Combobox(parent, textvariable=variable,
                          values=values, state="readonly", width=30,
                          font=("Segoe UI", 9))
        cb.pack(anchor="w", pady=(5, 14))

    def _on_scale_move(self, val):
        v = int(float(val))
        labels = ["Very Low", "Low", "Moderate", "High", "Peak"]
        col = ENERGY_COLORS[v - 1]
        self._energy_dot.config(fg=col)
        self._energy_label.config(
            text=f"Energy: {v} / 5  —  {labels[v - 1]}",
            fg=col)

    # ── Tab 2: Insights ──────────────────────────────────────────────────────

    def _build_insights_tab(self):
        root = tk.Frame(self.tab_insights, bg=C["bg"])
        root.pack(fill="both", expand=True, padx=18, pady=18)

        # Metric row
        metrics_row = tk.Frame(root, bg=C["bg"])
        metrics_row.pack(fill="x", pady=(0, 14))

        self.lbl_total   = metric_card(metrics_row, "📝", "Total Records", "0", C["morning"])
        self.lbl_period  = metric_card(metrics_row, "📈", "Most Active Period", "—", C["afternoon"])
        self.lbl_avg     = metric_card(metrics_row, "⚡", "Overall Avg Energy", "—", C["good"])
        self.lbl_streak  = metric_card(metrics_row, "🔥", "Best Performing", "—", C["evening"])

        # Chart card
        chart_card = card_frame(root, padx=20, pady=18)
        chart_card.pack(fill="both", expand=True)

        tk.Label(chart_card, text="ENERGY LEVELS BY TIME SEGMENT",
                 font=("Consolas", 10, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(anchor="w", pady=(0, 12))

        self.chart = tk.Canvas(chart_card, height=220,
                               bg=C["surface"],
                               highlightthickness=0)
        self.chart.pack(fill="x")

        divider(chart_card)

        # Summary sentence
        self.state_label = tk.Label(
            chart_card,
            text="No records yet. Start logging in the first tab.",
            font=("Segoe UI", 10),
            bg=C["surface2"],
            fg=C["text"],
            wraplength=900, justify="left",
            padx=16, pady=12
        )
        self.state_label.pack(fill="x")

    # ── Tab 3: Analysis ──────────────────────────────────────────────────────

    def _build_analysis_tab(self):
        root = tk.Frame(self.tab_analysis, bg=C["bg"])
        root.pack(fill="both", expand=True, padx=18, pady=18)

        # Metric row
        metrics_row = tk.Frame(root, bg=C["bg"])
        metrics_row.pack(fill="x", pady=(0, 14))

        self.lbl_peak     = metric_card(metrics_row, "🌟", "Peak Energy Period",   "—", C["good"])
        self.lbl_low      = metric_card(metrics_row, "🌙", "Lowest Energy Period", "—", C["poor"])
        self.lbl_good_fit = metric_card(metrics_row, "✅", "Good Task Matches",    "0", C["fair"])
        self.lbl_poor_fit = metric_card(metrics_row, "❌", "Poor Task Matches",    "0", C["poor"])

        # Main analysis card
        body_card = card_frame(root, padx=20, pady=18)
        body_card.pack(fill="both", expand=True)

        # Header + run button
        hdr_row = tk.Frame(body_card, bg=C["surface"])
        hdr_row.pack(fill="x", pady=(0, 14))

        tk.Label(hdr_row, text="ENERGY PATTERN ANALYSIS",
                 font=("Consolas", 10, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(side="left")

        tk.Button(hdr_row, text="▶  RUN ANALYSIS",
                  command=self.run_analysis,
                  bg=C["accent"], fg="#0D0D1A",
                  font=("Consolas", 9, "bold"),
                  relief="flat", cursor="hand2",
                  padx=18, pady=8,
                  activebackground=C["accent_hi"],
                  activeforeground="#0D0D1A").pack(side="right")

        # Two-panel body
        panels = tk.Frame(body_card, bg=C["surface"])
        panels.pack(fill="both", expand=True)

        left_panel = tk.Frame(panels, bg=C["surface2"],
                              highlightbackground=C["border"],
                              highlightthickness=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right_panel = tk.Frame(panels, bg=C["surface2"],
                               highlightbackground=C["border"],
                               highlightthickness=1)
        right_panel.pack(side="right", fill="both", expand=True)

        self.energy_text = tk.Label(
            left_panel,
            text="Click ▶ Run Analysis to generate insights.",
            font=("Segoe UI", 10),
            bg=C["surface2"], fg=C["text"],
            justify="left", wraplength=340,
            padx=20, pady=20, anchor="nw"
        )
        self.energy_text.pack(fill="both", expand=True)

        self.reco_text = tk.Label(
            right_panel,
            text="Your personalised recommendation will appear here.",
            font=("Segoe UI", 10),
            bg=C["surface2"], fg=C["text"],
            justify="left", wraplength=340,
            padx=20, pady=20, anchor="nw"
        )
        self.reco_text.pack(fill="both", expand=True)

    # ── Actions ─────────────────────────────────────────────────────────────

    def add_record(self):
        time_seg = self.time_var.get()
        activity = self.activity_var.get()
        energy   = int(self.energy_scale.get())

        if not time_seg or not activity:
            messagebox.showerror("Missing Fields",
                                 "Please select a Time Segment and Activity Type.")
            return

        records.append({
            "time":     time_seg,
            "activity": activity,
            "energy":   energy,
            "date":     datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_records()

        self.time_var.set("")
        self.activity_var.set("")
        self.energy_scale.set(3)
        self._on_scale_move(3)

        self.refresh_records()
        self.refresh_insights()
        self.reset_analysis()

        self._set_status(
            f"Record added: {SEG_ICON.get(time_seg, '')} {time_seg} · "
            f"{ACT_ICON.get(activity, '')} {activity} · ⚡ {energy}/5"
        )

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            self._set_status("No row selected. Click a row to select it first.")
            return

        if not messagebox.askyesno("Remove Entry",
                                   f"Remove {len(selected)} selected record(s)?"):
            return

        # Remove by index (tree is in insertion order = records list order)
        indices = sorted([self.tree.index(iid) for iid in selected], reverse=True)
        for idx in indices:
            if 0 <= idx < len(records):
                records.pop(idx)

        save_records()
        self.refresh_records()
        self.refresh_insights()
        self.reset_analysis()
        self._set_status(f"Removed {len(indices)} record(s).")

    def refresh_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, r in enumerate(records):
            fit   = task_fit(r["activity"], int(r["energy"]))
            e_str = f"{r['energy']}/5"
            tag   = {"Good Match": "good", "Fair Match": "fair", "Poor Match": "poor"}[fit]
            if i % 2 == 1:
                tag = tag  # keep semantic tag; alternating done via bg in tag_configure
            self.tree.insert(
                "", "end",
                values=(
                    f"{SEG_ICON.get(r['time'], '')} {r['time']}",
                    f"{ACT_ICON.get(r['activity'], '')} {r['activity']}",
                    e_str,
                    f"{FIT_ICON.get(fit, '')} {fit}",
                    r.get("date", "—")
                ),
                tags=(tag,)
            )

    def refresh_insights(self):
        total = len(records)
        self.lbl_total.config(text=str(total))

        if not records:
            self.lbl_period.config(text="—")
            self.lbl_avg.config(text="—")
            self.lbl_streak.config(text="—")
            self.state_label.config(
                text="No records yet. Head to the Log Activity tab to get started.")
            draw_chart(self.chart, {})
            return

        avgs   = get_averages()
        counts = {s: 0 for s in TIME_SEGMENTS}
        total_e = 0

        for r in records:
            counts[r["time"]] += 1
            total_e += int(r["energy"])

        most_logged = max(counts, key=counts.get)
        overall     = total_e / total
        best        = max(avgs, key=avgs.get) if avgs else "—"

        self.lbl_period.config(text=f"{SEG_ICON.get(most_logged, '')} {most_logged}")
        self.lbl_avg.config(text=f"{overall:.1f} / 5",
                            fg=energy_color(round(overall)))
        self.lbl_streak.config(text=f"{SEG_ICON.get(best, '')} {best}" if best != "—" else "—")

        self.state_label.config(
            text=(f"  {total} record(s) logged.  "
                  f"Most active: {most_logged}.  "
                  f"Overall energy: {overall:.1f}/5  ({classify_energy(overall)}).  "
                  f"Highest average: {best}.")
        )

        draw_chart(self.chart, avgs)

    def reset_analysis(self):
        self.lbl_peak.config(text="—")
        self.lbl_low.config(text="—")
        self.lbl_good_fit.config(text="0")
        self.lbl_poor_fit.config(text="0")
        self.energy_text.config(text="Click ▶ Run Analysis to generate energy insights.")
        self.reco_text.config(text="Your personalised recommendation will appear here.")

    def run_analysis(self):
        result = analyze_data()

        if result is None:
            messagebox.showwarning("No Data",
                                   "Add some activity records first to run analysis.")
            return

        peak, lowest, avgs, fits, reco = result

        self.lbl_peak.config(text=f"{SEG_ICON.get(peak, '')} {peak}")
        self.lbl_low.config(text=f"{SEG_ICON.get(lowest, '')} {lowest}")
        self.lbl_good_fit.config(text=str(fits["Good Match"]))
        self.lbl_poor_fit.config(text=str(fits["Poor Match"]))

        # Energy overview text
        overview = "ENERGY OVERVIEW\n" + "─" * 15 + "\n\n"
        for seg in TIME_SEGMENTS:
            icon = SEG_ICON.get(seg, "")
            if seg in avgs:
                bar = "█" * int(avgs[seg]) + "░" * (5 - int(avgs[seg]))
                overview += f"{icon}  {seg:10s}  {bar}  {avgs[seg]:.1f}  {classify_energy(avgs[seg])}\n"
            else:
                overview += f"{icon}  {seg:10s}  ░░░░░  —   No data\n"

        overview += "\n\nTASK FIT SUMMARY\n" + "─" * 16 + "\n\n"
        overview += f"✅  Good Match   {fits['Good Match']:>3}\n"
        overview += f"⚡  Fair Match   {fits['Fair Match']:>3}\n"
        overview += f"❌  Poor Match   {fits['Poor Match']:>3}"

        self.energy_text.config(
            text=overview,
            font=("Consolas", 9),
            fg=C["text"]
        )

        self.reco_text.config(
            text=f"RECOMMENDATION\n{'─' * 10}\n\n{reco}",
            font=("Segoe UI", 10),
            fg=C["text"]
        )

        self._set_status(
            f"Analysis complete — Peak: {peak} · Lowest: {lowest} · "
            f"Good Matches: {fits['Good Match']}"
        )

    def clear_records(self):
        if not records:
            self._set_status("Nothing to clear.")
            return
        if messagebox.askyesno("Clear All",
                               f"Permanently delete all {len(records)} records?"):
            records.clear()
            save_records()
            self.refresh_records()
            self.refresh_insights()
            self.reset_analysis()
            self._set_status("All records cleared.")

if __name__ == "__main__":
    load_records()
    app = CircadianApp()
    app.mainloop()
