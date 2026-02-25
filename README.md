# AI Study Planner

Web app where users add study goals and available weekly time, then generate a weekly study plan.

## Stack

- FastAPI backend
- React (Vite) frontend
- SQLite database

## Project Structure

- `backend/` API + planner + SQLite models
- `frontend/` React UI

## Run Locally

### 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# optional: cp .env.example .env
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`.

### 2) Frontend

```bash
cd frontend
npm install
# optional: cp .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173`.

If needed, override API URL:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

## Main Endpoints

- `POST /goals` add a goal
- `GET /goals` list goals
- `POST /plans/generate` generate and persist weekly plan
- `GET /health` health check

## Publish To GitHub

1) Initialize and commit:

```bash
cd /Users/srinumarapureddi/Desktop/New\ Codex\ Project
git add .
git commit -m "Initial AI Study Planner app"
```

2) Create a new empty GitHub repo, then connect and push:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Run From Git (Fresh Machine)

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend (new terminal):

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open:
- Frontend: `http://localhost:5173`
- Backend docs: `http://127.0.0.1:8000/docs`
