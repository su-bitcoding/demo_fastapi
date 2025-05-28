from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer, Text
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



class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    image_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    image_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    image_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return username.strip()
    @validates('message')
    def validate_message(self, key, message):
        if not message or len(message.strip()) < 3:
            raise ValueError("message must be at least 3 characters long")
        return message.strip()

    @validates('file_name', 'image_name')
    def validate_file_names(self, key, filename):
        if filename:
            if len(filename) > 255:
                raise ValueError("Filename too long")
            return filename.replace('/', '').replace('\\', '')
        return filename
