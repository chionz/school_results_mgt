from fastapi import APIRouter
from app.views.dashboard import viewrouter

app_routes = APIRouter(prefix="/app")


app_routes.include_router(viewrouter)