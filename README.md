# Cortex Agent

A **production-style personal autonomous AI decision agent** built with FastAPI, React, SQLite, Celery, and Docker.

> The agent accepts user goals, breaks them into tasks, plans actions, executes them, and learns from outcomes — simulating a *digital brain* architecture.

---

## 📐 Architecture

```
User Goal → Goal Interpreter → Planner → Decision Engine
         → Action Executor → Memory System → Learning Engine
```

See [`docs/architecture.md`](docs/architecture.md) for the full design.

---

## 🗂 Folder Structure

```
cortex-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models/              # ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── modules/
│   │   │   ├── goal_interpreter.py
│   │   │   ├── planner.py
│   │   │   ├── decision_engine.py
│   │   │   ├── action_executor.py
│   │   │   ├── memory_system.py
│   │   │   └── learning_engine.py
│   │   ├── api/
│   │   │   ├── goals.py
│   │   │   ├── tasks.py
│   │   │   ├── memory.py
│   │   │   └── analytics.py
│   │   └── tasks/
│   │       └── celery_tasks.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # GoalInput, TaskMonitor, MemoryLogs, …
│   │   ├── pages/               # Dashboard
│   │   └── api/                 # Axios client
│   ├── package.json
│   └── Dockerfile
├── tests/                       # pytest test suite
├── docs/
│   └── architecture.md
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start with Docker Compose

### Prerequisites
- Docker ≥ 24
- Docker Compose v2

```bash
# 1. Clone the repository
git clone https://github.com/saiveerateja2000/Cortex-agent.git
cd Cortex-agent

# 2. Copy environment example
cp backend/.env.example backend/.env

# 3. Build and start all services
docker compose up --build

# Services:
#   Frontend  → http://localhost:80
#   Backend   → http://localhost:8000
#   API docs  → http://localhost:8000/docs
#   Redis     → localhost:6379
```

---

## 🔧 Local Development (without Docker)

### Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env if needed (SQLite is the default — no setup required)

uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for interactive Swagger UI.

### Celery Worker (optional — requires Redis)

```bash
cd backend
celery -A app.tasks.celery_tasks.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

---

## 🧪 Running Tests

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
cd ..
pytest tests/ -v
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/goals/` | Create a new goal |
| `POST` | `/api/v1/goals/{id}/run` | Run the full agent pipeline |
| `GET`  | `/api/v1/goals/` | List all goals |
| `GET`  | `/api/v1/goals/{id}` | Get a single goal |
| `PATCH`| `/api/v1/goals/{id}` | Update a goal |
| `DELETE`| `/api/v1/goals/{id}` | Delete a goal |
| `GET`  | `/api/v1/tasks/` | List tasks (filter by `goal_id`) |
| `GET`  | `/api/v1/tasks/goal/{goal_id}` | Tasks for a goal |
| `GET`  | `/api/v1/tasks/{id}/actions` | Action logs for a task |
| `GET`  | `/api/v1/memory/` | List memory entries |
| `POST` | `/api/v1/memory/` | Create a memory entry |
| `GET`  | `/api/v1/analytics/summary` | Dashboard summary |
| `GET`  | `/api/v1/analytics/metrics` | Performance metrics |
| `GET`  | `/api/v1/analytics/learning` | Learning insights |
| `GET`  | `/health` | Health check |

---

## 💡 Example Use Case

**User enters goal:**
> *"Invest 1000 units in a simulated stock trading strategy."*

**Agent workflow:**

1. **Goal Interpreter** detects `domain=finance`, `priority=5`, `amount=1000 units`
2. **Planner** generates 5 tasks: *fetch data → analyse → simulate → evaluate → store*
3. **Decision Engine** selects strategies: `yfinance_api`, `statistical_analysis`, `monte_carlo`…
4. **Action Executor** runs each tool, retrying on failure
5. **Memory System** persists outcomes & metrics to SQLite
6. **Learning Engine** scores tool performance and suggests adjustments

**Results visible in the React dashboard:** task status, P&L from simulation, memory log, analytics charts.

---

## 🐳 Docker Services

| Service | Image | Port |
|---------|-------|------|
| `backend` | Python 3.11 + FastAPI | 8000 |
| `frontend` | Node 20 + nginx | 80 |
| `redis` | redis:7-alpine | 6379 |
| `celery_worker` | Python 3.11 + Celery | — |

---

## 🔮 Roadmap

- [ ] Real market data integration (yfinance / Alpha Vantage)
- [ ] Reinforcement learning decision engine (Q-learning / PPO)
- [ ] WebSocket live task updates
- [ ] PostgreSQL migration for production scale
- [ ] User authentication (JWT)
- [ ] Goal scheduling (cron-based)

---

## 📄 License

MIT