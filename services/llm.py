import os
import json
import time
from google import genai
from google.genai import errors as genai_errors

# Read model name from environment (default: gemini-3.5-flash)
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
API_KEY = os.getenv("GEMINI_API_KEY", "")

# Fallback models tried in order if the primary model returns an error
_FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
]

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=API_KEY)
    return _client


def _is_retryable(e):
    """Check if an exception is a transient/retryable API error."""
    if isinstance(e, genai_errors.APIError):
        return e.code in (502, 503, 504, 429)
    return False


def _generate_with_retry(contents, config=None):
    """Call Gemini with retry logic and model fallbacks.

    Tries the primary model first, then falls back to alternative
    models. Retries up to 3 times per model for transient errors
    (503, 429, 502, 504).
    """
    client = _get_client()
    models_to_try = [MODEL] + [m for m in _FALLBACK_MODELS if m != MODEL]
    last_error = None
    for try_model in models_to_try:
        for attempt in range(3):
            try:
                kwargs = {"model": try_model, "contents": contents}
                if config:
                    kwargs["config"] = config
                response = client.models.generate_content(**kwargs)
                return response.text
            except Exception as e:
                last_error = e
                if attempt < 2 and _is_retryable(e):
                    time.sleep(2 ** attempt)
                    continue
                break
    raise last_error


def _call(prompt: str) -> str:
    """Send a prompt and return the raw JSON string."""
    return _generate_with_retry(prompt, config={"response_mime_type": "application/json"})


def generate_questions(title: str, notes: str, n: int = 10) -> list:
    """
    Ask Gemini to create n multiple-choice questions from the lecture notes.
    Returns a list of question dicts.
    """
    prompt = f"""
You are a quiz generator. Use ONLY the notes below. Do not invent facts. Beginner level.
Return ONLY a JSON array of exactly {n} objects. Each object must have:
  "question": string,
  "options": [optionA, optionB, optionC, optionD],
  "correct_option": one of "A","B","C","D",
  "explanation": why the correct answer is right,
  "wrong_reasons": object with keys only for the WRONG options, each value explaining why that option is wrong.

Topic: {title}
Notes:
{notes}
"""
    for attempt in range(2):
        try:
            raw = _call(prompt)
            data = json.loads(raw)
            if isinstance(data, list):
                validated = []
                for item in data:
                    if (
                        len(item.get("options", [])) == 4
                        and item.get("correct_option") in ("A", "B", "C", "D")
                    ):
                        validated.append(item)
                if validated:
                    return validated
        except Exception:
            if attempt == 1:
                raise ValueError("Gemini returned invalid question data after two attempts.")
    raise ValueError("Gemini returned invalid question data.")


def chat_with_studymate(message: str, history: list, lectures: list,
                        wrong_answers: list = None, weak_topics: list = None) -> str:
    """
    Conversational study assistant powered by Gemini.

    Args:
        message:       The student's latest message.
        history:       Last N turns [{"role": "user"|"assistant", "text": str}].
        lectures:      All lecture notes [{"title": str, "notes": str}].
        wrong_answers: Wrong answers from the student's last quiz attempt
                       [{"question", "chosen", "correct", "explanation", "topic"}].
        weak_topics:   Topic names where the student scores below 50%.

    Returns a plain-text reply string (no markdown symbols).
    """
    wrong_answers = wrong_answers or []
    weak_topics   = weak_topics   or []

    # ── Build lecture notes context ──
    if lectures:
        notes_context = "\n\n".join(
            f"=== {lec['title']} ===\n{lec['notes']}" for lec in lectures
        )
    else:
        notes_context = "No lecture notes have been uploaded yet."

    # ── Build quiz performance context ──
    quiz_context = ""
    if wrong_answers:
        lines = ["The student got these questions WRONG in their last quiz:"]
        for i, w in enumerate(wrong_answers, 1):
            lines.append(
                f"{i}. Question: {w.get('question','')} | "
                f"Student answered: {w.get('chosen','')} | "
                f"Correct answer: {w.get('correct','')} | "
                f"Explanation: {w.get('explanation','')}"
            )
        quiz_context += "\n".join(lines) + "\n"
    if weak_topics:
        quiz_context += f"\nThe student's WEAK topics (below 50% mastery): {', '.join(weak_topics)}\n"

    # ── Build conversation history ──
    history_text = ""
    for turn in history[-12:]:   # keep last 12 turns to stay within token limits
        role = "Student" if turn["role"] == "user" else "StudyMate AI"
        history_text += f"{role}: {turn['text']}\n"

    # ── Full prompt ──
    prompt = f"""
You are StudyMate AI, a warm and encouraging study assistant for university students.
Your only job is to help students understand their lecture material.

STRICT RULES:
1. Answer using ONLY the lecture notes provided. Do not invent facts.
2. If a question is clearly outside the notes, say: "That topic isn't in your uploaded notes. Please check your textbook or ask your lecturer."
3. Explain everything at beginner level — simple words, short sentences.
4. Be encouraging. Never make the student feel bad for not knowing something.
5. When giving examples, use everyday objects or simple numbers.
6. When giving practice questions, write the answer after a line that says "Answer:".
7. Do NOT use markdown symbols like **, ##, or bullet dashes. Use plain numbered lists or plain paragraphs.
8. Keep replies under 220 words unless the student explicitly asks for a detailed explanation or study plan.
9. If the student asks about a wrong answer, use the quiz context below to explain it clearly.
10. If the student asks what to study next, recommend their weakest topic first.

LECTURE NOTES:
{notes_context}

STUDENT QUIZ PERFORMANCE:
{quiz_context if quiz_context else "No quiz data available yet."}

CONVERSATION:
{history_text}Student: {message}
StudyMate AI:"""

    raw = _generate_with_retry(prompt)
    return raw.strip()


def generate_explainer(title: str, notes: str, question: str, chosen: str, correct: str) -> list:
    """
    Ask Gemini for 5 explainer slides for a wrong answer.
    Returns a list of 5 dicts: {icon, title, text}.
    """
    prompt = f"""
You are a friendly tutor. Use ONLY the notes below. Do not invent facts. Beginner level.
A student answered "{chosen}" but the correct answer is "{correct}".
Return ONLY a JSON array of exactly 5 slide objects. Each object must have:
  "icon": one emoji,
  "title": short slide title,
  "text": 2-3 sentence explanation (plain text, no markdown).

Slide order:
1. Where the mix-up happened (reference the student's wrong answer "{chosen}")
2. The idea explained simply
3. From your lecture notes (1-2 sentences from notes most relevant to the question)
4. Remember (the correct answer text)
5. Check yourself (a quick self-check question with the answer)

Topic: {title}
Question: {question}
Notes:
{notes}
"""
    for attempt in range(2):
        try:
            raw = _call(prompt)
            data = json.loads(raw)
            if isinstance(data, list) and len(data) == 5:
                return data
        except Exception:
            if attempt == 1:
                raise ValueError("Gemini returned invalid explainer data after two attempts.")
    raise ValueError("Gemini returned invalid explainer data.")