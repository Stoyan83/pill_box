from sqlalchemy import Column, String, Integer
from db import Base, engine, Session
import xlrd


class SessionManager:
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = Session()
        return cls._session

    @classmethod
    def close_session(cls):
        if cls._session:
            cls._session.close()
            cls._session = None


class Medicine(Base):
    __tablename__ = 'medicines'

    id = Column(Integer, autoincrement=True, primary_key=True)
    reg_number = Column(String)
    identifier = Column(String, unique=True)
    trade_name = Column(String, index=True)
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

    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session

    def create_table(self):
        Base.metadata.create_all(engine)

    def extract_and_insert_data(self):
        workbook = xlrd.open_workbook('IAL_Register_07_2023.xls')
        sheet = workbook.sheet_by_index(0)
        session = SessionManager.get_session()

        for row_index in range(1, sheet.nrows):
            row_data = sheet.row_values(row_index)
            medicine = Medicine(
                session=session,
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
            self.session.add(medicine)

        self.session.commit()

    def search_medicines(self, search_term, search_criteria, page=1, results_per_page=10):
        query = None

        if search_criteria == "ID":
            query = self.session.query(Medicine).filter(Medicine.id == search_term)
        elif search_criteria == "Name":
            query = self.session.query(Medicine).filter(Medicine.trade_name.like(f"%{search_term}%"))

        if query is not None:
            offset = (page - 1) * results_per_page

            medicines = query.offset(offset).limit(results_per_page).all()

            medicine_data_list = []

            for medicine in medicines:
                medicine_data = {
                    "Medicine ID": medicine.id,
                    "Trade Name": medicine.trade_name,
                    "Active Ingredient Quantity": medicine.active_ingredient_quantity,
                    "Registration Number": medicine.reg_number,
                    "Identifier": medicine.identifier,
                    "Dosage Form (BG)": medicine.dosage_form_bg,
                    "Dosage Form (EN)": medicine.dosage_form_en,
                    "Packaging": medicine.packaging,
                    "Volume Dose Unit": medicine.volume_dose_unit,
                    "Quantity per Packaging": medicine.quantity_per_packaging,
                    "Marketing Authorization Holder": medicine.marketing_authorization_holder,
                    "Country (BG)": medicine.country_bg,
                    "INN": medicine.inn,
                    "ATC Code": medicine.atc_code,
                    "Prescription Mode": medicine.prescription_mode
                }
                medicine_data_list.append(medicine_data)

            return medicine_data_list

        return []
