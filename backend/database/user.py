from sqlalchemy.orm import Session
import database.models as models
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    password: str


def get_user(username, db: Session) :
    result = db.query(models.Users).filter(models.Users.username == username).first()
    return result

def add_user(user : UserCreate, hashed_password, db: Session) -> UserCreate:
    db_user = models.Users(username=user.username,email=user.email,first_name=user.first_name,last_name=user.last_name, password_hashed=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user