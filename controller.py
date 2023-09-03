
from db import Base, engine, Session
from models import Medicine

class Controller:
    def __init__(self, model=None, view=None):
        self.model = model
        self.view = view

        self.create_database()

    def create_database(self):
        self.model.create()
