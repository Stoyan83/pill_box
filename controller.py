from db import Base, engine, Session
from models import Medicine, Inventory
from decimal import Decimal, ROUND_HALF_UP


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
        invoice = invoice_data
        invoice_sum = Decimal(invoice["sum"])
        invoice_vat = invoice_sum * Decimal("0.20")
        total_sum = invoice_sum + invoice_vat
        invoice["vat"] = invoice_vat
        invoice["total_sum"] = total_sum
        self.view.confirm_inventory(calculated=invoice)

    def calculate_customer_price(self, delivery_price):
        delivery_price_decimal = Decimal(delivery_price)
        multiplier = Decimal('1.4')
        customer_price = delivery_price_decimal * multiplier
        customer_price = customer_price.quantize(Decimal('0.00'))
        return customer_price

    def humanize_text(self, label):
        return ' '.join(word.capitalize() for word in label.split('_'))
