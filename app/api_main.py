from fastapi import FastAPI
from app.db.database import engine
from sqlalchemy import text


app = FastAPI()

@app.get("/ping")
def ping():
    return {'status': 'ok'}


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()
    return {"db_ok": result == 1}


@app.get("/info")
def info():
    return {"msg": "API is alive"}