from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import get_current_user_optional
from app.services.users import user_service
from app.utils.config import templates_env

auth_viewrouter = APIRouter(tags=["Auth Views"])


@auth_viewrouter.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    if current_user:
        return RedirectResponse("/app/dashboard/", status_code=302)

    template = templates_env.get_template("login.html")
    bootstrap_admin = user_service.bootstrap_admin(db)
    return HTMLResponse(
        template.render(
            {
                "request": request,
                "title": "Sign In",
                "bootstrap_hint": bootstrap_admin is not None,
            }
        )
    )
