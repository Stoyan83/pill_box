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
        self.search_frame_loaded = False
        self.search_frame = None

        self.selected_workplace = tk.StringVar()
        self.load_login_window()
        self.load_widgets()

    def load_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.load_menu()


    def create_notebook(self, page_title, data_list, page, results_per_page):
        if self.current_notebook_tab is not None:
            self.notebook.forget(self.current_notebook_tab)

        self.frame = ttk.Frame(self.notebook)
        self.notebook.add(self.frame, text=page_title)
        self.current_notebook_tab = self.frame

        close_button = tb.Button(self.frame, text="Close", bootstyle="danger-outline", command=lambda: self.close_notebook(self.frame))
        close_button.pack(side=tk.TOP, anchor=tk.NE)

        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        medicine_frame_container = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=medicine_frame_container, anchor=tk.NW)

        self.canvas.bind("<Configure>", lambda event, canvas=self.canvas: self.canvas.itemconfig(self.canvas.find_withtag("all"), width=event.width))
        self.canvas.bind_all("<MouseWheel>", lambda event, canvas=self.canvas: self.canvas.yview_scroll(-1*(event.delta//120), "units"))

        offset = (page - 1) * results_per_page
        end_index = offset + results_per_page
        displayed_data = data_list[offset:end_index]

        for data in displayed_data:
            medicine_frame = ttk.Frame(medicine_frame_container, borderwidth=1, relief="solid")
            medicine_frame.pack(pady=5, padx=10, fill="x")

            label_widget = ttk.Label(medicine_frame, text=f"ID: {data['ID']}\nTrade Name: {data['Trade Name']}\nQuantity: {data['Quantity']}", cursor="hand2")
            label_widget.pack(padx=5, pady=2, anchor="w", fill="x")

            additional_info_widget = ttk.Label(medicine_frame, text=f"", state=tk.HIDDEN)
            additional_info_widget.pack(padx=5, pady=2, anchor="w", fill="x")

            label_widget.is_visible = False

            label_widget.bind("<Button-1>", lambda event, label=label_widget, data=data: self.toggle_label_visibility(label, data))

        medicine_frame_container.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Pagination
        pagination_frame = ttk.Frame(self.current_notebook_tab)
        pagination_frame.pack(side=tk.BOTTOM, pady=10)

        prev_button = ttk.Button(pagination_frame, text="Previous Page", command=lambda: self.load_previous_page(page, results_per_page, data_list))
        prev_button.grid(row=0, column=0, padx=5)

        next_button = ttk.Button(pagination_frame, text="Next Page", command=lambda: self.load_next_page(page, results_per_page, data_list))
        next_button.grid(row=0, column=1, padx=5)


        self.total_pages = (len(data_list) - 1) // results_per_page + 1

        prev_button.config(state=tk.NORMAL if page > 1 else tk.DISABLED)
        next_button.config(state=tk.NORMAL if page < self.total_pages else tk.DISABLED)

    def load_previous_page(self, current_page, results_per_page, data_list):
        if current_page > 1:
            new_page = current_page - 1
            self.create_notebook("Search Results", data_list, new_page, results_per_page)

    def load_next_page(self, current_page, results_per_page, data_list):
        if current_page < self.total_pages:
            new_page = current_page + 1
            self.create_notebook("Search Results", data_list, new_page, results_per_page)

    def toggle_label_visibility(self, label, data):
        if label.is_visible:
            label.config(state=tk.HIDDEN)
            label.config(text=f"ID: {data['ID']}\nTrade Name: {data['Trade Name']}\nQuantity: {data['Quantity']}")
        else:
            label.config(state=tk.NORMAL)
            additional_info = "\n".join([f"{key}: {value}" for key, value in data.items()])
            label.config(text=additional_info)

        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        label.is_visible = not label.is_visible

    def close_notebook(self, frame_to_close):
        self.notebook.forget(frame_to_close)
        if self.search_frame is not None:
            self.search_frame.destroy()
            self.search_frame_loaded = False
            self.current_notebook_tab = None

    def load_login_window(self):
        self.top_login = tk.Toplevel(self.master)
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
                ("Nomenclature", self.load_search),

                ("Inventory Management", [
                    ("Receive Inventory", self.receive_inventory),
                    ("Placing Order", "placing_order"),
                    ("Inventory Check", "inventory_check")
                ])

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
                ("Log Out", self.log_out)
            ])
        ]

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        for menu_label, menu_items in menu_data:
            menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label=menu_label, menu=menu)

            for item_label, command in menu_items:
                if isinstance(command, list):
                    self.add_submenu(menu, item_label, command)
                else:
                    self.add_menu_item(menu, item_label, command)

    def add_submenu(self, parent_menu, label, submenu_data):
        submenu = tk.Menu(parent_menu, tearoff=0)
        parent_menu.add_cascade(label=label, menu=submenu)

        for sub_item_label, sub_command in submenu_data:
            self.add_menu_item(submenu, sub_item_label, sub_command)

    def add_menu_item(self, menu, label, command):
        if isinstance(command, str):
            menu.add_command(label=label, command=lambda cmd=command: self.execute_command(cmd))
        else:
            menu.add_command(label=label, command=command)

    def execute_command(self, command):
        getattr(self.controller, command)()

    def load_search(self):
        if not self.search_frame_loaded:
            self.search_frame = ttk.Frame(self.master)
            self.search_frame.pack(pady=10, padx=10, fill="x")

            search_label = ttk.Label(self.search_frame, text="Search:")
            search_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            self.search_entry = ttk.Entry(self.search_frame, validate="key")
            self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            self.criteria_listbox = ttk.Combobox(self.search_frame, values=["Name", "ID"])
            self.criteria_listbox.set("Name")
            self.criteria_listbox.grid(row=0, column=2, padx=5, pady=5, sticky="e")

            search_button = ttk.Button(self.search_frame, text="Search", command=self.on_search)
            search_button.grid(row=0, column=3, padx=5, pady=5)

            self.search_results_label = ttk.Label(self.master, text="", font=("Arial", 16))
            self.search_results_label.pack(pady=10)

            self.search_frame_loaded = True

            self.create_notebook("Nomenclature", [], 1, 10)

    def on_search(self):
        search_term = self.search_entry.get().strip()
        if search_term:
            search_criteria = self.criteria_listbox.get()
            self.controller.show_nomenclature(search_term, search_criteria)
            self.search_entry.delete(0, tk.END)

    def log_out(self):
        if self.current_notebook_tab:
            self.close_notebook(self.frame)
        if self.search_frame is not None:
            self.search_frame.destroy()
            self.search_frame_loaded = False
            self.current_notebook_tab = None
        self.master.withdraw()
        self.load_login_window()


    def receive_inventory(self):
        receive_inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(receive_inventory_tab, text="Receive Inventory")

        left_frame = ttk.Frame(receive_inventory_tab)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        input_fields = [
            "name", "quantity", "delivery_price", "vat_price",
            "customer_price", "batch_number", "expiry_date", "supplier"
        ]

        entries = [ttk.Entry(left_frame) for _ in range(len(input_fields))]

        for i, label in enumerate(input_fields):
            label = self.controller.humanize_text(label)
            label_widget = ttk.Label(left_frame, text=label, width=15)
            entry_widget = entries[i]

            label_widget.grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
            entry_widget.grid(row=i + 1, column=1, padx=5, pady=5, sticky="ew")

        invoice_labels = ["invoice_number", "date", "sum", "vat", "total_sum"]
        invoice_entries = [tb.Entry(left_frame) for _ in range(len(invoice_labels))]


        for i, label in enumerate(invoice_labels):
            label = self.controller.humanize_text(label)
            label_widget = tb.Label(left_frame, text=label, width=15, anchor="w")
            entry_widget = invoice_entries[i]

            label_widget.grid(row=i + 1, column=4, padx=5, pady=5, sticky="w")
            entry_widget.grid(row=i + 1, column=5, padx=5, pady=5, sticky="ew")


        invoice_entries[3].config(state="readonly")
        invoice_entries[4].config(state="readonly")

        submit_button = ttk.Button(left_frame, text="Add Medicine", command=lambda: self.add_medicine(entries, canvas, input_fields))
        submit_button.grid(row=len(input_fields) + 1, column=1, columnspan=2, pady=10)

        confirm_button = ttk.Button(left_frame, text="Confirm",  command=lambda: self.confirm_inventory(invoice_labels=invoice_labels, invoice_entries=invoice_entries))
        confirm_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        right_frame = ttk.Frame(receive_inventory_tab)
        right_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        labels_frame = ttk.Frame(right_frame)
        labels_frame.pack(fill=tk.X)

        for i, label in enumerate(input_fields):
            label = self.controller.humanize_text(label)
            label_widget = ttk.Label(labels_frame, text=label, width=15)
            label_widget.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        canvas = tk.Canvas(right_frame, bg="black")
        canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas = canvas
        self.get_invoice_fields = []

    def add_medicine(self, entries, canvas, labels):
        self.data_dict = {}

        for entry, label in zip(entries, labels):
            entry_value = entry.get()
            self.data_dict[label] = entry_value

        self.get_invoice_fields.append(self.data_dict)

        for entry in entries:
            entry.delete(0, "end")

        row_height, offset = 20, 0

        for i, row_data in enumerate(self.get_invoice_fields):
            y = (i + 1) * row_height + offset
            x = 20

            row_frame = tk.Frame(canvas)
            canvas.create_window(x, y, anchor="w", window=row_frame)

            for col, label_name in enumerate(row_data):
                label_value = row_data[label_name]
                label_text = f"{label_value}"
                label = tk.Label(row_frame, text=label_text, width=18, anchor="w", cursor="hand2")
                label.grid(row=0, column=col, pady=10, sticky="w")

                label.bind("<Button-1>", lambda event, i=i: self.edit_row(i))

            offset += row_height

        total_height = (len(self.get_invoice_fields) + 1) * row_height + offset

        canvas.config(scrollregion=(0, 0, 0, total_height))


    def edit_row(self, row_index):
        print("click")
        pass


    def confirm_inventory(self, invoice_labels=None, invoice_entries=None, calculated=None):
        invoice_data = {}

        if not calculated:
            self.invoice_entries = invoice_entries
            self.invoice_labels = invoice_labels
            for entry, label in zip(invoice_entries, invoice_labels):
                entry_value = entry.get()
                invoice_data[label] = entry_value

            self.controller.calculate_total(invoice_data)

        else:
            new_data = calculated
            for entry, label in zip(self.invoice_entries, self.invoice_labels):
                entry.configure(state="default")
                entry.delete(0, "end")
                entry.insert(0, new_data.get(label))
                entry.configure(state="disabled")
                entry_value = entry.get()
                invoice_data[label] = entry_value

        print(invoice_data)
