import tkinter as tk
from tkinter import ttk
from utils import *
from ttkbootstrap import Style
import ttkbootstrap as tb


class View():
    def __init__(self, master,  controller=None):
        self.master = master
        self.controller = controller

        self.master.title("PillBox")
        self.style = Style()
        self.style.theme_use('flatly')

        self.current_notebook_tab = None

        self.selected_workplace = tk.StringVar()
        self.load_login_window()
        self.load_widgets()

    def load_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.load_menu()


    def create_notebook(self, page_title, data_list):
        # Close the current tab if it exists
        if self.current_notebook_tab is not None:
            self.notebook.forget(self.current_notebook_tab)

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=page_title)

        # Set the current tab variable to the newly added tab
        self.current_notebook_tab = frame

        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        medicine_frame_container = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=medicine_frame_container, anchor=tk.NW)

        canvas.bind("<Configure>", lambda event, canvas=canvas: self.on_canvas_configure(event, canvas))
        canvas.bind_all("<MouseWheel>", lambda event, canvas=canvas: self.on_mousewheel(event, canvas))

        for data in data_list:
            medicine_frame = ttk.Frame(medicine_frame_container, borderwidth=1, relief="solid")
            medicine_frame.pack(pady=5, padx=10, fill="x")

            for label, value in data.items():
                label_widget = ttk.Label(medicine_frame, text=f"{label}: {value}")
                label_widget.pack(padx=5, pady=2, anchor="w", fill="x")

        medicine_frame_container.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


    def on_canvas_configure(self, event, canvas):
        canvas.itemconfig(canvas.find_withtag("all"), width=event.width)

    def on_mousewheel(self, event, canvas):
        canvas.yview_scroll(-1*(event.delta//120), "units")



    def load_login_window(self):
        self.top_login = tk.Toplevel(self.master)
        self.top_login.title("Login")
        WindowUtils.center_window(self.top_login, 400, 500)

        login_label = ttk.Label(
            self.top_login, text="Login", font=("Arial", 22, "bold")
        )
        login_label.pack(pady=10)

        login_options = ttk.Combobox(self.top_login, values=["workplace 1", "workplace 2", "workplace 3"], textvariable=self.selected_workplace)
        login_options.set("Select Workplace")
        login_options.pack(pady=10, padx=20)

        self.entry_username = self.create_entry(self.top_login, "Username")
        self.entry_password = self.create_entry(self.top_login, "Password", show="•")

        login_button = ttk.Button(
            self.top_login,
            text="Login",
            command=self.on_login,
            style="primary"
        )
        login_button.pack(pady=20)

        self.top_login.bind("<Return>", lambda event: self.on_login())
        self.top_login.protocol("WM_DELETE_WINDOW", self.on_login_window_close)

    def create_entry(self, parent, placeholder, **kwargs):
        entry = ttk.Entry(parent, font=("Arial", 12), style="secondary", **kwargs)
        entry.insert(0, placeholder)
        entry.pack(pady=10, padx=20)
        entry.bind("<FocusIn>", self.clear_placeholder)
        entry.bind("<FocusOut>", self.restore_placeholder)
        return entry

    def clear_placeholder(self, event):
        if event.widget.get() in ("Username", "Password"):
            event.widget.delete(0, "end")

    def restore_placeholder(self, event):
        if not event.widget.get():
            event.widget.insert(0, "Username" if event.widget == self.entry_username else "Password")


    def on_login(self):
        selected_option = self.selected_workplace.get()
        self.controller.login(selected_option)

    def on_login_window_close(self):
        self.top_login.destroy()
        self.master.destroy()

    def load_menu(self):
        menu_data = [
            ("Menu", [
                ("Nomenclature", self.load_search)
            ]),
            ("Admin Menu", [
                ("Users", [
                    ("Add New User", "add_new_user"),
                    ("Show Users", "show_users")
                ])
            ]),
            ("Help", [
                ("About", "show_about"),
                ("Documentation", "show_documentation"),
                ("Log Out", "log_out")
            ])
        ]

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        for menu_label, menu_items in menu_data:
            menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label=menu_label, menu=menu)

            for item_label, command in menu_items:
                if isinstance(command, str):
                    menu.add_command(label=item_label, command=lambda cmd=command: self.execute_command(cmd))
                else:
                    menu.add_command(label=item_label, command=command)
    def execute_command(self, command):
        getattr(self.controller, command)()


    def load_search(self):
        search_frame = ttk.Frame(self.master)
        search_frame.pack(pady=10, padx=10, fill="x")

        search_label = ttk.Label(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.criteria_listbox = ttk.Combobox(search_frame, values=["Name", "ID"])
        self.criteria_listbox.set("Name")
        self.criteria_listbox.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        search_button = ttk.Button(search_frame, text="Search", command=self.on_search)
        search_button.grid(row=0, column=3, padx=5, pady=5)

        self.search_results_label = ttk.Label(self.master, text="", font=("Arial", 16))
        self.search_results_label.pack(pady=10)


    def on_search(self):
        search_term = self.search_entry.get()
        self.controller.show_nomenclature(search_term)
