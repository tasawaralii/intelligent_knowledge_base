from fastapi import APIRouter, Depends, HTTPException, status
from schemas import User, TokenData
from database.core import get_db
from jose import jwt, JWTError
from database.user import get_user
from .auth import oauth2_scheme
import os
router = APIRouter(prefix="/user")

SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could Not Validate Credentials", headers={"WWW-Authenticate" : "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
        
    except JWTError:
        raise credential_exception
    
    user = get_user(token_data.username, db)
    if user is None:
        raise credential_exception
    return user


@router.get("/me", response_model=User)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user