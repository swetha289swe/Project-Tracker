from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import ai, auth, project, project_members, tasks, users

tracker = FastAPI(title="Smart Project Tracker", version="0.1.0")
# 👇 Add this right after creating the app
tracker.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@tracker.exception_handler(Exception)
async def catch_all(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})


tracker.include_router(auth.router)
tracker.include_router(users.router)
tracker.include_router(project.router)
tracker.include_router(project_members.router)
tracker.include_router(tasks.router)
tracker.include_router(ai.router)

@tracker.get("/")
def root():
    return {"status": "ok"}


    # uv run uvicorn app.main:tracker  --reload

    # add changes to table
    # uv run alembic revision --autogenerate -m "add refresh tokens table"
    # create a folder in versions
    # cat alembic/versions/*add_refresh_tokens*.py
    # create a  table
    # uv run alembic upgrade head
    # verify nd restart
    # uv run python -c "import app.models; from app.db.base import Base; print(list(Base.metadata.tables.keys()))"
    