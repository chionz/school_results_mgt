from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.classes import Class
from app.security import get_current_user_optional
from app.services.classes import class_service
from app.services.subjects import subject_service
from app.services.users import user_service
from app.utils.config import templates_env

viewrouter = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def build_navigation(request_path: str, current_user):
    items = [
        {"href": "/app/dashboard/", "label": "Overview"},
        {"href": "/app/dashboard/classes", "label": "Classes"},
        {"href": "/app/dashboard/score-entry", "label": "Score Entry"},
        {"href": "/app/dashboard/classes/result", "label": "Class Results"},
    ]
    if current_user.is_admin:
        items.insert(2, {"href": "/app/dashboard/add-subject", "label": "Subjects"})
        items.insert(3, {"href": "/app/dashboard/teachers", "label": "Teachers"})

    for item in items:
        item["active"] = request_path == item["href"]
    return items


def render_page(
    request: Request,
    template_name: str,
    current_user,
    title: str,
    description: str,
    **context,
):
    template = templates_env.get_template(template_name)
    return HTMLResponse(
        template.render(
            {
                "request": request,
                "title": title,
                "page_description": description,
                "navigation": build_navigation(request.url.path, current_user),
                "current_user": current_user,
                **context,
            }
        )
    )


def require_dashboard_user(current_user):
    if not current_user:
        return RedirectResponse("/app/login", status_code=302)
    return None


@viewrouter.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect

    classes = class_service.fetch_all(db=db, current_user=current_user)
    all_subjects = subject_service.get_all_subjects(db=db)
    form_classes = [cls for cls in classes if cls.form_teacher_id == current_user.id]
    teaching_assignments = [
        assignment
        for cls in classes
        for assignment in cls.class_subjects
        if assignment.teacher_id == current_user.id
    ]

    return render_page(
        request=request,
        template_name="dashboard.html",
        current_user=current_user,
        title="Dashboard",
        description="See your classes, teaching assignments, and the next steps that matter most.",
        classes=[class_service.serialize_class(cls) for cls in classes],
        total_classes=len(classes),
        total_subjects=len(all_subjects),
        form_classes=[class_service.serialize_class(cls) for cls in form_classes],
        teaching_assignments=[subject_service.serialize_assignment(item) for item in teaching_assignments],
    )


@viewrouter.get("/classes", response_class=HTMLResponse)
def class_create(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect

    classes = class_service.fetch_all(db=db, current_user=current_user)
    teachers = user_service.list_teachers(db=db) if current_user.is_admin else []
    return render_page(
        request=request,
        template_name="create-class.html",
        current_user=current_user,
        title="Classes",
        description="Manage classes, assign form teachers, and jump straight into students or results.",
        classes=[class_service.serialize_class(cls) for cls in classes],
        teachers=teachers,
        is_admin=current_user.is_admin,
    )


@viewrouter.get("/teachers", response_class=HTMLResponse)
def teachers_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect
    if not current_user.is_admin:
        return RedirectResponse("/app/dashboard/", status_code=302)

    teachers = user_service.list_teachers(db=db)
    return render_page(
        request=request,
        template_name="teachers.html",
        current_user=current_user,
        title="Teachers",
        description="Create staff accounts and assign the right person to each class or subject.",
        teachers=teachers,
    )


@viewrouter.get("/classes/result", response_class=HTMLResponse)
def class_result(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect

    accessible_classes = class_service.fetch_all(db=db, current_user=current_user)
    result_classes = accessible_classes if current_user.is_admin else [
        cls for cls in accessible_classes if cls.form_teacher_id == current_user.id
    ]
    return render_page(
        request=request,
        template_name="class-result.html",
        current_user=current_user,
        title="Class Results",
        description="Form teachers can review the full class, compare positions, and open printable result sheets.",
        classes=[class_service.serialize_class(cls) for cls in result_classes],
    )


@viewrouter.get("/student-result", response_class=HTMLResponse)
def student_result(
    request: Request,
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect
    return render_page(
        request=request,
        template_name="result.html",
        current_user=current_user,
        title="Student Result Sheet",
        description="Printable individual result sheet for a single student.",
    )


@viewrouter.get("/add-subject", response_class=HTMLResponse)
def add_subject(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect
    if not current_user.is_admin:
        return RedirectResponse("/app/dashboard/", status_code=302)

    classes = db.query(Class).order_by(Class.name.asc()).all()
    teachers = user_service.list_teachers(db=db)
    subjects = subject_service.get_all_subjects(db=db)
    selected_class = request.query_params.get("class_id")

    return render_page(
        request=request,
        template_name="add-subject-to-class.html",
        current_user=current_user,
        title="Subjects",
        description="Create subjects, assign them to classes, and choose the teacher who is allowed to edit scores.",
        classes=[class_service.serialize_class(cls) for cls in classes],
        teachers=teachers,
        subjects=subjects,
        selected_class=selected_class,
    )


@viewrouter.get("/add-student", response_class=HTMLResponse)
def add_student(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect

    class_id = request.query_params.get("class_id")
    if not class_id:
        return RedirectResponse("/app/dashboard/classes", status_code=302)

    class_obj = class_service.get_by_id(db, int(class_id))
    if not class_service.can_manage_students(current_user, class_obj):
        return RedirectResponse("/app/dashboard/classes", status_code=302)

    students = class_obj.students
    return render_page(
        request=request,
        template_name="create-student.html",
        current_user=current_user,
        title="Students",
        description="Keep the class register clean so every score and result sheet maps to the right learner.",
        class_obj=class_service.serialize_class(class_obj),
        students=students,
    )


@viewrouter.get("/score-entry", response_class=HTMLResponse)
def score_entry(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    redirect = require_dashboard_user(current_user)
    if redirect:
        return redirect

    classes = class_service.fetch_all(db=db, current_user=current_user)
    return render_page(
        request=request,
        template_name="score-entry.html",
        current_user=current_user,
        title="Score Entry",
        description="Enter scores only for the subjects assigned to you, with totals calculated instantly.",
        classes=[class_service.serialize_class(cls) for cls in classes],
    )
