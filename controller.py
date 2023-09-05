from db import Base, engine, Session
from models import Medicine, Inventory

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
