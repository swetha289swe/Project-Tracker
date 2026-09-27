from fastapi import FastAPI

from app.routers import auth, users

tracker = FastAPI(title="Smart Project Tracker", version="0.1.0")

tracker.include_router(auth.router)
tracker.include_router(users.router)

@tracker.get("/")
def root():
    return {"status": "ok"}


    # uv run uvicorn app.main:tracker  --reload