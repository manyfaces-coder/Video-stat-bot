import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from app.db.models import Base

# грузим .env (временный простой вариант)
load_dotenv(find_dotenv())

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")


DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)


def init_db():
    Base.metadata.create_all(bind=engine)