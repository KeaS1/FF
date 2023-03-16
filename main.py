from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    pass
class Service(Base):
    __tablename__ = "service"
    service_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    pay: Mapped[int] = mapped_column()
    customers: Mapped[List["Customers"]] = relationship(secondary="customers_in_service",back_populates="service")
    def __repr__(self) -> str:
        return f"Service(service_id={self.service_id!r},name={self.name!r},pay={self.pay!r})"
    

class Customers(Base):
    __tablename__ = "customers"
    customers_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    second_name: Mapped[str] = mapped_column(String(30))
    addresses: Mapped[str] = mapped_column(String(64))
    service: Mapped[List["Service"]] = relationship(secondary="customers_in_service", back_populates="customers")
    phone: Mapped["Phone"] = relationship(back_populates="customers")
    def __repr__(self) -> str:
        return f"Customers(customers_id={self.customers_id!r}, first_name={self.first_name!r}, second_name={self.second_name!r}, phone={self.phone!r}, addresses={self.addresses!r}, service={self.service!r})"

class Phone(Base):
    __tablename__ = "phone"
    phone: Mapped[str] = mapped_column(String(30))
    fk_customers_id: Mapped[int] = mapped_column(ForeignKey("customers.customers_id"),primary_key=True)
    customers: Mapped["Customers"] = relationship(back_populates="phone")
    def __repr__(self) -> str:
        return f"Phone(phone={self.phone!r})"
    

class Customers_in_service(Base):
    __tablename__ = "customers_in_service"
    fk_customers_id: Mapped[int] = mapped_column(ForeignKey("customers.customers_id"),primary_key=True)
    fk_service_id: Mapped[int] = mapped_column(ForeignKey("service.service_id"),primary_key=True)
    def __repr__(self) -> str:
        return f"Customers_in_service(fk_customers_id={self.fk_customers_id!r},fk_service_id={self.fk_service_id!r})"

from sqlalchemy import create_engine
engine = create_engine("postgresql+psycopg2://postgres:12345@localhost:5433/qq1", echo=True)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


from sqlalchemy.orm import Session
with Session(engine) as session:
    PI = Service(name="Пушка интернет", pay = 500)
    GPI = Service(name="Жиесть интернет пушка", pay = 1000)
    FHIM = Service(name="Летает как в Москве", pay = 2000 )


    session.add_all([
        Customers(first_name = "Владислав",second_name = "Козанцев",addresses = "Сибирская 81 кв 95", service=[PI,GPI], phone=Phone(phone="602379436346634")),
        Customers(first_name = "Семен",second_name = "Cосиков",addresses = "Костромская 98 кв 105", service= [PI], phone=Phone(phone="6023794335223534")),
        Customers(first_name = "Иван",second_name = "Золоторев",addresses = "Костромская 98 кв 106", service= [PI,GPI,FHIM],phone=Phone(phone="602323523546634"))    
    ])
    session.commit()

with Session(engine) as session:
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload

    stmt = select(Customers).options(joinedload(Customers.service))
    ss = session.execute(stmt).unique().scalars()
    print(ss)
    for s in ss:
        print(s.first_name)
        for i in s.service:
            print(i.name)
        print()

from fastapi import FastAPI
from os import environ
import databases
SQLALCHEMY_DATABASE_URL = (f"postgresql+psycopg2://postgres:12345@localhost:5433/qq1")
database = databases.Database(SQLALCHEMY_DATABASE_URL)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/customers")
def read_customers():
    sosok = select([])