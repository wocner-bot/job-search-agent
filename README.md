# Job Search Agent

React + FastAPI web app for turning a CV and vacancy queue into ready-to-send job application materials.

## MVP

- paste or upload a CV
- import the current tailored CV workbook package
- score and prioritize vacancies
- generate ready-to-send notes, DMs, and email cover letters
- manually track statuses
- export a ZIP package

The app does not submit applications automatically. Only the user can mark an application as sent.

## Local Development

Backend:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Render

Use `render.yaml` as a Blueprint. Configure these environment variables if not supplied by the Blueprint:

- `DATABASE_URL`
- `STORAGE_DIR`
- `CORS_ORIGINS`
- `APP_ENV`
- `OPENAI_API_KEY` for optional LLM-assisted generation
