from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from api.recipe import recipe_router

universes: List[dict]
DEBUG: bool = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app: FastAPI = FastAPI(title="SynTOD api implementation", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    recipe_router,
    prefix="/recipe",
)
