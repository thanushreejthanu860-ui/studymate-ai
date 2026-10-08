import os
import json
from functools import wraps
from datetime import datetime, date

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learning.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join("static", "videos")
app.config["UPLOADS_FOLDER"] = "uploads"

from models import db, User, Lecture, Question, Attempt, AttemptAnswer, Watched, Explainer

db.init_app(app)

with app.app_context():
    db.create_all()
    os.makedirs(app.config["UPLOADS_FOLDER"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def _seed_db():
    """Populate the database with demo lectures, questions and two users
    (a student and a lecturer).  Called automatically on first startup
    so no shell command is needed. """

    student = User(
        name="Alex Johnson",
        email="student@college.edu",
        password_hash=generate_password_hash("student123"),
        role="student",
        student_id="STU-2024-001",
        phone="+1-555-0101",
        course="BSc Computer Science",
        semester="3",
        department="Computer Science",
        college="Faculty of Engineering",
        joined=date(2024, 9, 1),
    )

    lecturer = User(
        name="Dr. Sarah Williams",
        email="lecturer@college.edu",
        password_hash=generate_password_hash("lecturer123"),
        role="lecturer",
        joined=date(2023, 1, 15),
    )

    db.session.add_all([student, lecturer])
    db.session.commit()

    lectures_data = [
        {
            "title": "Introduction to AI",
            "video_url": "https://www.youtube.com/watch?v=ad79nYk2keg",
            "notes": (
                "Artificial Intelligence (AI) is the simulation of human intelligence by machines. "
                "AI systems can perform tasks like reasoning, learning, problem-solving, perception, and language understanding. "
                "AI is broadly divided into Narrow AI (designed for a specific task, like a chess engine) and General AI (hypothetical human-level intelligence). "
                "Key branches include Machine Learning, Natural Language Processing, Computer Vision, and Robotics. "
                "The Turing Test, proposed by Alan Turing in 1950, is a measure of machine intelligence. "
                "AI applications include virtual assistants, recommendation systems, fraud detection, and self-driving cars."
            ),
            "questions": [
                {
                    "text": "What does AI stand for?",
                    "option_a": "Automated Integration",
                    "option_b": "Artificial Intelligence",
                    "option_c": "Automated Intelligence",
                    "option_d": "Artificial Integration",
                    "correct_option": "B",
                    "explanation": "AI stands for Artificial Intelligence — the simulation of human intelligence by machines.",
                    "wrong_reasons": json.dumps({
                        "A": "Automated Integration is a software engineering term unrelated to AI.",
                        "C": "Automated Intelligence is not a recognised term in computer science.",
                        "D": "Artificial Integration has no meaning in the context of AI."
                    }),
                },
                {
                    "text": "Which of the following is an example of Narrow AI?",
                    "option_a": "A robot that can do any human job",
                    "option_b": "A chess-playing program",
                    "option_c": "A system with human-level general reasoning",
                    "option_d": "A biological brain",
                    "correct_option": "B",
                    "explanation": "A chess-playing program is Narrow AI because it is designed for one specific task.",
                    "wrong_reasons": json.dumps({
                        "A": "A robot that can do any human job describes General AI, which does not yet exist.",
                        "C": "Human-level general reasoning is the definition of General AI, not Narrow AI.",
                        "D": "A biological brain is not an AI system."
                    }),
                },
                {
                    "text": "Who proposed the Turing Test?",
                    "option_a": "John McCarthy",
                    "option_b": "Marvin Minsky",
                    "option_c": "Alan Turing",
                    "option_d": "Geoffrey Hinton",
                    "correct_option": "C",
                    "explanation": "Alan Turing proposed the Turing Test in 1950 as a measure of machine intelligence.",
                    "wrong_reasons": json.dumps({
                        "A": "John McCarthy coined the term 'Artificial Intelligence' but did not propose the Turing Test.",
                        "B": "Marvin Minsky was a pioneer in AI but is not associated with the Turing Test.",
                        "D": "Geoffrey Hinton is known for deep learning, not the Turing Test."
                    }),
                },
            ],
        },
        {
            "title": "Machine Learning",
            "video_url": "https://www.youtube.com/watch?v=ukzFI9rgwfU",
            "notes": (
                "Machine Learning (ML) is a subset of AI that enables systems to learn from data without being explicitly programmed. "
                "The three main types are: Supervised Learning (labelled data, e.g. spam detection), "
                "Unsupervised Learning (unlabelled data, e.g. customer clustering), and "
                "Reinforcement Learning (learning by reward and penalty, e.g. game-playing agents). "
                "Key concepts include features (input variables), labels (output variables), training set, test set, and model evaluation. "
                "Overfitting occurs when a model learns the training data too well and performs poorly on new data. "
                "Common algorithms include Linear Regression, Decision Trees, k-Nearest Neighbours, and Support Vector Machines."
            ),
            "questions": [
                {
                    "text": "Which type of ML uses labelled training data?",
                    "option_a": "Unsupervised Learning",
                    "option_b": "Reinforcement Learning",
                    "option_c": "Supervised Learning",
                    "option_d": "Transfer Learning",
                    "correct_option": "C",
                    "explanation": "Supervised Learning trains on labelled data where the correct output is already known.",
                    "wrong_reasons": json.dumps({
                        "A": "Unsupervised Learning works with unlabelled data — there are no predefined correct outputs.",
                        "B": "Reinforcement Learning learns through rewards and penalties, not labelled datasets.",
                        "D": "Transfer Learning reuses a pre-trained model; it is not defined by labelled data alone."
                    }),
                },
                {
                    "text": "What is overfitting in machine learning?",
                    "option_a": "When a model is too simple to learn patterns",
                    "option_b": "When a model learns training data too well and fails on new data",
                    "option_c": "When a model is trained on too little data",
                    "option_d": "When a model uses too many features",
                    "correct_option": "B",
                    "explanation": "Overfitting means the model memorises the training data and cannot generalise to unseen examples.",
                    "wrong_reasons": json.dumps({
                        "A": "A model that is too simple suffers from underfitting, not overfitting.",
                        "C": "Training on too little data can cause overfitting but is not the definition of it.",
                        "D": "Using many features can contribute to overfitting but is not the definition."
                    }),
                },
                {
                    "text": "Which algorithm is commonly used for classification and regression tasks?",
                    "option_a": "k-Means Clustering",
                    "option_b": "Principal Component Analysis",
                    "option_c": "Decision Tree",
                    "option_d": "DBSCAN",
                    "correct_option": "C",
                    "explanation": "Decision Trees can handle both classification and regression problems.",
                    "wrong_reasons": json.dumps({
                        "A": "k-Means is an unsupervised clustering algorithm, not used for labelled classification.",
                        "B": "PCA is a dimensionality reduction technique, not a classification or regression algorithm.",
                        "D": "DBSCAN is a density-based clustering algorithm used in unsupervised learning."
                    }),
                },
            ],
        },
        {
            "title": "Deep Learning",
            "video_url": "https://www.youtube.com/watch?v=6M5VXKLf4D4",
            "notes": (
                "Deep Learning is a subset of Machine Learning that uses multi-layered neural networks to learn representations from data. "
                "The word 'deep' refers to the many hidden layers in the network. "
                "Deep Learning excels at tasks like image recognition, speech recognition, and natural language processing. "
                "Key architectures include Convolutional Neural Networks (CNNs) for images, "
                "Recurrent Neural Networks (RNNs) for sequences, and Transformers for language. "
                "Training requires large datasets and significant computing power (GPUs). "
                "Backpropagation and gradient descent are used to update the network weights during training. "
                "Common activation functions are ReLU, Sigmoid, and Softmax."
            ),
            "questions": [
                {
                    "text": "What does 'deep' refer to in Deep Learning?",
                    "option_a": "The complexity of the data",
                    "option_b": "The number of hidden layers in the network",
                    "option_c": "The depth of the training dataset",
                    "option_d": "The difficulty of the problem being solved",
                    "correct_option": "B",
                    "explanation": "'Deep' refers to the many hidden layers stacked in a neural network.",
                    "wrong_reasons": json.dumps({
                        "A": "Data complexity is not what 'deep' describes in this context.",
                        "C": "Dataset depth is not a standard term; 'deep' refers to network architecture.",
                        "D": "Problem difficulty does not determine whether a model is called 'deep'."
                    }),
                },
                {
                    "text": "Which architecture is best suited for image recognition?",
                    "option_a": "Recurrent Neural Network (RNN)",
                    "option_b": "Transformer",
                    "option_c": "Convolutional Neural Network (CNN)",
                    "option_d": "Autoencoder",
                    "correct_option": "C",
                    "explanation": "CNNs use convolutional filters to detect spatial patterns, making them ideal for images.",
                    "wrong_reasons": json.dumps({
                        "A": "RNNs are designed for sequential data like text or time series, not images.",
                        "B": "Transformers are primarily used for language tasks, though vision transformers exist.",
                        "D": "Autoencoders are used for compression and anomaly detection, not primarily image classification."
                    }),
                },
                {
                    "text": "Which algorithm is used to update weights during deep learning training?",
                    "option_a": "k-Means",
                    "option_b": "Backpropagation with gradient descent",
                    "option_c": "Random Forest",
                    "option_d": "Naive Bayes",
                    "correct_option": "B",
                    "explanation": "Backpropagation computes gradients and gradient descent uses them to update network weights.",
                    "wrong_reasons": json.dumps({
                        "A": "k-Means is a clustering algorithm unrelated to neural network training.",
                        "C": "Random Forest is an ensemble ML method, not a neural network training algorithm.",
                        "D": "Naive Bayes is a probabilistic classifier, not a weight-update method."
                    }),
                },
            ],
        },
        {
            "title": "Neural Networks",
            "video_url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "notes": (
                "A Neural Network is a computational model inspired by the human brain. "
                "It consists of layers of interconnected nodes called neurons. "
                "The three main layer types are: Input Layer (receives raw data), "
                "Hidden Layers (learn intermediate representations), and Output Layer (produces the final prediction). "
                "Each connection has a weight that is adjusted during training. "
                "An activation function decides whether a neuron should fire. "
                "Common activation functions: Sigmoid (outputs 0-1), ReLU (outputs 0 or the input if positive), Softmax (outputs probabilities summing to 1). "
                "A perceptron is the simplest neural network with a single layer. "
                "Bias is an extra parameter added to each neuron to shift the activation function."
            ),
            "questions": [
                {
                    "text": "What is the role of the hidden layer in a neural network?",
                    "option_a": "To receive raw input data",
                    "option_b": "To produce the final output",
                    "option_c": "To learn intermediate representations of the data",
                    "option_d": "To store the training dataset",
                    "correct_option": "C",
                    "explanation": "Hidden layers transform the input through learned weights to extract useful features.",
                    "wrong_reasons": json.dumps({
                        "A": "Receiving raw input is the role of the Input Layer, not the hidden layer.",
                        "B": "Producing the final output is the role of the Output Layer.",
                        "D": "Neural networks do not store the training dataset inside their layers."
                    }),
                },
                {
                    "text": "Which activation function outputs values between 0 and 1?",
                    "option_a": "ReLU",
                    "option_b": "Softmax",
                    "option_c": "Sigmoid",
                    "option_d": "Tanh",
                    "correct_option": "C",
                    "explanation": "The Sigmoid function maps any input to a value between 0 and 1, useful for binary classification.",
                    "wrong_reasons": json.dumps({
                        "A": "ReLU outputs 0 for negative inputs and the raw value for positive inputs, not bounded to 1.",
                        "B": "Softmax outputs a probability distribution across multiple classes, not a single 0-1 value.",
                        "D": "Tanh outputs values between -1 and 1, not 0 and 1."
                    }),
                },
                {
                    "text": "What is a perceptron?",
                    "option_a": "A multi-layer deep neural network",
                    "option_b": "The simplest neural network with a single layer",
                    "option_c": "A type of activation function",
                    "option_d": "A method for reducing overfitting",
                    "correct_option": "B",
                    "explanation": "A perceptron is the simplest neural network, consisting of a single layer of weights.",
                    "wrong_reasons": json.dumps({
                        "A": "A multi-layer network is called a Multi-Layer Perceptron (MLP), not a perceptron.",
                        "C": "A perceptron is a network architecture, not an activation function.",
                        "D": "Techniques like dropout or regularisation reduce overfitting; a perceptron does not."
                    }),
                },
            ],
        },
    ]

    for lec_data in lectures_data:
        lecture = Lecture(
            title=lec_data["title"],
            notes=lec_data["notes"],
            video_url=lec_data["video_url"],
            lecturer_id=lecturer.id,
        )
        db.session.add(lecture)
        db.session.flush()

        for q in lec_data["questions"]:
            question = Question(
                lecture_id=lecture.id,
                text=q["text"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q["option_c"],
                option_d=q["option_d"],
                correct_option=q["correct_option"],
                explanation=q["explanation"],
                wrong_reasons=q["wrong_reasons"],
            )
            db.session.add(question)

    db.session.commit()
    print("Database seeded with demo data.")
    print("  Student : student@college.edu / student123")
    print("  Lecturer: lecturer@college.edu / lecturer123")


with app.app_context():
    if User.query.count() == 0:
        _seed_db()


# ── Auth helpers ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "student":
            flash("Students only.", "error")
            return redirect(url_for("lecturer_page"))
        return f(*args, **kwargs)
    return decorated


def lecturer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "lecturer":
            flash("Lecturers only.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated

# ── Auth routes ───────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["role"] = user.role
            session["name"] = user.name
            return redirect(url_for("lecturer_page") if user.role == "lecturer" else url_for("home"))
        flash("Incorrect email or password.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "student")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("register.html")
        user = User(
            name=name, email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Student: Home ─────────────────────────────────────────────────────────────

@app.route("/")
@student_required
def home():
    user = User.query.get(session["user_id"])
    lectures = Lecture.query.order_by(Lecture.created_at).all()
    watched_ids = {w.lecture_id for w in Watched.query.filter_by(student_id=user.id).all()}
    attempts = Attempt.query.filter_by(student_id=user.id).all()
    avg_score = 0
    if attempts:
        avg_score = round(sum(a.score / a.total * 100 for a in attempts if a.total) / len(attempts))
    selected_id = request.args.get("lecture_id", type=int)
    selected = Lecture.query.get(selected_id) if selected_id else (lectures[0] if lectures else None)

    return render_template("home.html", user=user, lectures=lectures,
                           watched_ids=watched_ids, selected=selected,
                           quizzes_taken=len(attempts), avg_score=avg_score)


@app.route("/watch/<int:lecture_id>", methods=["POST"])
@student_required
def mark_watched(lecture_id):
    uid = session["user_id"]
    if not Watched.query.filter_by(student_id=uid, lecture_id=lecture_id).first():
        db.session.add(Watched(student_id=uid, lecture_id=lecture_id))
        db.session.commit()
    return jsonify({"ok": True})


@app.route("/download_notes/<int:lecture_id>")
@student_required
def download_notes(lecture_id):
    lecture = Lecture.query.get_or_404(lecture_id)
    if not lecture.notes:
        flash("No notes available for this lecture.", "info")
        return redirect(url_for("home"))
    
    from flask import make_response
    response = make_response(lecture.notes)
    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = f'attachment; filename="{lecture.title.replace(" ", "_")}_notes.txt"'
    return response


# ── Student: Quiz ─────────────────────────────────────────────────────────────

@app.route("/quiz")
@student_required
def quiz():
    user = User.query.get(session["user_id"])
    lectures = Lecture.query.order_by(Lecture.created_at).all()
    attempts = Attempt.query.filter_by(student_id=user.id).order_by(Attempt.created_at.desc()).all()
    scores = [round(a.score / a.total * 100) if a.total else 0 for a in attempts]
    avg = round(sum(scores) / len(scores)) if scores else 0
    best = max(scores) if scores else 0
    last = scores[0] if scores else 0
    last4 = list(zip([a.created_at.strftime("%b %d") for a in attempts[:4]], scores[:4]))
    return render_template("quiz.html", user=user, lectures=lectures,
                           quizzes_taken=len(attempts), avg_score=avg,
                           best_score=best, last_score=last, last4=last4)


@app.route("/quiz/start", methods=["POST"])
@student_required
def quiz_start():
    lecture_ids = request.form.getlist("lecture_ids", type=int)
    count = int(request.form.get("count", 6))
    lectures = Lecture.query.all() if not lecture_ids else Lecture.query.filter(Lecture.id.in_(lecture_ids)).all()

    # Gather questions round-robin across topics
    pools = {}
    for lec in lectures:
        qs = Question.query.filter_by(lecture_id=lec.id).all()
        # Generate more if not enough
        if len(qs) < 3:
            try:
                from services.llm import generate_questions
                new_qs = generate_questions(lec.title, lec.notes, 10)
                for q in new_qs:
                    opts = q["options"]
                    wr = q.get("wrong_reasons", {})
                    db.session.add(Question(
                        lecture_id=lec.id,
                        text=q["question"],
                        option_a=opts[0], option_b=opts[1],
                        option_c=opts[2], option_d=opts[3],
                        correct_option=q["correct_option"],
                        explanation=q.get("explanation", ""),
                        wrong_reasons=json.dumps(wr)
                    ))
                db.session.commit()
                qs = Question.query.filter_by(lecture_id=lec.id).all()
            except Exception as e:
                flash(f"Could not generate questions for '{lec.title}': {e}", "error")
        pools[lec.id] = list(qs)

    # Round-robin pick
    selected = []
    i = 0
    lec_ids = list(pools.keys())
    while len(selected) < count and any(pools[lid] for lid in lec_ids):
        lid = lec_ids[i % len(lec_ids)]
        if pools[lid]:
            selected.append(pools[lid].pop(0))
        i += 1

    if not selected:
        flash("No questions available for the selected topics.", "error")
        return redirect(url_for("quiz"))

    session["quiz_questions"] = [q.id for q in selected]
    return render_template("quiz_run.html", questions=selected)


@app.route("/quiz/submit", methods=["POST"])
@student_required
def quiz_submit():
    uid = session["user_id"]
    q_ids = session.pop("quiz_questions", [])
    score = 0
    attempt = Attempt(student_id=uid, total=len(q_ids))
    db.session.add(attempt)
    db.session.flush()
    for qid in q_ids:
        chosen = request.form.get(f"q_{qid}", "")
        q = Question.query.get(qid)
        correct = q.correct_option == chosen
        if correct:
            score += 1
        db.session.add(AttemptAnswer(
            attempt_id=attempt.id, question_id=qid,
            chosen_option=chosen, is_correct=correct
        ))
    attempt.score = score
    db.session.commit()
    return redirect(url_for("results", attempt_id=attempt.id))

# ── Student: Results ──────────────────────────────────────────────────────────

@app.route("/results")
@student_required
def results_latest():
    uid = session["user_id"]
    attempt = Attempt.query.filter_by(student_id=uid).order_by(Attempt.created_at.desc()).first()
    if not attempt:
        flash("No quiz attempts yet.", "info")
        return redirect(url_for("quiz"))
    return redirect(url_for("results", attempt_id=attempt.id))


@app.route("/results/<int:attempt_id>")
@student_required
def results(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)
    if attempt.student_id != session["user_id"]:
        flash("Access denied.", "error")
        return redirect(url_for("home"))

    answers = AttemptAnswer.query.filter_by(attempt_id=attempt_id).all()
    wrong, right = [], []
    topic_stats = {}  # lecture_id -> {correct, total, title}

    for ans in answers:
        q = Question.query.get(ans.question_id)
        lec = Lecture.query.get(q.lecture_id)
        ts = topic_stats.setdefault(lec.id, {"title": lec.title, "correct": 0, "total": 0, "lecture": lec})
        ts["total"] += 1
        if ans.is_correct:
            ts["correct"] += 1
            right.append({"q": q, "ans": ans})
        else:
            wr = json.loads(q.wrong_reasons) if q.wrong_reasons else {}
            wrong.append({"q": q, "ans": ans, "why_wrong": wr.get(ans.chosen_option, ""), "lec": lec})

    # Topic mastery
    for ts in topic_stats.values():
        pct = round(ts["correct"] / ts["total"] * 100) if ts["total"] else 0
        ts["pct"] = pct
        ts["level"] = "Strong" if pct >= 80 else ("Average" if pct >= 50 else "Weak")

    sorted_topics = sorted(topic_stats.values(), key=lambda x: x["pct"])
    weakest = sorted_topics[0] if sorted_topics else None
    strongest = sorted_topics[-1] if sorted_topics else None

    # Recommended topics (weak or average)
    recommended = [t for t in sorted_topics if t["level"] in ("Weak", "Average")]

    pct_score = round(attempt.score / attempt.total * 100) if attempt.total else 0
    return render_template("results.html", attempt=attempt, wrong=wrong, right=right,
                           topic_stats=list(topic_stats.values()), weakest=weakest,
                           strongest=strongest, recommended=recommended,
                           pct_score=pct_score)

# ── Student: Explainer ────────────────────────────────────────────────────────

@app.route("/explainer/<int:question_id>/<chosen_option>")
@student_required
def explainer(question_id, chosen_option):
    try:
        chosen_option = chosen_option.upper()
        cached = Explainer.query.filter_by(question_id=question_id, chosen_option=chosen_option).first()
        if cached:
            return jsonify(json.loads(cached.slides_json))

        q = Question.query.get_or_404(question_id)
        lec = Lecture.query.get(q.lecture_id)
        opt_map = {"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d}
        chosen_text = opt_map.get(chosen_option, chosen_option)
        correct_text = opt_map.get(q.correct_option, q.correct_option)
        wrong_reasons = json.loads(q.wrong_reasons) if q.wrong_reasons else {}
        wrong_reason = wrong_reasons.get(chosen_option, "")

        def build_fallback_slides():
            note_sentences = [s.strip() for s in (lec.notes or "").split(".") if s.strip()]
            question_words = set(q.text.lower().split())
            scored = []
            for s in note_sentences:
                score = len(set(s.lower().split()) & question_words)
                if score > 0:
                    scored.append((score, s))
            scored.sort(reverse=True)
            relevant = ". ".join([s for _, s in scored[:2]]) if scored else (lec.notes[:200] + "..." if lec.notes else "No lecture notes available.")
            if relevant and not relevant.endswith("."):
                relevant += "."

            return [
                {"icon": "🤔", "title": "Where the mix-up happened",
                 "text": f'You chose Option {chosen_option}: "{chosen_text}". {wrong_reason or "This answer is not supported by the lecture notes."}'},
                {"icon": "💡", "title": "The idea",
                 "text": q.explanation or "The concept is explained in your lecture notes."},
                {"icon": "📝", "title": "From your lecture notes",
                 "text": relevant},
                {"icon": "✅", "title": "Remember",
                 "text": f"The correct answer is Option {q.correct_option}: \"{correct_text}\"."},
                {"icon": "🎯", "title": "Check yourself",
                 "text": f"Try taking another quiz on \"{lec.title}\" to practice this topic."}
            ]

        try:
            from services.llm import generate_explainer
            slides = generate_explainer(lec.title, lec.notes or "", q.text, chosen_text, correct_text)
            for s in slides:
                s.setdefault("icon", "💡")
                s.setdefault("title", "")
                s.setdefault("text", "")
        except Exception as e:
            print("Explainer Gemini error:", e)
            import traceback
            traceback.print_exc()
            slides = build_fallback_slides()

        db.session.add(Explainer(
            question_id=question_id,
            chosen_option=chosen_option,
            slides_json=json.dumps(slides)
        ))
        db.session.commit()
        return jsonify(slides)
    except HTTPException:
        raise
    except Exception as e:
        print("Explainer route error:", e)
        import traceback
        traceback.print_exc()
        # Ultimate fallback - return basic slides from DB without AI
        try:
            q = Question.query.get_or_404(question_id)
            lec = Lecture.query.get(q.lecture_id)
            opt_map = {"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d}
            chosen_text = opt_map.get(chosen_option.upper(), chosen_option)
            correct_text = opt_map.get(q.correct_option, q.correct_option)
            wrong_reasons = json.loads(q.wrong_reasons) if q.wrong_reasons else {}
            wrong_reason = wrong_reasons.get(chosen_option.upper(), "")
            slides = [
                {"icon": "🤔", "title": "Where the mix-up happened",
                 "text": f'You chose Option {chosen_option.upper()}: "{chosen_text}". {wrong_reason or "This answer is not supported by the lecture notes."}'},
                {"icon": "💡", "title": "The idea",
                 "text": q.explanation or "The concept is explained in your lecture notes."},
                {"icon": "📝", "title": "From your lecture notes",
                 "text": (lec.notes or "No lecture notes available.")[:300]},
                {"icon": "✅", "title": "Remember",
                 "text": f"The correct answer is Option {q.correct_option}: \"{correct_text}\"."},
                {"icon": "🎯", "title": "Check yourself",
                 "text": f"Try taking another quiz on \"{lec.title}\" to practice this topic."}
            ]
            return jsonify(slides)
        except HTTPException:
            raise
        except Exception as e2:
            print("Explainer ultimate fallback error:", e2)
            traceback.print_exc()
            return jsonify({"error": "Could not generate explainer"}), 500

# ── Student: Dashboard ────────────────────────────────────────────────────────

@app.route("/dashboard")
@student_required
def dashboard():
    user = User.query.get(session["user_id"])
    attempts = Attempt.query.filter_by(student_id=user.id).order_by(Attempt.created_at).all()
    watched_count = Watched.query.filter_by(student_id=user.id).count()
    scores = [round(a.score / a.total * 100) if a.total else 0 for a in attempts]
    avg = round(sum(scores) / len(scores)) if scores else 0

    # Topic mastery across all attempts
    topic_stats = {}
    for attempt in attempts:
        for ans in attempt.answers:
            q = Question.query.get(ans.question_id)
            lec = Lecture.query.get(q.lecture_id)
            ts = topic_stats.setdefault(lec.id, {"title": lec.title, "correct": 0, "total": 0, "lecture": lec})
            ts["total"] += 1
            if ans.is_correct:
                ts["correct"] += 1

    for ts in topic_stats.values():
        pct = round(ts["correct"] / ts["total"] * 100) if ts["total"] else 0
        ts["pct"] = pct
        ts["level"] = "Strong" if pct >= 80 else ("Average" if pct >= 50 else "Weak")

    sorted_topics = sorted(topic_stats.values(), key=lambda x: x["pct"])
    weakest = sorted_topics[0] if sorted_topics else None

    chart_labels = [a.created_at.strftime("%b %d") for a in attempts]
    return render_template("dashboard.html", user=user, attempts=attempts,
                           scores=scores, avg_score=avg, watched_count=watched_count,
                           topic_stats=list(topic_stats.values()), weakest=weakest,
                           chart_labels=chart_labels)

# ── Student: Profile ──────────────────────────────────────────────────────────

@app.route("/profile", methods=["GET", "POST"])
@student_required
def profile():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        user.name = request.form.get("name", user.name).strip()
        user.phone = request.form.get("phone", user.phone).strip()
        db.session.commit()
        session["name"] = user.name
        flash("Profile updated.", "success")
    attempts = Attempt.query.filter_by(student_id=user.id).all()
    scores = [round(a.score / a.total * 100) if a.total else 0 for a in attempts]
    avg = round(sum(scores) / len(scores)) if scores else 0
    watched_count = Watched.query.filter_by(student_id=user.id).count()
    return render_template("profile.html", user=user, quizzes_taken=len(attempts),
                           avg_score=avg, watched_count=watched_count)

# ── Lecturer page ─────────────────────────────────────────────────────────────

@app.route("/lecturer", methods=["GET", "POST"])
@lecturer_required
def lecturer_page():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        notes_text = request.form.get("notes_text", "").strip()
        video_url = request.form.get("video_url", "").strip()
        video_file_name = None

        # Handle notes file upload
        notes_file = request.files.get("notes_file")
        if notes_file and notes_file.filename:
            fname = secure_filename(notes_file.filename)
            fpath = os.path.join(app.config["UPLOADS_FOLDER"], fname)
            os.makedirs(app.config["UPLOADS_FOLDER"], exist_ok=True)
            notes_file.save(fpath)
            if fname.lower().endswith(".pdf"):
                from services.pdf_reader import extract_text
                notes_text = extract_text(fpath)
            else:
                notes_text = notes_file.read().decode("utf-8", errors="ignore") if not notes_text else notes_text

        # Handle video upload
        video_file = request.files.get("video_file")
        if video_file and video_file.filename:
            vname = secure_filename(video_file.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            video_file.save(os.path.join(app.config["UPLOAD_FOLDER"], vname))
            video_file_name = vname
            video_url = None

        lecture = Lecture(
            title=title, notes=notes_text,
            video_file=video_file_name, video_url=video_url or None,
            lecturer_id=user.id
        )
        db.session.add(lecture)
        db.session.flush()

        # Generate questions with Gemini
        try:
            from services.llm import generate_questions
            qs = generate_questions(title, notes_text, 10)
            for q in qs:
                opts = q["options"]
                db.session.add(Question(
                    lecture_id=lecture.id,
                    text=q["question"],
                    option_a=opts[0], option_b=opts[1],
                    option_c=opts[2], option_d=opts[3],
                    correct_option=q["correct_option"],
                    explanation=q.get("explanation", ""),
                    wrong_reasons=json.dumps(q.get("wrong_reasons", {}))
                ))
            flash(f"Lecture saved with {len(qs)} questions.", "success")
        except Exception as e:
            flash(f"Lecture saved, but question generation failed: {e}. Click 'Regenerate' later.", "warning")

        db.session.commit()
        return redirect(url_for("lecturer_page"))

    lectures = Lecture.query.filter_by(lecturer_id=user.id).order_by(Lecture.created_at.desc()).all()

    # Class performance: wrong-answer % per lecture
    performance = []
    for lec in Lecture.query.all():
        q_ids = [q.id for q in lec.questions]
        if not q_ids:
            continue
        total_ans = AttemptAnswer.query.filter(AttemptAnswer.question_id.in_(q_ids)).count()
        wrong_ans = AttemptAnswer.query.filter(
            AttemptAnswer.question_id.in_(q_ids),
            AttemptAnswer.is_correct == False
        ).count()
        pct = round(wrong_ans / total_ans * 100) if total_ans else 0
        performance.append({"title": lec.title, "pct": pct, "total": total_ans})
    performance.sort(key=lambda x: x["pct"], reverse=True)

    return render_template("lecturer.html", user=user, lectures=lectures, performance=performance)


@app.route("/lecturer/regenerate/<int:lecture_id>", methods=["POST"])
@lecturer_required
def regenerate_questions(lecture_id):
    lec = Lecture.query.get_or_404(lecture_id)
    try:
        from services.llm import generate_questions
        Question.query.filter_by(lecture_id=lec.id).delete()
        qs = generate_questions(lec.title, lec.notes, 10)
        for q in qs:
            opts = q["options"]
            db.session.add(Question(
                lecture_id=lec.id,
                text=q["question"],
                option_a=opts[0], option_b=opts[1],
                option_c=opts[2], option_d=opts[3],
                correct_option=q["correct_option"],
                explanation=q.get("explanation", ""),
                wrong_reasons=json.dumps(q.get("wrong_reasons", {}))
            ))
        db.session.commit()
        flash(f"Regenerated {len(qs)} questions for '{lec.title}'.", "success")
    except Exception as e:
        flash(f"Regeneration failed: {e}", "error")
    return redirect(url_for("lecturer_page"))


@app.route("/lecturer/delete/<int:lecture_id>", methods=["POST"])
@lecturer_required
def delete_lecture(lecture_id):
    lec = Lecture.query.get_or_404(lecture_id)
    q_ids = [q.id for q in lec.questions]
    AttemptAnswer.query.filter(AttemptAnswer.question_id.in_(q_ids)).delete(synchronize_session=False)
    Question.query.filter_by(lecture_id=lec.id).delete()
    Watched.query.filter_by(lecture_id=lec.id).delete()
    db.session.delete(lec)
    db.session.commit()
    flash("Lecture deleted.", "success")
    return redirect(url_for("lecturer_page"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(debug=False, host="0.0.0.0", port=port)
