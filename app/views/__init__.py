from fastapi import APIRouter
from app.views.auth import auth_viewrouter
from app.views.dashboard import viewrouter

app_routes = APIRouter(prefix="/app")


app_routes.include_router(auth_viewrouter)
app_routes.include_router(viewrouter)
