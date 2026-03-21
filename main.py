#Import system modules here
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.utils.config import templates_env
from app.routes import api_routes
from app.views import app_routes

# Declare Instances here
app = FastAPI()

# includes all routes from app.routes
app.include_router(api_routes)
app.include_router(app_routes)

# import templates/statics
app.mount("/static", StaticFiles(directory="statics"), name="static")

# Index Page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    template = templates_env.get_template("index.html")
    return template.render({"request": request,
                            "title": "Result Management",
                            "templates_env": templates_env})

# This auto starts your API server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)