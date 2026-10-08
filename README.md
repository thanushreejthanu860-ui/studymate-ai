# StudyMate AI - AI-Powered Lecture Notes, Quiz & Learning Assistant

StudyMate AI is a full-stack web application that lets lecturers upload lecture videos and notes, automatically generates topic-based multiple-choice quizzes with AI, and gives students an interactive learning experience. Students can take quizzes, review their wrong answers, get AI-powered step-by-step explanations on mistakes, view a personalised dashboard of their topic mastery, and revise with generated practice questions.

## Tech Stack

- **Flask** — web framework and REST API
- **SQLite** (via Flask-SQLAlchemy) — database for users, lectures, questions, and quiz attempts
- **Gemini API** — AI-generated quiz questions, wrong-answer explanations, and tutoring content
- **Hugging Face** — embeddings / NLP utilities
- **Browser speech** — Web Speech API for text-to-speech and speech-to-text support

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS / Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:
   ```
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   GEMINI_MODEL=gemini-3.5-flash
   ```

4. Seed the database with demo data:
   ```bash
   python seed.py
   ```

5. Start the development server:
   ```bash
   python app.py
   ```

Visit `http://127.0.0.1:5000` in your browser.

## Demo Logins

| Role      | Email                  | Password     |
|-----------|------------------------|--------------|
| Student   | `student@college.edu`  | `student123` |
| Lecturer  | `lecturer@college.edu` | `lecturer123`|
