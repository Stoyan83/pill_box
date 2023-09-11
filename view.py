import tkinter as tk
from tkinter import ttk, PhotoImage, simpledialog
from utils import *
from ttkbootstrap import Style
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox


class View():
    def __init__(self, master,  controller=None):
        self.master = master
        self.controller = controller

        self.master.title("PillBox")
        self.style = Style()
        self.style.theme_use('superhero')

        self.current_notebook_tab = None
        self.search_frame_loaded = False
        self.search_frame = None
        self.from_inventory = False
        self.receive_inventory_tab = None

        self.sales_data = []

        self.delivery_price_var = tk.StringVar()
        self.selected_workplace = tk.StringVar()

        self.invoice_id_var = tk.StringVar()

        self.load_login_window()
        self.load_widgets()

    def load_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.pencil_icon = PhotoImage(file="images/edit.png").subsample(11, 11)
        self.trash_icon = PhotoImage(file="images/delete.png").subsample(10, 10)

        self.load_menu()

    def create_notebook(self, page_title, data_list, page, results_per_page):
        if self.current_notebook_tab is not None:
            self.notebook.forget(self.current_notebook_tab)

        self.frame = ttk.Frame(self.notebook)
        self.notebook.add(self.frame, text=page_title)

        self.notebook.select(self.frame)

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

            if self.from_inventory:
                add_button = ttk.Button(medicine_frame, text="Add", command=lambda medecine_id=data['ID'], name=data['Trade Name']: self.controller.add_medicine_to_invoice(medecine_id, name))
                add_button.pack(side=tk.RIGHT, padx=5, pady=5)

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
        self.from_inventory = False
        if self.search_frame is not None:
            self.search_frame.destroy()
            self.search_frame_loaded = False
            self.current_notebook_tab = None
        if self.receive_inventory_tab is not None and frame_to_close == self.receive_inventory_tab:
            self.delivery_price_var = tk.StringVar()
            self.invoice_id_var = tk.StringVar()
            self.get_invoice_fields = []
            self.receive_inventory_tab = None
            self.invoice_row_labels = None


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
                ("Sales", self.sales),
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
                ("Toggle Theme", [
                    ("Dark Theme", self.set_superhero_theme),
                    ("Light Theme", self.set_flatly_theme)
                ]),
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


    def set_superhero_theme(self):
        if isinstance(self.master, tk.Tk):  # Check if self.master is the main application window
            try:
                self.style.theme_use('superhero')
            except tk.TclError as e:
                if "bad window path name" in str(e) and ".!toplevel.!combobox" in str(e):
                    # Ignore the error for destroyed combobox login widget
                    pass

    def set_flatly_theme(self):
        if isinstance(self.master, tk.Tk):
            try:
                self.style.theme_use('flatly')
            except tk.TclError as e:
                if "bad window path name" in str(e) and ".!toplevel.!combobox" in str(e):
                    # Ignore the error for destroyed combobox login widget
                    pass


    def load_search(self):
        if not self.search_frame_loaded:
            if self.current_notebook_tab is not None:
                self.notebook.forget(self.current_notebook_tab)

            self.frame = ttk.Frame(self.notebook)
            self.notebook.add(self.frame, text="Search")
            self.notebook.select(self.frame)

            self.search_frame = ttk.Frame(self.frame)
            self.search_frame.pack(side=tk.TOP, fill=tk.X)

            search_label = ttk.Label(self.search_frame, text="Search:")
            search_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            self.search_entry = ttk.Entry(self.search_frame, validate="key")
            self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            self.criteria_listbox = ttk.Combobox(self.search_frame, values=["Name", "ID"], state="readonly")
            self.criteria_listbox.set("Name")
            self.criteria_listbox.grid(row=0, column=2, padx=5, pady=5, sticky="e")

            search_button = ttk.Button(self.search_frame, text="Search", command=self.on_search)
            search_button.grid(row=0, column=3, padx=5, pady=5)

            self.search_results_label = ttk.Label(self.master, text="", font=("Arial", 16))
            self.search_results_label.pack(pady=10)

            self.search_frame_loaded = True

        self.current_notebook_tab = self.frame

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
        if self.receive_inventory_tab:
            return

        self.receive_inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.receive_inventory_tab, text="Receive Inventory")

        self.left_frame = ttk.Frame(self.receive_inventory_tab)
        self.left_frame.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        validate_numeric = self.left_frame.register(self.controller.validate_numeric_input)

        # Define input fields for inventory
        input_fields = ["actions", "id", "name", "quantity", "delivery_price", "customer_price", "batch_number", "expiry_date"]

        # Create Entry widgets for input fields
        entries = []
        for label in input_fields:
            entry = ttk.Entry(self.left_frame)
            entries.append(entry)

            if label == "quantity" or label == "delivery_price":
                entry.config(validate="key", validatecommand=(validate_numeric, "%P"))

        row_num = 1

        labels_to_skip = ["customer_price", "actions", "id"]

        for i, label in enumerate(input_fields):
            # SKip some auto filled labels
            if label in labels_to_skip:
                continue

            label = self.controller.humanize_text(label)
            label_widget = ttk.Label(self.left_frame, text=label, width=15)
            entry_widget = entries[i]

            self.combobox_methods = {
                "Search by Name": self.search_by_name
            }

            # Create a Combobox for choosing a medicine
            if label == "Name":
                entry_widget.config(state="readonly")
                self.name_widget = entry_widget
                self.combobox = ttk.Combobox(self.left_frame, values=list(self.combobox_methods.keys()), state="readonly")
                self.combobox.set("Choose Medicine")
                self.combobox.grid(row=row_num, column=2, padx=5, pady=5, sticky="ew")

            label_widget.grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
            entry_widget.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
            row_num += 1

        self.combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Define labels and Entry widgets for invoice details
        invoice_labels = ["invoice_id", "invoice_number", "supplier", "date", "sum", "vat", "total_sum"]

        self.invoice_entries = []
        for i in range(len(invoice_labels)):
            if invoice_labels[i] == "supplier":
                choices = self.controller.get_suppliers()
                self.entry = tb.Combobox(self.left_frame, values=choices, state="readonly")
            else:
                self.entry = tb.Entry(self.left_frame)
            self.invoice_entries.append(self.entry)

        close_button = tb.Button(self.receive_inventory_tab, text="Close", bootstyle="danger-outline", command=lambda: self.close_notebook(self.receive_inventory_tab))
        close_button.grid(row=0, column=5, padx=5, pady=5, sticky="ne")

        for i, label in enumerate(invoice_labels):
            label = self.controller.humanize_text(label)
            label_widget = tb.Label(self.left_frame, text=label, width=15, anchor="w")
            entry_widget = self.invoice_entries[i]

            if label == "Invoice Id":
                entry_widget.config(textvariable=self.invoice_id_var)

            if label == "Sum":
                entry_widget.config(textvariable=self.delivery_price_var)

            if label in ["Invoice Id", "Invoice Number"]:
                label_widget.grid(row=i + 1, column=4, padx=5, pady=5, sticky="w")
                entry_widget.grid(row=i + 1, column=5, padx=5, pady=5, sticky="ew")
            else:
                label_widget.grid(row=i - 1, column=6, padx=5, pady=5, sticky="w")
                entry_widget.grid(row=i - 1, column=7, padx=5, pady=5, sticky="ew")

        self.invoice_entries[0].config(state="readonly", bootstyle="info")
        self.invoice_entries[4].config(state="readonly")
        self.invoice_entries[5].config(state="readonly")
        self.invoice_entries[6].config(state="readonly")

        self.submit_button = ttk.Button(self.left_frame, text="Add Medicine", command=lambda: self.add_rows_to_inventory(entries, canvas, input_fields))
        self.submit_button.grid(row=len(input_fields) + 1, column=1, columnspan=2, pady=10)

        self.confirm_button = ttk.Button(self.left_frame, text="Confirm",  command=lambda: self.confirm_inventory(invoice_labels=invoice_labels, invoice_entries=self.invoice_entries))
        self.confirm_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        clear_button = ttk.Button(self.left_frame, text="Clear", command=lambda: self.clear_fields(self.receive_inventory_tab))
        clear_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Create a frame for displaying inventory data
        right_frame = ttk.Frame(self.receive_inventory_tab)
        right_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        labels_frame = ttk.Frame(right_frame)
        labels_frame.pack(fill=tk.X)

        widths = [17, 12, 12, 12, 15, 15, 15, 15]

        # Create labels for the inventory fields
        for i, label in enumerate(input_fields):
            label = self.controller.humanize_text(label)
            label_widget = ttk.Label(labels_frame, text=label, width=widths[i])
            label_widget.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        canvas = tk.Canvas(right_frame, bg="black")
        canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas = canvas
        self.get_invoice_fields = []

        self.notebook.select(self.receive_inventory_tab)

    def add_rows_to_inventory(self, entries, canvas, labels):
            labels_to_validate = ["name", "quantity", "delivery_price", "expiry_date", "batch_number"]

            if self.validate_entries(entries, labels, labels_to_validate):
                return

            self.data_dict = {}

            for entry, label in zip(entries, labels):
                entry_value = entry.get()
                if label == "customer_price":
                    delivery_price = self.data_dict.get("delivery_price", 0)
                    quantity = self.data_dict.get("quantity", 0)
                    entry_value = self.controller.calculate_customer_price(delivery_price)
                    self.controller.add_total(delivery_price, quantity)

                if label == "expiry_date":
                    if not self.controller.is_valid_date(entry_value):
                        expected_format = "YYYY-MM-DD"
                        self.show_date_format_error(entry_value, expected_format)
                        return

                self.data_dict[label] = entry_value

            self.get_invoice_fields.append(self.data_dict)

            for entry in entries:
                entry.delete(0, "end")

            row_height, offset = 30, 0
            column_widths = [11, 15, 15, 14, 18, 17, 18]

            self.invoice_row_labels = []

            # Create a canvas for displaying rows with a vertical scrollbar
            canvas_frame = tk.Frame(canvas)
            canvas_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

            # Set the canvas to span multiple columns
            canvas = tk.Canvas(canvas_frame, bg="white", width=1200)
            canvas.grid(row=0, column=0, columnspan=3, sticky="news")

            scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            scrollbar.grid(row=0, column=3, sticky="ns")

            canvas.configure(yscrollcommand=scrollbar.set)

            # Create a frame inside the canvas to hold rows
            rows_frame = tk.Frame(canvas, bg="white")
            canvas.create_window((0, 0), window=rows_frame, anchor="nw")


            for i, row_data in enumerate(self.get_invoice_fields):
                y = i * row_height + offset
                x = 0

                row_frame = tk.Frame(rows_frame, relief="ridge", borderwidth=1)
                row_frame.grid(row=i, column=0, padx=10, pady=10, sticky="w")

                self.edit_button = tb.Button(row_frame, text="Edit", bootstyle="success-link", image=self.pencil_icon, command=lambda i=i: self.edit_row(i))
                self.edit_button.grid(row=0, column=0, pady=10, padx=(10, 0), sticky="w")

                for col, label_name in enumerate(row_data, start=2):
                    label_value = row_data[label_name]
                    label_text = f"{label_value}"

                    if label_name == "id":
                        label_text = self.label_text
                        self.data_dict["id"] = label_text

                    width = column_widths[col - 2] if col - 2 < len(column_widths) else 20
                    label = tk.Label(row_frame, text=label_text, width=width, anchor="w", cursor="hand2")
                    label.grid(row=0, column=col, pady=10, sticky="w")

                    self.invoice_row_labels.append(label)

            total_height = len(self.get_invoice_fields) * row_height + offset
            canvas.config(scrollregion=(0, 0, total_height, 500))
            canvas.yview_moveto(0)

            self.name_widget.configure(state="default")
            self.name_widget.delete(0, tk.END)
            self.name_widget.configure(state="readonly")

    def clear_fields(self, frame_to_close):
        self.close_notebook(frame_to_close)
        self.receive_inventory()

    def validate_entries(self, entries, labels, labels_to_validate):
        for entry, label in zip(entries, labels):
            if label in labels_to_validate:
                entry_value = entry.get()
                if not entry_value:
                    Messagebox.show_error(f"{label} field cannot be empty!", title="Error")
                    return True
        return False

    def on_combobox_select(self, event):
        selected_item = self.combobox.get()
        if selected_item in self.combobox_methods:
            self.combobox_methods[selected_item]()
        self.combobox.set("Choose Medicine")

    def search_by_name(self):
        if self.current_notebook_tab:
            self.close_notebook(self.frame)
        if self.search_frame is not None:
            self.search_frame.destroy()
            self.search_frame_loaded = False
            self.current_notebook_tab = None
        self.from_inventory = True
        self.load_search()

    def edit_row(self, row_index):
        if row_index < 0 or row_index >= len(self.get_invoice_fields):
            return

        selected_data = self.get_invoice_fields[row_index]

        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Row")

        edit_entries = {}
        row_height = 20
        y = 20

        labels_to_display = ["quantity", "delivery_price", "expiry_date", "batch_number"]

        for label_name, label_value in selected_data.items():
            if label_name in labels_to_display:
                label = tk.Label(edit_window, text=label_name, width=15, anchor="w")
                label.grid(row=y, column=0, padx=5, pady=5, sticky="w")

                entry = tk.Entry(edit_window)
                entry.insert(0, label_value)
                entry.grid(row=y, column=1, padx=5, pady=5, sticky="ew")

                edit_entries[label_name] = entry
                y += row_height

        def update_row():
            for label_name, entry in edit_entries.items():
                updated_value = entry.get()
                selected_data[label_name] = updated_value

            self.controller.update_selected_data(selected_data)

            for i, label_name in enumerate(selected_data, start=1):
                if label_name == "total":
                    continue
                label_value = selected_data.get(label_name, "")
                label_text = f"{label_value}"

                if row_index * (len(selected_data) - 1) + i - 1 < len(self.invoice_row_labels):
                    label = self.invoice_row_labels[row_index * (len(selected_data) - 1) + i - 1]
                    label.config(text=label_text)

            edit_window.destroy()

            self.controller.recalculate_total()

        save_button = tk.Button(edit_window, text="Save", command=update_row)
        save_button.grid(row=y, column=1, padx=5, pady=10)

    def confirm_inventory(self, invoice_labels=None, invoice_entries=None, calculated=None):
        invoice_data = {}

        if not calculated:
            labels_to_validate = ["invoice_number", "supplier", "date", "sum"]


            if self.validate_entries(self.invoice_entries, invoice_labels, labels_to_validate):
                return

            self.invoice_entries = self.invoice_entries
            self.invoice_labels = invoice_labels
            for entry, label in zip(self.invoice_entries, invoice_labels):
                entry_value = entry.get()
                if label == "date":
                    if not self.controller.is_valid_date(entry_value):
                        expected_format = "YYYY-MM-DD"
                        self.show_date_format_error(entry_value, expected_format)
                        return

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

            if self.invoice_row_labels:
                self.edit_button.config(state="disabled")
                for label in self.invoice_row_labels:
                    label.config(state="disabled", cursor="arrow")

            invoice_data = self.controller.changee_supplier_name_to_id(invoice_data)

            invoice_id = self.controller.get_invoice_id()
            self.invoice_id_var.set(invoice_id)
            self.combobox.config(state="disabled")
            self.submit_button.config(state="disabled")
            self.controller.save_invoice(self.get_invoice_fields, invoice_data)

    def show_date_format_error(self, entry_value, expected_format):
        error_message = f"Invalid Date Format: {entry_value}. Please use the format: {expected_format}"
        Messagebox.show_error(error_message, title="Validation Error")

    def sales(self):
        sales_frame = tb.Frame(self.notebook)
        self.notebook.add(sales_frame, text="Sales")

        input_frame = tb.Frame(sales_frame)
        input_frame.pack(pady=20, anchor="w")

        product_name_label = tb.Label(input_frame, text="Product Name:")
        product_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.product_name_entry = tb.Entry(input_frame, width=50)
        self.product_name_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="w")

        search_button = tb.Button(input_frame, text="Search", command=self.search_product)
        search_button.grid(row=0, column=3, pady=10, sticky="w")

        tree_frame = tb.Frame(sales_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("id", "name", "quantity", "price")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize(), anchor="w")
            self.tree.column(col, width=100)

        self.tree.pack(fill='both', expand=True)

        self.tree2 = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree2.heading(col, text=col.capitalize(), anchor="w")
            self.tree2.column(col, width=100)

        self.tree2.pack(fill='both', expand=True)

        process_button = tb.Button(sales_frame, text="Process", command=self.on_process)
        process_button.pack(pady=10, anchor="center")

        self.total_label = tb.Label(sales_frame, text="Total sum: ", textvariable=self.controller.sales_total_var, borderwidth=1, relief="solid")
        self.total_label.pack(side="right", padx=10, pady=5)


    def search_product(self):
        self.tree.delete(*self.tree.get_children())

        searched_product_for_sale = self.product_name_entry.get()
        self.controller.search_product_for_sale(searched_product_for_sale)
        self.product_name_entry.delete(0, "end")

        for product in self.controller.filtered_medicine_data_list:
            self.tree.insert("", "end", values=(product["ID"], product["Name"], product["Quantity"], product["Price"]))

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.selected_product_id = self.tree.item(selected_item)["values"][0]
            self.selected_name = self.tree.item(selected_item)["values"][1]
            self.selected_quantity = self.tree.item(selected_item)["values"][2]
            self.selected_price = self.tree.item(selected_item)["values"][3]
            inventory_medicine = self.controller.medicine_inventory[self.selected_product_id]
            self.open_result_window(inventory_medicine)

    def open_result_window(self, inventory_medicine):
        self.result_window = tk.Toplevel(self.master)
        self.result_window.title("Search Results")

        self.tree3 = ttk.Treeview(self.result_window, columns=("ID", "Quantity", "Expiration Date", "Customer Price"))
        self.tree3.heading("ID", text="ID")
        self.tree3.heading("Quantity", text="Quantity")
        self.tree3.heading("Expiration Date", text="Expiration Date")
        self.tree3.heading("Customer Price", text="Customer Price")


        for product in inventory_medicine:
            self.tree3.insert("", "end", values=(product["ID"], product["Quantity"], product["Expiration Date"], product["Customer Price"]))

        self.tree3.bind("<<TreeviewSelect>>", self.on_second_tree_select)

        self.tree3.pack()

    def on_second_tree_select(self, event):
        selected_item = self.tree3.selection()
        if selected_item:
            self.item_id = self.tree3.item(selected_item)["values"][0]
            self.item_quantity = self.tree3.item(selected_item)["values"][1]
            self.item_price = self.tree3.item(selected_item)["values"][3]
            self.result_window.destroy()
            self.user_quantity = simpledialog.askinteger("Choose Quantity", f"Select quantity for {self.selected_name}:")
            self.tree.delete(*self.tree.get_children())
            if self.user_quantity is not None:
                if self.controller.lock_product(self.item_id):
                    Messagebox.show_error("This batch is currently being sold, and we need to wait.", title="Error")
                elif self.item_quantity < self.user_quantity:
                    Messagebox.show_error("Insufficient quantity available.", title="Error")
                else:
                    self.tree2.insert("", "end", values=(self.selected_product_id, self.selected_name, self.user_quantity, self.item_price))
                    self.controller.locked_products[self.item_id] = "locked"
                    self.controller.calculate_sales_total(self.user_quantity, self.item_price)

                self.tree2.bind("<<TreeviewSelect>>", self.delete_from_second_tree)

    def delete_from_second_tree(self, event):
        selected_items = self.tree2.selection()
        if selected_items:
            selected_item = selected_items[0]
            item_quantity = self.tree2.item(selected_item)["values"][2]
            item_price = self.tree2.item(selected_item)["values"][3]
            confirm_delete = Messagebox.show_question("Are you sure you want to delete this item?", buttons=['Yes:primary', 'No:secondary'])

            if confirm_delete == 'Yes':
                self.controller.recalculate_sale_sum(item_quantity, item_price)
                self.tree2.delete(selected_item)
                if self.item_id in self.controller.locked_products:
                    del self.controller.locked_products[self.item_id]

    def on_process(self):
        print(self.controller.total_sales)
        self.controller.locked_products = {}
        self.controller.total_sales = 0
        self.controller.sales_total_var.set(f"Total Sum: {self.controller.total_sales}")
