from fastapi import APIRouter, Depends
from schemas import User
from dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=User)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user