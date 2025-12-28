from sqlalchemy import Boolean, Integer, Date, String, ForeignKey, Column, DateTime, Text, Table, CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from database.core import Base
# Facts models are imported separately to avoid circular imports


note_persons = Table(
    'note_persons',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('note_id', Integer, ForeignKey('notes.id', ondelete='CASCADE'), index=True),
    Column('person_id', Integer, ForeignKey('persons.id', ondelete='CASCADE'), index=True),
    Column('mention_text', String(200), nullable=True),  # Store the actual @mention text
    Column('position', Integer, nullable=True),  # Character position in note content
    Column('created_at', DateTime, default=datetime.utcnow)
)

note_places = Table(
    'note_places',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('note_id', Integer, ForeignKey('notes.id', ondelete='CASCADE'), index=True),
    Column('place_id', Integer, ForeignKey('places.id', ondelete='CASCADE'), index=True),
    Column('mention_text', String(200), nullable=True),
    Column('position', Integer, nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

note_events = Table(
    'note_events',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('note_id', Integer, ForeignKey('notes.id', ondelete='CASCADE'), index=True),
    Column('event_id', Integer, ForeignKey('events.id', ondelete='CASCADE'), index=True),
    Column('mention_text', String(200), nullable=True),
    Column('position', Integer, nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)
class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password_hashed = Column(String)
    
    # Relationships
    notes = relationship("Notes", back_populates="owner", cascade="all, delete-orphan")
    persons = relationship("Persons", back_populates="owner", cascade="all, delete-orphan")
    places = relationship("Places", back_populates="owner", cascade="all, delete-orphan")
    events = relationship("Events", back_populates="owner", cascade="all, delete-orphan")


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
    
    # Relationships
    owner = relationship("Users", back_populates="notes")
    
    # Many-to-many relationships
    mentioned_persons = relationship(
        "Persons",
        secondary=note_persons,
        backref="mentioned_in_notes"
    )
    mentioned_places = relationship(
        "Places",
        secondary=note_places,
        backref="mentioned_in_notes"
    )
    mentioned_events = relationship(
        "Events",
        secondary=note_events,
        backref="mentioned_in_notes"
    )
    
    # Fact relationships
    note_facts = relationship("NoteFact", back_populates="note", cascade="all, delete-orphan")

class Persons(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # Basic Info
    first_name = Column(String(100))
    last_name = Column(String(100), nullable=True)
    father_name = Column(String(100), nullable=True)
    
    # Unique identifiers
    slug = Column(String(100), unique=True, index=True, nullable=True)  # For @mentions like @p.john
    cnic = Column(CHAR(13), unique=True, nullable=True)
    phone_number = Column(CHAR(11), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    picture_url = Column(String(500), nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)

    # Demographics
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("Users", back_populates="persons")

class PersonChanges(Base):
    __tablename__ = "person_changes"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="CASCADE"), index=True)
    field = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)

class Places(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=True)  # For @mentions like @pl.office
    place_type = Column(String(50), nullable=True)  # home, office, school, etc.
    
    # Address
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Extra info
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("Users", back_populates="places")
    events = relationship("Events", back_populates="place")

class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=True)  # For @mentions like @e.meeting
    event_type = Column(String(50), nullable=True)  # meeting, incident, ceremony
    
    # Time
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    
    # Location
    place_id = Column(Integer, ForeignKey("places.id"), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("Users", back_populates="events")
    place = relationship("Places", back_populates="events")