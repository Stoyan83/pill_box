
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
