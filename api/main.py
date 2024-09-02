from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from api.recipe import recipe_router
from api.car import car_router
from api.doctor import doctor_router
from api.hotel import hotel_router
from api.worker import worker_router

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

app.include_router(
    car_router,
    prefix="/car",
)

app.include_router(
    doctor_router,
    prefix="/doctor",
)

app.include_router(
    hotel_router,
    prefix="/hotel",
)

app.include_router(
    worker_router,
    prefix="/worker",
)
