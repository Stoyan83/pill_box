from sqlalchemy import Column, String, Integer
from db import Base, engine, Session
import xlrd


class Medicine(Base):
    __tablename__ = 'medicines'

    id = Column(Integer, autoincrement=True, primary_key=True)
    reg_number = Column(String)
    identifier = Column(String, unique=True)
    trade_name = Column(String)
    dosage_form_bg = Column(String)
    dosage_form_en = Column(String)
    active_ingredient_quantity = Column(String)
    packaging = Column(String)
    volume_dose_unit = Column(String)
    quantity_per_packaging = Column(String)
    marketing_authorization_holder = Column(String)
    country_bg = Column(String)
    inn = Column(String)
    atc_code = Column(String)
    prescription_mode = Column(String)

    def create_table(self):
        Base.metadata.create_all(engine)

    def extract_and_insert_data(self):

        workbook = xlrd.open_workbook('IAL_Register_07_2023.xls')
        sheet = workbook.sheet_by_index(0)

        session = Session()

        for row_index in range(1, sheet.nrows):
            row_data = sheet.row_values(row_index)
            medicine = Medicine(
                reg_number=row_data[0],
                identifier=row_data[1],
                trade_name=row_data[2],
                dosage_form_bg=row_data[3],
                dosage_form_en=row_data[4],
                active_ingredient_quantity=row_data[5],
                packaging=row_data[6],
                volume_dose_unit=row_data[7],
                quantity_per_packaging=row_data[8],
                marketing_authorization_holder=row_data[9],
                country_bg=row_data[10],
                inn=row_data[11],
                atc_code=row_data[12],
                prescription_mode=row_data[13]
            )
            session.add(medicine)

        session.commit()
        session.close()
