"""
Build context for StudyMate AI chatbot from database.
"""

from models import db, User, Lecture, Question, Attempt, AttemptAnswer, Watched


def build_context(user_id, lecture_id=None):
    """Return a context text block for the chatbot, under ~12000 chars."""
    user = User.query.get(user_id)
    if not user:
        return "No user found."

    parts = []

    # ---- a) All lectures: title + notes (trim to ~1500 chars each) ----
    lectures = Lecture.query.order_by(Lecture.created_at).all()
    if lectures:
        parts.append("=== LECTURES ===")
        for lec in lectures:
            notes = (lec.notes or "").strip()
            if len(notes) > 1500:
                notes = notes[:1500] + "..."
            current_marker = " (CURRENT LECTURE)" if lecture_id and lec.id == lecture_id else ""
            parts.append(f"\n--- {lec.title}{current_marker} ---\n{notes or '(no notes)'}")

    # ---- b) Topic mastery across all attempts ----
    attempts = Attempt.query.filter_by(student_id=user_id).all()
    if attempts:
        topic_stats = {}
        for attempt in attempts:
            for ans in attempt.answers:
                q = Question.query.get(ans.question_id)
                if not q:
                    continue
                lec = Lecture.query.get(q.lecture_id)
                if not lec:
                    continue
                ts = topic_stats.setdefault(lec.id, {"title": lec.title, "correct": 0, "total": 0})
                ts["total"] += 1
                if ans.is_correct:
                    ts["correct"] += 1

        parts.append("\n=== TOPIC MASTERY ===")
        for ts in topic_stats.values():
            pct = round(ts["correct"] / ts["total"] * 100) if ts["total"] else 0
            level = "Strong" if pct >= 80 else ("Average" if pct >= 50 else "Weak")
            parts.append(f"- {ts['title']}: {ts['correct']}/{ts['total']} ({pct}%) — {level}")

    # ---- c) Wrong answers from last 3 attempts ----
    recent_attempts = Attempt.query.filter_by(student_id=user_id).order_by(Attempt.created_at.desc()).limit(3).all()
    if recent_attempts:
        parts.append("\n=== RECENT WRONG ANSWERS (last 3 attempts) ===")
        for attempt in recent_attempts:
            for ans in attempt.answers:
                if ans.is_correct:
                    continue
                q = Question.query.get(ans.question_id)
                if not q:
                    continue
                lec = Lecture.query.get(q.lecture_id)
                opt_map = {"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d}
                chosen_text = opt_map.get(ans.chosen_option, ans.chosen_option)
                correct_text = opt_map.get(q.correct_option, q.correct_option)
                wrong_reasons = {}
                if q.wrong_reasons:
                    import json
                    try:
                        wrong_reasons = json.loads(q.wrong_reasons)
                    except:
                        pass
                wrong_reason = wrong_reasons.get(ans.chosen_option, "")
                parts.append(
                    f"\nTopic: {lec.title if lec else 'Unknown'}\n"
                    f"Question: {q.text}\n"
                    f"Student chose: {ans.chosen_option} — {chosen_text}\n"
                    f"Correct: {q.correct_option} — {correct_text}\n"
                    f"Explanation: {q.explanation or '(none)'}\n"
                    f"Why wrong: {wrong_reason or '(none)'}"
                )

    # ---- d) Current lecture (if given) ----
    if lecture_id:
        lec = Lecture.query.get(lecture_id)
        if lec:
            notes = (lec.notes or "").strip()
            if len(notes) > 3000:
                notes = notes[:3000] + "..."
            parts.append(f"\n=== CURRENT LECTURE DETAILS ===\n{lec.title}\n{notes or '(no notes)'}")

    # Join and trim to ~12000 chars
    context = "\n".join(parts)
    if len(context) > 12000:
        context = context[:12000] + "\n... (trimmed)"
    return context