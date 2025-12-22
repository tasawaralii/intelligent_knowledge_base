from sqlalchemy import Boolean, Integer, Date, String, ForeignKey, Column, DateTime, Text, Table, CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from database.core import Base

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password_hashed = Column(String)
    notes = relationship("Notes", back_populates="owner")
    persons = relationship("Persons", back_populates="owner")
    places = relationship("Places", back_populates="owner")
    events = relationship("Events", back_populates="owner")

class Notes(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=True)
    content = Column(Text, nullable=True)  # Markdown supported
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    in_archive = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("Users", back_populates="notes")

class Persons(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    father_name = Column(String(100), nullable=True)
    cnic = Column(CHAR(13), unique=True, nullable=True)
    phone_number = Column(CHAR(11), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)

    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    owner = relationship("Users", back_populates="persons")


class Places(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String(200), nullable=False, index=True)
    place_type = Column(String(50), nullable=True)  # home, office, school, etc.
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    # Extra info
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    owner = relationship("Users", back_populates="places")
    event = relationship("Events")

class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(200), nullable=False, index=True)
    event_type = Column(String(50), nullable=True)  # meeting, incident, ceremony
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    owner = relationship("Users", back_populates="events")
    place = relationship("Places")