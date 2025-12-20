from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
import database.models as models
from database.core import engine
from routers.auth import router as auth_router
from routers.me import router as me_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(me_router)

models.Base.metadata.create_all(bind=engine)