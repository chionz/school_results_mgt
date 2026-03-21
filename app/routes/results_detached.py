# results.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from jinja2 import Template

from main import app, get_db
from app.models import Student, Score, Class, ClassSubject, Subject

# ---------------------------
# Utility: Calculate results and rankings for a class
# ---------------------------
def calculate_class_ranking(class_id: int, db: Session):
    students = db.query(Student).filter(Student.class_id == class_id).all()
    student_totals = []

    for student in students:
        scores = db.query(Score).filter(Score.student_id == student.id).all()
        total = sum(s.test1 + s.test2 + s.test3 + s.exam for s in scores)
        student_totals.append({
            "student": student,
            "total": total
        })

    # Sort descending
    student_totals.sort(key=lambda x: x["total"], reverse=True)

    # Assign positions
    for index, item in enumerate(student_totals):
        item["position"] = index + 1

    return student_totals

# ---------------------------
# Endpoint: Generate HTML result for a student
# ---------------------------
@app.get("/result/{student_id}", response_class=HTMLResponse)
def generate_student_result(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get all subjects for this student's class
    links = db.query(ClassSubject).filter(ClassSubject.class_id == student.class_id).all()
    subjects = [db.query(Subject).get(link.subject_id) for link in links]

    # Get scores for this student
    scores = db.query(Score).filter(Score.student_id == student.id).all()
    score_dict = {s.subject_id: s for s in scores}

    # Build table rows
    table_rows = []
    overall_total = 0
    for subject in subjects:
        s = score_dict.get(subject.id)
        t1 = s.test1 if s else 0
        t2 = s.test2 if s else 0
        t3 = s.test3 if s else 0
        exam = s.exam if s else 0
        total = t1 + t2 + t3 + exam
        overall_total += total
        table_rows.append({
            "subject": subject.name,
            "test1": t1,
            "test2": t2,
            "test3": t3,
            "exam": exam,
            "total": total
        })

    average = overall_total / len(subjects) if subjects else 0

    # Get position
    ranking = calculate_class_ranking(student.class_id, db)
    position = next(item["position"] for item in ranking if item["student"].id == student.id)

    # Simple HTML template
    html_template = """
    <html>
    <head>
        <title>Result - {{ student.name }}</title>
        <style>
            table { border-collapse: collapse; width: 60%; }
            th, td { border: 1px solid black; padding: 5px; text-align: center; }
        </style>
    </head>
    <body>
        <h2>Class: {{ class_name }}</h2>
        <h3>Student: {{ student.name }} ({{ student.class_number }})</h3>
        <table>
            <tr>
                <th>Subject</th>
                <th>T1</th>
                <th>T2</th>
                <th>T3</th>
                <th>Exam</th>
                <th>Total</th>
            </tr>
            {% for row in rows %}
            <tr>
                <td>{{ row.subject }}</td>
                <td>{{ row.test1 }}</td>
                <td>{{ row.test2 }}</td>
                <td>{{ row.test3 }}</td>
                <td>{{ row.exam }}</td>
                <td>{{ row.total }}</td>
            </tr>
            {% endfor %}
        </table>
        <h4>Overall Total: {{ overall_total }}</h4>
        <h4>Average: {{ average }}</h4>
        <h4>Position: {{ position }}</h4>
    </body>
    </html>
    """

    template = Template(html_template)
    html_content = template.render(
        student=student,
        class_name=student.class_.name,
        rows=table_rows,
        overall_total=overall_total,
        average=round(average, 2),
        position=position
    )
    return HTMLResponse(content=html_content)