# Architecture Overview

## System Architecture

```
User Input
    │
    ▼
┌─────────────────┐
│  FastAPI REST   │  ← HTTP / JSON
│     API         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Goal Interpreter│  ← Parses user intent, detects domain & priority
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Planner      │  ← Generates ordered task list from templates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Decision Engine │  ← Rule-based strategy selection & outcome evaluation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Action Executor │  ← Pluggable tool registry (market data, simulation…)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Memory System   │  ← SQLAlchemy / SQLite persistence
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Learning Engine │  ← Analyses outcomes, suggests strategy adjustments
└─────────────────┘
```

## Module Descriptions

| Module | File | Responsibility |
|---|---|---|
| Goal Interpreter | `modules/goal_interpreter.py` | NLP-lite parsing of user goals |
| Planner | `modules/planner.py` | Domain-aware task template selection |
| Decision Engine | `modules/decision_engine.py` | Strategy ranking & outcome scoring |
| Action Executor | `modules/action_executor.py` | Tool registry + retry logic |
| Memory System | `modules/memory_system.py` | SQLite persistence via SQLAlchemy |
| Learning Engine | `modules/learning_engine.py` | Statistical learning & RL hook |

## Data Flow

```
POST /api/v1/goals/{id}/run
  → interpret_goal()
  → plan_tasks()
  → [Celery task queue]
      → for each task:
          decide_strategy()
          execute_action()
          memory.store(outcome)
          memory.record_metric()
```

## Database Schema

- `goals` – user goals with status & context
- `tasks` – planned tasks linked to goals
- `action_logs` – per-task tool execution logs
- `memory_entries` – outcome / insight records
- `performance_metrics` – time-series metric data points

## Future Extensions

- Replace rule-based decision engine with Q-learning or PPO
- Add real API integrations (yfinance, Alpha Vantage, Tavily)
- Add WebSocket live updates for the frontend
- Migrate from SQLite to PostgreSQL for production scale
