from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import bcrypt
import os
from database.user import get_user, add_user, UserCreate
from database.core import get_db
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from schemas import User, Token

router = APIRouter(prefix="/auth")

SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))
ACCESS_TOKEN_EXPIRE_MINUTES = 1 * 24 * 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

def get_password_hash(plain_password):
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
    
def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.password_hashed):
        return False
    return user

def create_access_token(data : dict, expires_delta: timedelta):
    to_encode = data.copy()
    expires = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signup")
async def signup(user:UserCreate, db = Depends(get_db)) -> User:
    hashed_password = get_password_hash(user.password)
    user = add_user(user, hashed_password, db)
    return User(**user.__dict__)

@router.post("/signin", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Username or Password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(data={"sub":user.username}, expires_delta=access_token_expires)
    response = {"access_token" : access_token, "token_type": "bearer"}
    print(response)
    return response
    
     