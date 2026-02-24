import tkinter as tk
from tkinter import ttk
from backend.dfa_to_cfg import convert_dfa_to_cfg

# COLOR PALETTE
BG        = "#1c1c1c"   # main window background
PANEL     = "#242424"   # card / panel background
SURFACE   = "#2e2e2e"   # input fields, table cells, rules box
BORDER    = "#3a3a3a"   # subtle borders and dividers
BLUE      = "#3c8cee"   # main accent — buttons, headings, output text
BLUE_DIM  = "#235ea7"   # darker blue — separator line under header
TEXT      = "#f0ead6"   # warm off-white — general text
DIM       = "#888070"   # muted — hints, secondary labels, rules box text
ERROR     = "#e05050"   # red — validation error messages

MONO      = "Helvetica"
FONT_XL   = (MONO, 18, "bold")
FONT_LG   = (MONO, 12, "bold")
FONT_MD   = (MONO, 11)
FONT_SM   = (MONO, 10)
FONT_XS   = (MONO, 9)


# LETTER PICKER POPUP
# shows up when the user picks Latin and clicks Choose Letters
class LetterPicker(tk.Toplevel):
    def __init__(self, parent, current_selection):
        super().__init__(parent)
        self.title("Pick Letters")
        self.configure(bg=PANEL)
        self.resizable(False, False)
        self.result = None
        self.vars   = {}

        tk.Label(self, text="Choose your alphabet letters",
                 font=FONT_LG, bg=PANEL, fg=BLUE).pack(padx=24, pady=(18, 10))

        # 26 letters in a 9-column grid
        grid = tk.Frame(self, bg=PANEL)
        grid.pack(padx=24, pady=(0, 10))
        for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
            v = tk.BooleanVar(value=(ch in current_selection))
            self.vars[ch] = v
            tk.Checkbutton(
                grid, text=ch, variable=v, font=FONT_SM,
                bg=PANEL, fg=TEXT, selectcolor=SURFACE,
                activebackground=PANEL, activeforeground=BLUE
            ).grid(row=i // 9, column=i % 9, padx=5, pady=3)

        tk.Button(
            self, text="Confirm", font=FONT_LG,
            bg=BLUE, fg=BG, relief="flat",
            padx=16, pady=6, cursor="hand2",
            command=self._confirm
        ).pack(pady=(6, 18))

        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")
        parent.wait_window(self)

    def _confirm(self):
        self.result = [ch for ch, v in self.vars.items() if v.get()]
        self.destroy()


# MAIN APPLICATION
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DFA → CFG")
        self.geometry("1000x720")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.num_states      = tk.IntVar(value=2)
        self.alpha_choice    = tk.StringVar(value="binary")
        self.latin_letters   = ["a", "b"]
        self.start_state     = tk.StringVar()
        self.accept_vars     = {}   # { "q0": BooleanVar, ... }
        self.transition_vars = {}   # { ("q0","a"): StringVar, ... }

        self._build_ui()

    # TOP LEVEL LAYOUT
    # header on top, then two side-by-side panels below
    def _build_ui(self):
        self._build_header()
        tk.Frame(self, bg=BLUE_DIM, height=1).pack(fill="x", padx=0, pady=0)
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)
        self._build_left(body)
        self._build_right(body)

    # HEADER SECTION — title, description and the 3 conversion rules
    def _build_header(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 12))

        title_row = tk.Frame(hdr, bg=BG)
        title_row.pack(anchor="w")
        tk.Label(title_row, text=">", font=FONT_XL, bg=BG, fg=BLUE).pack(side="left")
        tk.Label(title_row, text="  DFA to CFG Converter",
                 font=FONT_XL, bg=BG, fg=TEXT).pack(side="left")

        tk.Label(hdr,
                 text="Generates a right-linear context-free grammar from a deterministic finite automaton.",
                 font=FONT_XS, bg=BG, fg=DIM).pack(anchor="w", pady=(6, 8))

        # 3 conversion rules laid out clearly
        rules_frame = tk.Frame(hdr, bg=SURFACE, padx=14, pady=10)
        rules_frame.pack(anchor="w")
        for rule in [
            "Rule 1:  δ(qi, a) = qj   →   add production  qi → a qj",
            "Rule 2:  If qi  is an accept state   →   add production  qi → ε",
            "Rule 3:  Start variable  =  start state of the DFA",
        ]:
            tk.Label(rules_frame, text=rule, font=FONT_XS,
                     bg=SURFACE, fg=DIM).pack(anchor="w", pady=1)

    # LEFT PANEL — all DFA input goes here
    # wrapped in a scrollable canvas so the convert button is always reachable
    def _build_left(self, parent):
        outer = tk.Frame(parent, bg=PANEL,
                         highlightthickness=1, highlightbackground=BORDER)
        outer.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # vertical scrollbar
        self.lcanvas = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.lcanvas.yview)
        self.lcanvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.lcanvas.pack(side="left", fill="both", expand=True)

        self.lframe = tk.Frame(self.lcanvas, bg=PANEL)
        self.lframe.bind("<Configure>",
            lambda e: self.lcanvas.configure(scrollregion=self.lcanvas.bbox("all")))
        self.lcanvas.create_window((0, 0), window=self.lframe, anchor="nw")
        self.lcanvas.bind_all("<MouseWheel>",
            lambda e: self.lcanvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._left_static()

    def _left_static(self):
        f = self.lframe
        P = 16

        # number of states input section
        self._section(f, "> States")
        tk.Spinbox(
            f, from_=1, to=10, textvariable=self.num_states,
            width=5, font=FONT_MD, fg=TEXT, bg=SURFACE,
            buttonbackground=BORDER, relief="flat",
            insertbackground=TEXT, disabledforeground=TEXT
        ).pack(anchor="w", padx=P, pady=(0, 12))

        # alphabet input section
        self._section(f, "> Alphabet")

        tk.Radiobutton(
            f, text="binary   { 0, 1 }", variable=self.alpha_choice,
            value="binary", font=FONT_MD, bg=PANEL, fg=TEXT,
            selectcolor=SURFACE, activebackground=PANEL,
            activeforeground=BLUE,
            command=self._on_alpha_change
        ).pack(anchor="w", padx=P)

        tk.Radiobutton(
            f, text="latin    { a, b, c ... }", variable=self.alpha_choice,
            value="latin", font=FONT_MD, bg=PANEL, fg=TEXT,
            selectcolor=SURFACE, activebackground=PANEL,
            activeforeground=BLUE,
            command=self._on_alpha_change
        ).pack(anchor="w", padx=P, pady=(6, 8))

        # choose letters button — only shown when latin is selected
        self.letter_btn = tk.Button(
            f, text="Choose Letters", font=FONT_SM,
            bg=BLUE, fg=BG, relief="flat",
            cursor="hand2", padx=8, pady=3,
            command=self._pick_letters
        )
        # hidden by default since binary is selected on launch

        # generate button — builds the rest of the form
        tk.Button(
            f, text="Generate Form", font=FONT_LG,
            bg=BLUE, fg=BG, relief="flat", cursor="hand2",
            padx=14, pady=7,
            command=self._generate
        ).pack(anchor="w", padx=P, pady=(10, 10))

        # dynamic section — rebuilt every time the user clicks generate
        self.dynamic = tk.Frame(f, bg=PANEL)
        self.dynamic.pack(fill="x")

        # error messages show here
        self.err = tk.StringVar()
        tk.Label(f, textvariable=self.err, font=FONT_XS,
                 bg=PANEL, fg=ERROR, wraplength=380,
                 justify="left").pack(anchor="w", padx=P, pady=(4, 12))

    # RIGHT PANEL — CFG output display
    def _build_right(self, parent):
        outer = tk.Frame(parent, bg=PANEL,
                         highlightthickness=1, highlightbackground=BORDER)
        outer.pack(side="right", fill="both", expand=True, padx=(8, 0))

        inner = tk.Frame(outer, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        self.output = tk.Text(
            inner, font=("Courier New", 11), bg=SURFACE, fg=BLUE,
            relief="flat", state="disabled", wrap="word",
            insertbackground=TEXT,
            highlightthickness=1, highlightbackground=BORDER,
            padx=12, pady=10
        )
        self.output.pack(fill="both", expand=True)

        # tags used in the output — titles in bold, everything else in blue
        self.output.tag_config("title", foreground=BLUE,
                               font=("Courier New", 11, "bold"))
        self.output.tag_config("dim",   foreground=DIM)

    # GENERATE FORM
    # clears and rebuilds the dynamic section based on current state/alphabet selection
    def _generate(self):
        for w in self.dynamic.winfo_children():
            w.destroy()
        self.accept_vars.clear()
        self.transition_vars.clear()
        self.err.set("")

        states   = [f"q{i}" for i in range(self.num_states.get())]
        alphabet = self._resolve_alphabet()
        if alphabet is None:
            return

        f = self.dynamic
        P = 16

        # start state dropdown
        self._section(f, "> Start state")
        self.start_state.set(states[0])
        om = tk.OptionMenu(f, self.start_state, *states)
        om.config(font=FONT_MD, bg=SURFACE, fg=BG, relief="flat",
                  highlightthickness=0,
                  activebackground=BLUE, activeforeground=BG)
        om["menu"].config(font=FONT_MD, bg=SURFACE, fg=BG,
                          activebackground=BLUE, activeforeground=BG)
        om.pack(anchor="w", padx=P, pady=(0, 12))

        # accept states checkboxes
        self._section(f, "> Accept states")
        row = tk.Frame(f, bg=PANEL)
        row.pack(anchor="w", padx=P, pady=(0, 12))
        for state in states:
            v = tk.BooleanVar(value=False)
            self.accept_vars[state] = v
            tk.Checkbutton(
                row, text=state, variable=v, font=FONT_MD,
                bg=PANEL, fg=TEXT, selectcolor=SURFACE,
                activebackground=PANEL, activeforeground=BLUE
            ).pack(side="left", padx=6)

        # transition table
        # horizontally scrollable so it handles many states/symbols without clipping
        self._section(f, "> Transition table")

        # outer frame holds the canvas + scrollbars
        tbl_outer = tk.Frame(f, bg=PANEL)
        tbl_outer.pack(anchor="w", padx=P, pady=(0, 12), fill="x")

        tbl_canvas = tk.Canvas(tbl_outer, bg=PANEL, highlightthickness=0,
                               height=40 + 36 * len(states))
        h_scroll = ttk.Scrollbar(tbl_outer, orient="horizontal",
                                  command=tbl_canvas.xview)
        tbl_canvas.configure(xscrollcommand=h_scroll.set)

        h_scroll.pack(side="bottom", fill="x")
        tbl_canvas.pack(side="top", fill="x")

        # actual table frame inside the canvas
        tbl = tk.Frame(tbl_canvas, bg=PANEL)
        tbl_canvas.create_window((0, 0), window=tbl, anchor="nw")
        tbl.bind("<Configure>",
            lambda e: tbl_canvas.configure(scrollregion=tbl_canvas.bbox("all")))

        # header row — symbol names
        tk.Label(tbl, text="δ", font=FONT_MD, bg=PANEL,
                 fg=DIM, width=6).grid(row=0, column=0, padx=6, pady=4)
        for j, sym in enumerate(alphabet):
            tk.Label(tbl, text=sym, font=(MONO, 11, "bold"), bg=PANEL,
                     fg=BLUE, width=8).grid(row=0, column=j+1, padx=6)

        # one row per state, alternating background for readability
        for i, state in enumerate(states):
            bg_row = SURFACE if i % 2 == 0 else PANEL
            tk.Label(tbl, text=state, font=FONT_MD, bg=bg_row,
                     fg=TEXT, width=6).grid(row=i+1, column=0, padx=6, pady=3)
            for j, sym in enumerate(alphabet):
                var = tk.StringVar(value=states[0])
                self.transition_vars[(state, sym)] = var
                om = tk.OptionMenu(tbl, var, *states)
                om.config(font=FONT_SM, bg=SURFACE, fg=BG,
                          relief="flat", width=5, highlightthickness=0,
                          activebackground=BLUE, activeforeground=BG)
                om["menu"].config(font=FONT_SM, bg=SURFACE, fg=BG,
                                  activebackground=BLUE, activeforeground=BG)
                om.grid(row=i+1, column=j+1, padx=4, pady=2)

        # convert button
        tk.Button(
            f, text="Convert to CFG", font=FONT_LG,
            bg=BLUE, fg=BG, relief="flat", cursor="hand2",
            padx=14, pady=7,
            command=lambda: self._convert(states, alphabet)
        ).pack(anchor="w", padx=P, pady=(2, 20))

    # CONVERT — validate inputs, build the dfa dict, call the backend
    def _convert(self, states, alphabet):
        self.err.set("")

        # need at least one accept state
        accept_states = [s for s, v in self.accept_vars.items() if v.get()]
        if not accept_states:
            self.err.set("error: select at least one accept state.")
            return

        # build transitions dict from the table dropdowns
        transitions = {
            (st, sym): var.get()
            for (st, sym), var in self.transition_vars.items()
        }

        # this is the exact dict that goes to the backend
        dfa = {
            "states":        states,
            "alphabet":      alphabet,
            "transitions":   transitions,
            "start_state":   self.start_state.get(),
            "accept_states": accept_states,
        }

        try:
            cfg = convert_dfa_to_cfg(dfa)
            self._display_cfg(cfg)
        except Exception as e:
            self.err.set(f"backend error: {e}")

    # DISPLAY CFG — formats and writes the cfg to the output box
    def _display_cfg(self, cfg):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")

        def w(text, tag=None):
            self.output.insert("end", text, tag or "")

        # header info
        w("// context-free grammar\n\n", "dim")
        w(f"  start variable  :  {cfg['start_variable']}\n")
        w(f"  terminals       :  {', '.join(cfg['terminals'])}\n")
        w(f"  variables       :  {', '.join(cfg['variables'])}\n\n")

        # production rules
        w("// production rules\n", "dim")
        w("  " + "─" * 32 + "\n", "dim")
        for var, rules in cfg["productions"].items():
            w(f"  {var}  →  {' | '.join(rules)}\n")

        self.output.config(state="disabled")

    # HELPERS

    # show or hide the choose letters button depending on alphabet selection
    def _on_alpha_change(self):
        if self.alpha_choice.get() == "latin":
            self.letter_btn.pack(anchor="w", padx=32, pady=(0, 10))
        else:
            self.letter_btn.pack_forget()

    def _pick_letters(self):
        popup = LetterPicker(self, self.latin_letters)
        if popup.result is not None:
            if not popup.result:
                self.err.set("error: select at least one letter.")
            else:
                self.latin_letters = popup.result

    def _resolve_alphabet(self):
        if self.alpha_choice.get() == "binary":
            return ["0", "1"]
        if not self.latin_letters:
            self.err.set("error: select at least one letter.")
            return None
        return self.latin_letters

    # reusable bold blue section heading
    def _section(self, parent, text):
        tk.Label(parent, text=text, font=(MONO, 10, "bold"),
                 bg=parent["bg"], fg=BLUE).pack(anchor="w", padx=16, pady=(14, 4))


# ENTRY POINT
def run_app():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    run_app()