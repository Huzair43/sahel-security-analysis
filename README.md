# Sahel Security Analysis

An open-source intelligence platform analyzing armed conflict dynamics and their economic consequences in Burkina Faso, Mali, and Niger, built on ACLED data, Bayesian modeling, and a RAG-powered AI analyst.

**Live demo:** [sahel-security-analysis.onrender.com](https://sahel-security-analysis.onrender.com/)

---

## What it does

- Visualizes 23,000+ conflict incidents on an interactive WebGL map with real-time client-side filtering
- Tracks monthly trends, detects anomalies (Z-score), and projects a 6-month forecast via linear regression
- Identifies geographic hotspots and most active armed groups
- Quantifies the conflict-inflation relationship through a Bayesian hierarchical model (PyMC, ArviZ)
- Exposes an AI analyst powered by a RAG pipeline: questions answered from the ACLED dataset, no hallucination

---

## Versions

| Branch | Stack | Status |
|---|---|---|
| `main` | Flask, Plotly WebGL, RAG chatbot, Render | Live |
| `streamlit` | Streamlit, Folium | Preserved |

The project was originally built with Streamlit. It was migrated to Flask to support a production deployment with a RAG chatbot, WebGL map performance at 23k points, and full control over the frontend design.

---

## Architecture

```
flask_app/
├── routes/          # Page blueprints (overview, map, trends, hotspots, bayesian, about)
├── api/             # JSON endpoints (map points, chart data, chat)
├── chat/
│   ├── rag.py             # Intent detection + Pandas retrieval + prompt builder
│   ├── backend_local.py   # Gemma via Ollama (local Docker)
│   └── backend_groq.py    # Llama 3.1 via Groq API (production)
├── utils/
│   └── data_loader.py     # lru_cache data loading
└── templates/       # Jinja2 templates extending base.html
```

---

## RAG chatbot

The AI analyst uses a two-stage pipeline:

1. **Retrieval:** intent detection extracts countries, years, and event types from the question, then queries the ACLED DataFrame with Pandas to build structured context (incident counts, fatalities, top actors, yearly trend).
2. **Generation:** the context is injected into a system prompt sent to the LLM. The model answers strictly from the retrieved data.

**Local setup:** Gemma via Ollama, containerized with Docker Compose.
**Production:** switched to Groq API (Llama 3.1 8B) after identifying that Ollama containers require 8GB+ RAM, exceeding free-tier cloud limits.

---

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Flask 3, Gunicorn, flask-compress |
| Data | Pandas, NumPy |
| Visualization | Plotly (WebGL, 23k points without lag) |
| Bayesian model | PyMC 5, ArviZ |
| AI / RAG | Groq API (prod), Ollama + Gemma (local) |
| Deployment | Render, Docker Compose |
| Data source | ACLED API (OAuth2), IMF DataMapper API |

---

## Quickstart

### Flask app (local)

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # fill GROQ_API_KEY or set CHAT_BACKEND=local
python run.py
```

App available at `http://localhost:5000`.

### With local AI (Gemma via Ollama)

```bash
# Install Ollama: https://ollama.com/download
ollama pull gemma4:latest
```

Set in `.env`:

```
CHAT_BACKEND=local
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma4:latest
```

Then run `python run.py`.

### Full Docker setup (Flask + Ollama)

```bash
docker-compose up --build
```

Ollama pulls the model on first start. Flask waits for it before serving.

---

## Bayesian model

We fit a Bayesian hierarchical linear regression to test whether conflict intensity (ACLED) predicts national inflation (IMF):

```
inflation(t) = α_country + β x conflict_z(t-1) + ε

Priors:
  α_country ~ Normal(μ_α, σ_α)   # country-specific intercept
  β         ~ Normal(0, 2)        # shared conflict effect
  σ         ~ HalfNormal(5)
```

**Result:** β = -0.416, 94% HDI [-2.302, +1.399]. The HDI includes zero: no credible causal effect can be established at the country-year aggregation level. This null result is methodologically expected given N=12 and the mismatch between local conflict dynamics and national CPI.

Sampled with NUTS, 4 chains x 4,000 draws, all R-hat = 1.0.

---

## Data

| Source | Coverage | Access |
|---|---|---|
| ACLED | 23,156 incidents, Jan 2020 to Mar 2025 | OAuth2 API |
| IMF DataMapper | Annual CPI, 2018 to 2024 | Public API |

---

## Project structure

```
sahel-security-analysis/
├── flask_app/          # Flask application
├── app/                # Streamlit version (branch: streamlit)
├── data/processed/     # Preprocessed CSV files (tracked in git)
├── notebooks/          # Analysis notebooks (EDA, Bayesian model)
├── src/                # ACLED data pipeline
├── docker-compose.yml  # Local Docker setup (Flask + Ollama)
├── Dockerfile
├── render.yaml         # Render deployment config
├── run.py
└── requirements.txt
```

---

## Author

Ousaïrou Bagagnan, Data Science Student
