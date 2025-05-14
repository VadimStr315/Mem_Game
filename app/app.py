from database.postgres import postgresManager
from database.redis import redisManager
from routers.cards.routers import cards_router
from routers.collections.routers import collection_router
from routers.users.routers import users_router

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await postgresManager.init_db()    
    await redisManager.connect()
# Подключение маршрутов

app.include_router(cards_router)
app.include_router(collection_router)
app.include_router(users_router)