from fastapi import FastAPI
from .api import register_routes
from .db import init_db
from .config import settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(fast_api_app: FastAPI):
    init_db()

    yield


app = FastAPI(lifespan=lifespan)

register_routes(app)
