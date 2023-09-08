from db import Session
from models import Medicine, Supplier
from decimal import Decimal
import tkinter as tk
from datetime import datetime


class Controller:
    def __init__(self, view=None, **models):
        self.medicine_model = models.get('medicine_model')
        self.session_model = models.get('session_model')
        self.invoice_model = models.get('invoice_model')
        self.invoice_inventory_model = models.get('invoice_inventory_model')
        self.view = view

        self.create_database()

    def create_database(self):
        self.session_model.create_table()

        session = Session()
        count = session.query(Supplier).count()
        session.close()

        if count == 0:
            self.medicine_model.extract_and_insert_data()
            Supplier.create_fake_suppliers()

    def login(self, workplace):
        print(workplace)
        self.view.master.deiconify()
        self.view.top_login.destroy()


    def show_nomenclature(self, search_term, search_criteria):
        page = 1
        results_per_page = 10
        nomenclature = self.medicine_model.search_medicines(search_term, search_criteria, page, results_per_page)
        self.view.create_notebook("Nomenclature", nomenclature, page, results_per_page)

    def calculate_total(self, invoice_data):
        invoice_sum = Decimal(invoice_data["sum"])
        vat_rate = Decimal("0.20")
        invoice_data["vat"] = (invoice_sum * vat_rate).quantize(Decimal("0.00"))
        invoice_data["total_sum"] = (invoice_sum + invoice_data["vat"]).quantize(Decimal("0.00"))
        self.view.confirm_inventory(calculated=invoice_data)

    def calculate_customer_price(self, delivery_price):
         return (Decimal(delivery_price) * Decimal("1.4")).quantize(Decimal("0.00"))

    def add_total(self, price, quantity):
        current_delivery_price = Decimal(self.view.delivery_price_var.get() or 0)
        new_sum = current_delivery_price + (Decimal(quantity) * Decimal(price))
        self.view.delivery_price_var.set(new_sum.quantize(Decimal("0.00")))

    def add_medicine_to_invoice(self, medicine_id, name):
        self.update_name_entry(name)
        self.view.label_text = medicine_id
        self.cleanup_view()

    def update_name_entry(self, name):
        self.view.name_widget.configure(state="normal")
        self.view.name_widget.delete(0, tk.END)
        self.view.name_widget.insert(0, name)
        self.view.name_widget.configure(state="readonly")

    def cleanup_view(self):
        self.view.close_notebook(self.view.frame)
        self.view.current_notebook_tab = None

    def humanize_text(self, label):
        return ' '.join(word.capitalize() for word in label.split('_'))

    def save_invoice(self, get_invoice_fields, invoice_data):
        self.invoice_model.create_invoice(invoice_data, get_invoice_fields)


    def validate_numeric_input(self, value):
        try:
            if value == "" or isinstance(float(value), (int, float)):
                return True
            else:
                return False
        except ValueError:
            return False

    def is_valid_date(self, date_string):
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
