# get_db, get_current_user,
from collections.abc import Iterator

from app.db.session import SessionLocal


def get_db() -> Iterator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()