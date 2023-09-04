import tkinter as tk
from tkinter import ttk
from utils import *
from ttkbootstrap import Style
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class View():
    def __init__(self, master,  controller=None):
        self.master = master
        self.master.title("PillBox")
        self.controller = controller

        self.load_login_window()
        self.load_widgets()

        self.style = Style()
        self.style.theme_use('flatly')

    def load_widgets(self):
        self.label = ttk.Label(self.master, text="Hello")
        self.label.pack()
        self.label = ttk.Label(self.master, text="World")
        self.label.pack()
        self.load_menu()


    def load_login_window(self):
        self.top_login = tk.Toplevel(self.master)
        WindowUtils.center_window(self.top_login, 400, 500)

        self.login_label = tb.Label(
            self.top_login, text="Login", font=("Arial", 22, "bold")
        )
        self.login_label.pack(pady=10)

        self.entry_username = tb.Entry(
            self.top_login, font=("Arial", 12), style="Primary.TEntry"
        )
        self.entry_username.insert(0, "Username")
        self.entry_username.pack(pady=10, padx=20)
        self.entry_username.bind("<FocusIn>", self.clear_placeholder)
        self.entry_username.bind("<FocusOut>", self.restore_placeholder)

        self.entry_password = tb.Entry(
            self.top_login, show="•", font=("Arial", 12), style="Primary.TEntry"
        )
        self.entry_password.insert(0, "Password")
        self.entry_password.pack(pady=10, padx=20)
        self.entry_password.bind("<FocusIn>", self.clear_placeholder)
        self.entry_password.bind("<FocusOut>", self.restore_placeholder)

        self.login_button = tb.Button(
            self.top_login,
            text="Login",
            command=self.on_login,
            bootstyle=SECONDARY
        )
        self.login_button.pack(pady=20)

        self.top_login.bind("<Return>", lambda event: self.on_login())

    def clear_placeholder(self, event):
        if event.widget.get() in ("Username", "Password"):
            event.widget.delete(0, "end")

    def restore_placeholder(self, event):
        if not event.widget.get():
            event.widget.insert(0, "Username" if event.widget == self.entry_username else "Password")


    def on_login(self):
        self.controller.login()

    def on_login_window_close(self):
        self.top_login.destroy()

    def load_menu(self):
        menu_data = [
            ("Menu", [
                ("Sales", None)
            ]),
            ("Admin Menu", [
                ("Users", [
                    ("Add New User", None),
                    ("Show Users", None)
                ])
            ]),
            ("Help", [
                ("About", None),
                ("Documentation", None),
                ("Log Out", None)
            ])
        ]

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        for menu_label, menu_items in menu_data:
            menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label=menu_label, menu=menu)

            for item_label, command in menu_items:
                if isinstance(command, list):
                    sub_menu = tk.Menu(menu, tearoff=0)
                    menu.add_cascade(label=item_label, menu=sub_menu)

                    for sub_item_label, sub_command in command:
                        sub_menu.add_command(label=sub_item_label, command=sub_command)
                else:
                    menu.add_command(label=item_label, command=command)
