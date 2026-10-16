from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import RefreshToken, User
from app.schemas.user import MessageResponse, Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"

def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=False,       # True in production (requires HTTPS)
        samesite="lax",
        max_age=settings.refresh_token_days * 24 * 60 * 60,
        path="/auth",        # cookie only sent to /auth/* routes
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role = payload.role
        # role = (payload.role or 'member').upper()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/login", response_model=Token)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
  
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(subject=str(user.id))

    raw_refresh = generate_refresh_token()
    refresh_row = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
    )
    db.add(refresh_row)
    db.commit()

    _set_refresh_cookie(response, raw_refresh)

    # logRes = {
    #     userDet :user,
    #     access_token:access_token,
    #     token_type : "bearer"
    # }
    # return Token(access_token=access_token)
    return Token(userDet =user,  
        access_token =access_token,
        token_type = "bearer")


@router.post("/refresh", response_model=Token)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_refresh is None:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    token_hash = hash_refresh_token(raw_refresh)
    stored = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    ).scalar_one_or_none()

    if (
        stored is None
        or stored.revoked
        or stored.expires_at < datetime.now(UTC)
    ):
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    # Rotation: revoke the old token, issue a brand new one
    stored.revoked = True

    new_raw_refresh = generate_refresh_token()
    new_refresh_row = RefreshToken(
        user_id=stored.user_id,
        token_hash=hash_refresh_token(new_raw_refresh),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
    )
    db.add(new_refresh_row)
    db.commit()

    _set_refresh_cookie(response, new_raw_refresh)

    access_token = create_access_token(subject=str(stored.user_id))
    return Token(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get(REFRESH_COOKIE_NAME)

    if raw_refresh is not None:
        token_hash = hash_refresh_token(raw_refresh)
        stored = db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).scalar_one_or_none()
        if stored is not None:
            stored.revoked = True
            db.commit()

    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/auth")
    return MessageResponse(message="Logged out successfully")