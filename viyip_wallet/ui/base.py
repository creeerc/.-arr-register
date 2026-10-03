"""Base screen class with common styling."""

import tkinter as tk
from tkinter import ttk

from . import styles as S


class BaseScreen(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=S.BG, **kwargs)
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def header(self, title: str, show_back: bool = True):
        bar = tk.Frame(self, bg=S.BG_CARD, height=56)
        bar.pack(fill="x", padx=0, pady=0)
        bar.pack_propagate(False)

        if show_back:
            back = tk.Button(bar, text="Back", bg=S.BG_CARD, fg=S.ACCENT,
                             activebackground=S.BG_CARD_2, activeforeground=S.ACCENT,
                             font=S.FONT_SMALL, bd=0, cursor="hand2",
                             command=lambda: self.app.show_screen("DashboardScreen"))
            back.pack(side="left", padx=12, pady=10)

        lbl = tk.Label(bar, text=title, bg=S.BG_CARD, fg=S.TEXT,
                       font=S.FONT_HEADING)
        lbl.pack(side="left", padx=8, pady=10)


def action_button(parent, text, command, bg=S.ACCENT, fg=S.TEXT,
                  font=S.FONT_BODY, width=None):
    return tk.Button(parent, text=text, bg=bg, fg=fg, activebackground=S.ACCENT_HOVER,
                     activeforeground=S.TEXT, font=font, bd=0, cursor="hand2",
                     relief="flat", width=width, command=command)


def card(parent, **kwargs):
    f = tk.Frame(parent, bg=S.BG_CARD, highlightbackground=S.BORDER,
                 highlightthickness=1, **kwargs)
    return f


def label(parent, text, font=S.FONT_BODY, fg=S.TEXT, bg=S.BG_CARD, **kwargs):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)


def entry(parent, **kwargs):
    e = tk.Entry(parent, bg=S.BG_CARD_2, fg=S.TEXT, insertbackground=S.TEXT,
                 font=S.FONT_BODY, highlightbackground=S.BORDER,
                 highlightthickness=1, **kwargs)
    return e


def combo(parent, **kwargs):
    cb = ttk.Combobox(parent, background=S.BG_CARD_2, foreground=S.TEXT,
                      font=S.FONT_BODY, state="readonly",
                      style="TCombobox")
    return cb


def status_badge(parent, text="", status="info"):
    colors = {
        "success": (S.SUCCESS, "#0f1f0f"),
        "danger": (S.DANGER, "#2a0f0f"),
        "warn": (S.WARN, "#2a1f0a"),
        "info": (S.ACCENT, S.BG_CARD_2),
    }
    fg, bg = colors.get(status, colors["info"])
    lbl = tk.Label(parent, text=text, bg=bg, fg=fg, font=S.FONT_SMALL,
                   padx=6, pady=2)
    return lbl


def divider(parent):
    sep = tk.Frame(parent, bg=S.BORDER, height=1)
    sep.pack(fill="x", pady=8)
    return sep