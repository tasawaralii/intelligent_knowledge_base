from sqlalchemy import Boolean, Integer, String, ForeignKey, Column
from database.core import Base

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password_hashed = Column(String)
    disabled = Column(Boolean)