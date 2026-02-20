from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

#Creates a base class, all database models inherit from it.
Base = declarative_base()

#SQLAlchemy model. It represents the items table.
class ItemDB(Base):
    #actual table name in PostgreSQL.
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) #nullable=False = NOT NULL (required)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    cost_price = Column(Float, nullable=False)
    supplier_secret = Column(String, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False) # for migration
