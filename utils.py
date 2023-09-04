import tkinter as tk
from tkinter import ttk


class WindowUtils:
    """
        Note:
             Centers the window in the middle of the screen.
    """
    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.enter_timer = None
        self.leave_timer = None

        self.widget.bind("<Enter>", self.start_enter_timer)
        self.widget.bind("<Leave>", self.start_leave_timer)

    def start_enter_timer(self, event):
        if self.leave_timer:
            self.widget.after_cancel(self.leave_timer)
        self.enter_timer = self.widget.after(500, self.show_tooltip)

    def start_leave_timer(self, event):
        if self.enter_timer:
            self.widget.after_cancel(self.enter_timer)
        self.leave_timer = self.widget.after(500, self.hide_tooltip)

    def show_tooltip(self):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
