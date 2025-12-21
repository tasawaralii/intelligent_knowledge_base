from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database.models as models
from database.core import engine
from routers.auth import router as auth_router
from routers.me import router as me_router
from routers.notes import router as notes_router
from routers.relationships import router as relationships_router

origins = ['http://localhost:5174']

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(me_router)
app.include_router(notes_router)
app.include_router(relationships_router)

models.Base.metadata.create_all(bind=engine)