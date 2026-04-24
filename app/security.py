import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User

SESSION_COOKIE_NAME = "rms_session"
SESSION_DURATION_HOURS = int(os.getenv("SESSION_DURATION_HOURS", "12"))
PASSWORD_ITERATIONS = 390000


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str, salt: Optional[str] = None) -> str:
    active_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        active_salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"{active_salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False

    salt, saved_digest = stored_hash.split("$", 1)
    test_digest = hash_password(password, salt=salt).split("$", 1)[1]
    return secrets.compare_digest(saved_digest, test_digest)


def create_session(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(32)
    user.session_token = token
    user.session_expires_at = utcnow() + timedelta(hours=SESSION_DURATION_HOURS)
    user.last_login_at = utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return token


def clear_session(db: Session, user: User) -> None:
    user.session_token = None
    user.session_expires_at = None
    db.add(user)
    db.commit()


def get_user_from_request(request: Request, db: Session) -> Optional[User]:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None

    user = db.query(User).filter(User.session_token == token, User.is_active.is_(True)).first()
    if not user:
        return None

    if user.session_expires_at and user.session_expires_at < utcnow():
        clear_session(db, user)
        return None

    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_user_from_request(request=request, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    return get_user_from_request(request=request, db=db)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return current_user
