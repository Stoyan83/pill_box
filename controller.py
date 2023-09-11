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
        self.supplier_model = models.get('supplier_model')
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

    def recalculate_total(self):
        total = Decimal('0.00')

        for row_data in self.view.get_invoice_fields:
            edited_row_total = Decimal(row_data.get("total", 0))
            total += edited_row_total

        self.view.delivery_price_var.set(str(total.quantize(Decimal("0.00"))))

    def add_medicine_to_invoice(self, medicine_id, name):
        self.update_name_entry(name)
        self.view.label_text = medicine_id
        self.cleanup_view()

    def update_name_entry(self, name):
        self.view.name_widget.configure(state="normal")
        self.view.name_widget.delete(0, tk.END)
        self.view.name_widget.insert(0, name)
        self.view.name_widget.configure(state="readonly")

    def update_selected_data(self, selected_data):
        delivery_price = selected_data.get("delivery_price", 0)
        quantity = selected_data.get("quantity", 0)
        selected_data["customer_price"] = self.calculate_customer_price(delivery_price)

        edited_row_total = Decimal(quantity) * Decimal(delivery_price)
        selected_data["total"] = str(edited_row_total.quantize(Decimal("0.00")))

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

    def get_suppliers(self):
        return self.supplier_model.get_all_supplier_names()

    def changee_supplier_name_to_id(self, invoice_data):
        supplier_name = invoice_data["supplier"]
        supplier_id = self.supplier_model.find_supplier_id_by_name(supplier_name)
        invoice_data["supplier"] = supplier_id
        return invoice_data

    def get_invoice_id(self):
        return self.invoice_model.get_id()

    def search_product_for_sale(self, searched_product_for_sale):
        medicine_data_list = self.medicine_model.seacrh_medicine_only_in_stock(searched_product_for_sale)

        self.filtered_medicine_data_list = []
        self.inventory_data_list = []
        self.medicine_inventory = {}

        for medicine_data in medicine_data_list:
            filtered_medicine_data = {
                "ID": medicine_data["ID"],
                "Name": medicine_data["Name"],
                "Quantity": medicine_data["Quantity"],
                "Price": medicine_data["Customer Price"]
            }

            self.filtered_medicine_data_list.append(filtered_medicine_data)
            inventory_data = medicine_data.get("Inventory")
            self.medicine_inventory[medicine_data["ID"]] = inventory_data

            if inventory_data:
                self.inventory_data_list.extend(inventory_data)

        # print("Filtered Medicine Data List:")
        # print(self.filtered_medicine_data_list)

        # print("Inventory Data List:")
        # print(self.inventory_data_list)
