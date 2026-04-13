from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import db
from api.config import settings
from api.routers import game, health


@asynccontextmanager
async def lifespan(application: FastAPI):
    db.connect()
    yield
    db.disconnect()


app = FastAPI(title="RAG Narrative Engine API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(game.router)
