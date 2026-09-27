# FitBuddy – AI Fitness Plan Generator (Gemini 3.1 Pro + Gemini 3 Flash)

FitBuddy generates personalized 7-day workout plans and nutrition/recovery
tips using Google's current Gemini models (3.1 Pro for plans, 3 Flash for
quick tips) via the current `google-genai` SDK, FastAPI for the backend,
and SQLite for storage.

## Project Structure
```
fitbuddy/
├── main.py                        # App entry point (uvicorn main:app --reload)
├── app/
│   ├── routes.py                  # All route handlers
│   ├── database.py                # SQLite/SQLAlchemy models + helpers
│   ├── schemas.py                 # UserInput, FeedbackRequest (Pydantic)
│   ├── gemini_generator.py        # generate_workout_gemini() - Gemini 3.1 Pro
│   ├── gemini_flash_generator.py  # generate_nutrition_tip_with_flash() - Gemini 3 Flash
│   └── updated_plan.py            # update_workout_plan() - feedback-based revision
├── templates/
│   ├── index.html                 # Input form
│   ├── result.html                # Plan + tip + feedback form
│   └── all_users.html             # Admin dashboard
├── static/
│   └── style.css
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Gemini API key**
   - Copy `.env.example` to `.env`
   - Get a free key from https://aistudio.google.com/apikey
   - Paste it into `.env` as `GOOGLE_API_KEY=...`

4. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open in browser**
   - App: http://127.0.0.1:8000
   - API docs: http://127.0.0.1:8000/docs

## On Replit

1. Import this zip into a new Repl.
2. Open the **Secrets** tool (padlock icon) and add:
   - Key: `GOOGLE_API_KEY`
   - Value: your Gemini API key (from https://aistudio.google.com/apikey)
3. Click **Run**. The app serves on the Replit-assigned port automatically.

## Routes

| Method | Route | Description |
|---|---|---|
| GET | `/` | Home page - user input form |
| POST | `/generate-workout` | Scenario 1 - generates + saves a 7-day plan and nutrition tip |
| POST | `/submit-feedback` | Scenario 2 - revises the stored plan using feedback |
| GET | `/view-all-users` | Admin dashboard - view all users and their plans |
| POST | `/delete-user/{user_id}` | Admin - delete a user and their plan |

## Notes
- `fitbuddy.db` (SQLite) is created automatically on first run.
- Uses the current `google-genai` SDK (`from google import genai`) - the
  older `google-generativeai` package is fully deprecated and its
  Gemini 1.5 / 2.5 model names are being retired for new API keys, which
  is why this version targets `gemini-3.1-pro-preview` and
  `gemini-3-flash-preview` instead.
- If `GOOGLE_API_KEY` is missing or invalid, plan/tip endpoints return a
  clear error instead of crashing.
- `user_id` is entered by the user on the form and used as the primary
  key, so a user can return later and submit feedback against the same ID.
