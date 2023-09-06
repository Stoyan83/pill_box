from db import Base, engine, Session
from models import Medicine, Inventory
from decimal import Decimal
from tkinter import ttk
import tkinter as tk


class Controller:
    def __init__(self, view=None, **models):
        self.medicine_model = models.get('medicine_model')
        self.session_model = models.get('session_model')
        self.view = view

        self.create_database()

    def create_database(self):
        self.session_model.create_table()

        session = Session()
        count = session.query(Medicine).count()
        session.close()

        if count == 0:
            self.medicine_model.extract_and_insert_data()
            Inventory.generate_fake_data(num_records=100)
        else:
            print("Database is not empty. Skipping data extraction and insertion.")

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
        invoice_data["vat"] = invoice_sum * Decimal("0.20")
        invoice_data["total_sum"] = invoice_sum + invoice_data["vat"]
        self.view.confirm_inventory(calculated=invoice_data)

    def calculate_customer_price(self, delivery_price):
         return (Decimal(delivery_price) * Decimal("1.4")).quantize(Decimal("0.00"))

    def add_total(self, price):
        current_delivery_price = Decimal(self.view.delivery_price_var.get() or 0)
        new_sum = current_delivery_price + Decimal(price)
        self.view.delivery_price_var.set(new_sum.quantize(Decimal("0.00")))

    def add_medicine_to_invoice(self, medicine_id, name):
        self.view.name_widget.configure(state="default")
        self.view.name_widget.delete(0, tk.END)
        self.view.name_widget.insert(0, name)
        self.view.name_widget.configure(state="readonly")

    def humanize_text(self, label):
        return ' '.join(word.capitalize() for word in label.split('_'))
