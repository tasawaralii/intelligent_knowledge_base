from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"status": "ok"}

from fastapi.middleware.cors import CORSMiddleware
from .api.routes import test as test_router

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_router.router, prefix="/api")