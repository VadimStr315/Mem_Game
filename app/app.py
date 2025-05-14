from fastapi import FastAPI
from api.analitic.router import analitics_router
from api.courses.router import course_router
from api.users.router import users_router
import logging
from fastapi.middleware.cors import CORSMiddleware
from database import db_core, redis_client

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
    await db_core.init_db()    
    await redis_client.connect()
# Подключение маршрутов

app.include_router(analitics_router)
app.include_router(course_router)
app.include_router(users_router)