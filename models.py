from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="student")  # "student" or "lecturer"
    student_id = db.Column(db.String(50))
    phone = db.Column(db.String(30))
    course = db.Column(db.String(120))
    semester = db.Column(db.String(20))
    department = db.Column(db.String(120))
    college = db.Column(db.String(120))
    joined = db.Column(db.Date, default=date.today)


class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text)
    video_file = db.Column(db.String(200))   # filename in static/videos/
    video_url = db.Column(db.String(500))    # YouTube link
    lecturer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship("Question", backref="lecture", lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey("lecture.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500))
    option_b = db.Column(db.String(500))
    option_c = db.Column(db.String(500))
    option_d = db.Column(db.String(500))
    correct_option = db.Column(db.String(1))  # "A", "B", "C", or "D"
    explanation = db.Column(db.Text)
    wrong_reasons = db.Column(db.Text)  # JSON: {"A": "...", "B": "..."}


class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    score = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.relationship("AttemptAnswer", backref="attempt", lazy=True)


class AttemptAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempt.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    chosen_option = db.Column(db.String(1))
    is_correct = db.Column(db.Boolean, default=False)


class Watched(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey("lecture.id"), nullable=False)


class Explainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    chosen_option = db.Column(db.String(1), nullable=False)
    slides_json = db.Column(db.Text)  # JSON list of slides with audio_url
