
from db import Base, engine, Session
from models import Medicine

class Controller:
    def __init__(self, model=None, view=None):
        self.model = model
        self.view = view

        self.create_database()

    def create_database(self):
        self.model.create_table()

        session = Session()
        count = session.query(Medicine).count()
        session.close()

        if count == 0:
            self.model.extract_and_insert_data()
        else:
            print("Database is not empty. Skipping data extraction and insertion.")

    def login(self, workplace):
        print(workplace)
        self.view.master.deiconify()
        self.view.top_login.destroy()


    def show_nomenclature(self, search_term, search_criteria):
        page = 1  # You can set the initial page to 1
        results_per_page = 10  # You can set the number of results per page
        nomenclature = self.model.search_medicines(search_term, search_criteria, page, results_per_page)
        self.view.create_notebook("Nomenclature", nomenclature, page, results_per_page)

