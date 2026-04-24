from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.users import LoginSchema
from app.security import SESSION_COOKIE_NAME, create_session, get_current_user
from app.services.users import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(schema: LoginSchema, db: Session = Depends(get_db)):
    user = user_service.authenticate(db=db, username=schema.username.strip(), password=schema.password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid username or password"},
        )

    token = create_session(db=db, user=user)
    response = JSONResponse(
        content={
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
        }
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 12,
        path="/",
    )
    return response


@router.post("/logout")
def logout(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.session_token = None
    current_user.session_expires_at = None
    db.add(current_user)
    db.commit()

    payload = JSONResponse(content={"message": "Logged out"})
    payload.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return payload


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_admin": current_user.is_admin,
    }
