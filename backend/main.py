from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database.models as models
from database.facts import Facts, FactEvidence
from database.core import engine
from routers.auth import router as auth_router
from routers.me import router as me_router
from routers.notes import router as notes_router
from routers.person import router as person_router
from routers.places import router as place_router
from routers.events import router as event_router
from routers.relations import router as relations_router

origins = ['http://localhost:5173']

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
app.include_router(person_router)
app.include_router(place_router)
app.include_router(event_router)
app.include_router(relations_router)

models.Base.metadata.create_all(bind=engine)