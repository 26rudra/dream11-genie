# Dream11 Genie 🏏

The Week 1 project for **Agentic AI for Developers**. A ReAct **agent** (LLM + tools + loop)
that reasons over live-style cricket data and returns a fantasy XI — a captain, a
vice-captain, and a one-line reason for every pick.

Built with **LangGraph** + **Groq** (free tier). Data is baked-in sample data
(`data.py`) so it runs offline and deterministically; the tools are structured so a real
sports API can drop in later without touching the agent.

## What it demonstrates (Week 1 skills)
- The agent loop and the **ReAct** pattern (reason → act → observe)
- **Native tool calling** — four tools the model decides when to use
- **Structured output** — a validated `Team` the UI can render
- **LangChain** `create_agent` as the spine (it runs on LangGraph underneath)

## Setup

```bash
# 1. from this folder, create a virtual env
python3 -m venv .venv && source .venv/bin/activate

# 2. install
pip install -r requirements.txt

# 3. add your FREE Groq key
cp .env.example .env
#   then edit .env and paste your key from https://console.groq.com/keys
```

## Run

```bash
# offline sanity check (no key needed) — tests tools + schema
python test_offline.py

# the agent (needs the Groq key)
python run.py                 # defaults to "CSK vs MI"
python run.py "CSK vs MI"     # a fixture with sample data
python run.py "CSK vs MI" -q  # hide the reasoning trace

# the web UI
streamlit run app.py
```

## Files
| File | Role |
|------|------|
| `data.py` | Baked-in sample squads, form notes & pitch report |
| `tools.py` | The four agent tools (the "hands") |
| `validate.py` | The hard rules in code — 11 players, role quotas, ≤100 credits, ≤7 per team, plus deterministic credit repair |
| `schema.py` | The `Team` / `Pick` structured-output schema |
| `agent.py` | The LangGraph ReAct agent + `pick_team()` |
| `run.py` | CLI runner (prints the XI + a trace) |
| `app.py` | Streamlit UI |
| `test_offline.py` | Offline tests for the tools/schema |

## Going live
Replace the bodies in `tools.py` with real API calls (keep the signatures). The agent,
schema and UI don't change.
