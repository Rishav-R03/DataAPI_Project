from sqlalchemy import Column, Integer, String,Float,Boolean
from database import Base
import datetime

class User(Base): # for register users
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    created_at = Column(String, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class CSVData(Base):
    __tablename__ = "csv_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Ensure these fields exist and match
    age = Column(Integer, nullable=False)
    occupation = Column(String, nullable=False)
    city = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    married = Column(Boolean, nullable=False)


