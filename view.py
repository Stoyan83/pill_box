import tkinter as tk
from tkinter import ttk
from utils import *
from ttkbootstrap import Style


class View():
    def __init__(self, master,  controller=None):
        self.master = master
        self.master.title("PillBox")
        self.controller = controller

        self.load_login_window()
        self.load_widgets()

        self.style = Style()
        self.style.theme_use('pulse')

    def load_widgets(self):
        self.label = ttk.Label(self.master, text="Hello")
        self.label.pack()
        self.label = ttk.Label(self.master, text="World")
        self.label.pack()
        self.load_menu()


    def load_login_window(self):
        self.top_login = tk.Toplevel()
        WindowUtils.center_window(self.top_login, 600, 400)

        self.top_login.configure(bg="#2c3e50")

        self.login_label = tk.Label(self.top_login, text="Login", bg="#2c3e50", fg="white", font=("Arial", 24, "bold"))
        self.login_label.grid(row=0, column=0, padx=10, pady=20, columnspan=2)

        self.entry_username = EntryWithPlaceholder(self.top_login, placeholder="Username", color="#34495e")
        self.entry_username.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        self.entry_password = EntryWithPlaceholder(self.top_login, placeholder="Password", show='\u2022', color="#34495e")
        self.entry_password.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

        self.login_button = tk.Button(self.top_login, text="Login", command=self.on_login, font=("Arial", 14), bg="#3498db", fg="white")
        self.login_button.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

        self.top_login.bind("<Return>", lambda event: self.on_login())

        self.top_login.protocol("WM_DELETE_WINDOW", self.on_login_window_close)

        self.top_login.grid_rowconfigure(0, weight=1)
        self.top_login.grid_rowconfigure(4, weight=1)
        self.top_login.grid_columnconfigure(0, weight=1)
        self.top_login.grid_columnconfigure(1, weight=1)


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
