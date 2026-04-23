from fastapi import APIRouter,  Request
from fastapi.responses import HTMLResponse
from app.utils.config import templates_env

# This maps and tags routes 
viewrouter = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# This is an endpoint
@viewrouter.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    template = templates_env.get_template("dashboard.html")
    return template.render({
        "request": request,
        "title": "User Dashboard",
        "templates_env": templates_env,
    })

@viewrouter.get("/classes", response_class=HTMLResponse)
def class_create(request: Request):
    template = templates_env.get_template("create-class.html")
    return template.render({
        "request": request,
        "title": "Class Dashboard",
        "templates_env": templates_env,
    })

@viewrouter.get("/classes/result", response_class=HTMLResponse)
def class_result(request: Request):
    template = templates_env.get_template("class-result.html")
    return template.render({
        "request": request,
        "title": "Class Dashboard",
        "templates_env": templates_env,
    })

@viewrouter.get("/student-result", response_class=HTMLResponse)
def student_result(request: Request):
    template = templates_env.get_template("result.html")
    return template.render({
        "request": request,
        "title": "Class Dashboard",
        "templates_env": templates_env,
    })

@viewrouter.get("/add-subject", response_class=HTMLResponse)
def add_subject(request: Request):
    template = templates_env.get_template("add-subject-to-class.html")
    return template.render({
        "request": request,
        "title": "Class Dashboard",
        "templates_env": templates_env,
    })

@viewrouter.get("/add-student", response_class=HTMLResponse)
def add_student(request: Request):
    template = templates_env.get_template("create-student.html")
    return template.render({
        "request": request,
        "title": "Class Dashboard",
        "templates_env": templates_env,
    })



