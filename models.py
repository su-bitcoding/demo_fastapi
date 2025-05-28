from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import validates, DeclarativeBase
import re

class Base(DeclarativeBase):
    pass


print("Base class created for SQLAlchemy models")
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    development = Column(String(255), nullable=False)
    production = Column(String(255), nullable=False)
    staging = Column(String(255), nullable=False)
    
    address = Column(String(255), nullable=False)
    name1 = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    
    @validates('email')
    def validate_email(self, key, address):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, address):
            raise ValueError("Invalid email address")
        return address.lower() 

