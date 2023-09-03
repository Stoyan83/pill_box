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


class EntryWithPlaceholder(tk.Entry):
    """
        Note:
             Shows placeholders for entries.
    """
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', show=None):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.show = show

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def focus_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color
            if self.show is not None:
                self.configure(show=self.show)

    def focus_out(self, *args):
        if not self.get():
            self.put_placeholder()
            if self.show is not None:
                self.configure(show='')


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
