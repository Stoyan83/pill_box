
from sqlalchemy import Column, String, Integer
from db import Base, engine

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    surname = Column(String)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    def create(self):
        Base.metadata.create_all(engine)
