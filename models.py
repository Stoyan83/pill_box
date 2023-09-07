import random
from datetime import date, timedelta
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
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

    def create_table(self):
        Base.metadata.create_all(engine)


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

    inventory = relationship('Inventory', back_populates='medicine')
    inventory_invoices = relationship('InvoiceInventories', back_populates='medicine')  # Added this line


    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session

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
            query = self.session.query(Medicine).filter(Medicine.trade_name.like(f"{search_term}%"))

        if query is not None:
            offset = (page - 1) * results_per_page

            medicines = query.offset(offset).all()

            medicine_data_list = []

            for medicine in medicines:

                inventory_quantities = [inv.quantity for inv in medicine.inventory]
                total_inventory_quantity = sum(inventory_quantities)

                medicine_data = {
                    "ID": medicine.id,
                    "Trade Name": medicine.trade_name,
                    "Quantity": total_inventory_quantity,
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


class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    batch_number = Column(String)
    expiration_date = Column(Date)
    delivery_price = Column(Numeric(precision=10, scale=2))
    customer_price = Column(Numeric(precision=10, scale=2))

    medicine = relationship('Medicine', back_populates='inventory')

    def __init__(self, medicine_id, quantity, batch_number, expiration_date, delivery_price, customer_price):
        self.medicine_id = medicine_id
        self.quantity = quantity
        self.batch_number = batch_number
        self.expiration_date = expiration_date
        self.delivery_price = delivery_price
        self.customer_price = customer_price

    @staticmethod
    def generate_fake_data(num_records=100):
        session = SessionManager.get_session()

        medicine_ids = [medicine.id for medicine in session.query(Medicine).all()]

        for _ in range(num_records):
            medicine_id = random.choice(medicine_ids)
            inventory_data = Inventory._generate_random_inventory_data(medicine_id)
            inventory = Inventory(**inventory_data)
            session.add(inventory)

        session.commit()

    @staticmethod
    def _generate_random_inventory_data(medicine_id):
        return {
            'medicine_id': medicine_id,
            'quantity': random.randint(1, 100),
            'batch_number': str(random.randint(100000, 999999)),
            'expiration_date': date.today() + timedelta(days=random.randint(365, 730)),
            'delivery_price': random.randint(10, 100),
            'customer_price': random.randint(50, 200)
        }


class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    initials = Column(String, nullable=False)

    invoices = relationship('Invoice', back_populates='supplier')

    def __init__(self, name, initials):
        self.name = name
        self.initials = initials


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, autoincrement=True, primary_key=True)
    number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    invoice_sum = Column(Numeric(precision=10, scale=2), nullable=False)
    vat = Column(Numeric(precision=10, scale=2), nullable=False)
    total_sum = Column(Numeric(precision=10, scale=2), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)

    supplier = relationship('Supplier', back_populates='invoices')
    invoice_inventories = relationship('InvoiceInventories', back_populates='invoice')  # Added this line


    def __init__(self, number, date, sum, vat, total_sum, supplier_id):
        self.number = number
        self.date = date
        self.sum = sum
        self.vat = vat
        self.total_sum = total_sum
        self.supplier_id = supplier_id


class InvoiceInventories(Base):
    __tablename__ = 'invoice_inventories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    batch_number = Column(String)
    expiration_date = Column(Date)
    delivery_price = Column(Numeric(precision=10, scale=2))
    customer_price = Column(Numeric(precision=10, scale=2))
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)

    medicine = relationship('Medicine', back_populates='inventory_invoices')
    invoice = relationship('Invoice', back_populates='invoice_inventories')

    def __init__(self, medicine_id, quantity, batch_number, expiration_date, delivery_price, customer_price, invoice_id):
        self.medicine_id = medicine_id
        self.quantity = quantity
        self.batch_number = batch_number
        self.expiration_date = expiration_date
        self.delivery_price = delivery_price
        self.customer_price = customer_price
        self.invoice_id = invoice_id
