from fastapi import APIRouter

from app.routes.users import router as users_router
from app.routes.classes import classrouter
from app.routes.students import studentrouter
from app.routes.subjects import subjectrouter
from app.routes.scores import scoresrouter


api_routes = APIRouter(prefix="/api")

api_routes.include_router(users_router)
api_routes.include_router(classrouter)
api_routes.include_router(studentrouter)
api_routes.include_router(subjectrouter)
api_routes.include_router(scoresrouter)