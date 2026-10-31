"""HAESS Support Platform – FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine
from app.seed import seed_data
from app.db import SessionLocal

# Import routers – stubs for now, filled phase by phase
from app.api import tickets, tasks, handoffs, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title="HAESS Support Platform", version="0.1.0", lifespan=lifespan)

app.include_router(tickets.router)
app.include_router(tasks.router)
app.include_router(handoffs.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}

