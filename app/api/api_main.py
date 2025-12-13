from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import text
from .v1 import router as v1_router
from app.db.database import get_session, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(v1_router)


@app.get("/db-check")
async def db_check(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    return {"db_ok": value == 1}


@app.get("/info")
def info():
    return {"msg": "API is alive"}