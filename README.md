# QuizFlow — Dynamic Quiz Website

A beginner-friendly quiz website built with Python, Flask, HTML, CSS and vanilla JavaScript. It includes topic/difficulty/count setup, a countdown timer, answer navigation, server-side scoring, answer explanations, a results dashboard, theme toggle, and session-based quiz history.

## Run locally on Windows

1. Install Python 3.10 or newer.
2. Open Command Prompt or PowerShell in this folder.
3. Create and activate a virtual environment (optional but recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. You can also skip activation and use `python -m pip` directly.
4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Start the app:

   ```powershell
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

## Add questions

Open `questions.json`. Add question objects under the topic key (`python`, `cpp`, `c`, `html`, `css`, `javascript`, `computer-systems`, `dsa`, or `general`). Every question needs a unique `id`, `difficulty` (`Easy`, `Medium`, or `Hard`), `question`, four `options`, `answer` matching one option exactly, and `explanation`.

The current sample bank is intentionally compact. Python has enough sample questions for a 10-question Python quiz; other individual topics have fewer examples and the app supplements those with questions from the same topic at other difficulty levels. For a genuinely varied 15- or 30-question quiz per topic, add more questions to that topic's JSON list. Mixed Topics draws from every topic.

## Project structure

- `app.py` — Flask routes, validation, server-side scoring, and session handling.
- `questions.json` — editable question bank.
- `templates/` — home/setup, quiz, results, history, and about pages.
- `static/css/style.css` — responsive white/purple themes and component styling.
- `static/js/script.js` — theme toggle and estimated duration.
- `static/js/quiz.js` — question navigation, answer saving, timer, and submit confirmation.
- `static/js/results.js` — answer-review filters.

## Notes

- The quiz answers are retained in Flask's signed session cookie during the quiz; correct-answer fields are only used by the server and are not sent to the quiz page.
- History is stored in the Flask session/browser cookie, not in a permanent database. It is suitable for a local learning project, not multi-user production use.
- Before deployment, set a strong random `FLASK_SECRET_KEY` and load it from an environment variable, disable debug mode, and consider a database for persistent history.
