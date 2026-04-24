from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.security import get_user_from_request
from app.utils.config import templates_env
from app.routes import api_routes
from app.views import app_routes
from app.services.users import user_service

# Declare Instances here
app = FastAPI()

# includes all routes from app.routes
app.include_router(api_routes)
app.include_router(app_routes)

# import templates/statics
app.mount("/static", StaticFiles(directory="statics"), name="static")


@app.on_event("startup")
def bootstrap_admin():
    db: Session = SessionLocal()
    try:
        user_service.bootstrap_admin(db)
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db: Session = SessionLocal()
    try:
        current_user = get_user_from_request(request=request, db=db)
    finally:
        db.close()

    if current_user:
        return RedirectResponse("/app/dashboard/", status_code=302)

    template = templates_env.get_template("index.html")
    return template.render(
        {
            "request": request,
            "title": "Result Management",
            "templates_env": templates_env,
        }
    )

# This auto starts your API server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
