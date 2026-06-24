# 💰 PocketSage — AI-Powered Personal Finance Assistant for West Africa

> **Concierge Agent Track** — Kaggle AI Agents Intensive Vibe Coding Capstone 2026

[![Python](https://img.shields.io/badge/Python-3.14+-blue?logo=python)](https://python.org)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-orange?logo=google)](https://ai.google.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)
[![ADK](https://img.shields.io/badge/Google_ADK-Multi--Agent-red)](https://google.github.io/adk-docs/)
[![MCP](https://img.shields.io/badge/MCP-2_Servers-cyan)](https://modelcontextprotocol.io)

---

## 🌍 The Problem

Most personal finance apps were built for salaried workers in Western countries — people with fixed monthly incomes, linked bank accounts, and credit cards. **They completely ignore the economic reality of West Africa.**

In Benin and across West Africa, the financial reality looks like this:

- 💵 **Variable, irregular income** — from commerce, artisanship, farming, freelance work
- 📱 **Mobile Money first** — MTN Mobile Money, Moov Money are the primary financial tools
- 🤝 **High social expenses** — tontines, baptisms, funerals, ceremonies are non-negotiable
- 🏪 **Cash economy** — most transactions leave no digital trace
- 🗣️ **Multilingual households** — French, Fon, Yoruba coexist daily

**No existing app understands this.** PocketSage does.

---

## 💡 The Solution

PocketSage is a **multilingual AI concierge agent** that helps West African users manage their personal finances through natural conversation — in French, English, Fon, or Yoruba.

It learns your habits, anticipates difficult end-of-months, and acts **before** problems arise. Unlike reactive budgeting tools, PocketSage is **proactive**: it reasons, predicts, and guides.

### Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural conversation** | Record expenses by simply talking — no forms, no categories to pick |
| 🌐 **4 languages** | French, English, Fon (Benin), Yoruba (Nigeria/Benin) |
| 📱 **Mobile Money aware** | Understands MTN, Moov, cash, and bank transfers |
| 🤝 **Tontine tracking** | Built-in support for rotating savings groups |
| 📊 **Smart insights** | Culturally adapted analysis of your spending patterns |
| 🔔 **Proactive alerts** | Anticipates end-of-month difficulties before they happen |
| 🔒 **Privacy first** | All data stored locally — nothing leaves your device |
| 🎨 **Beautiful dashboard** | Real-time web interface with charts and transaction history |

---

## 🏗️ Architecture

PocketSage is built on a **multi-agent system** using Google ADK principles, with 4 specialized agents coordinated by a central Orchestrator.

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│         Web Dashboard (HTML/CSS/JS) + CLI               │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP
┌─────────────────────▼───────────────────────────────────┐
│                  FastAPI Server                          │
│              api.py — REST endpoints                     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              ORCHESTRATOR AGENT                          │
│   Detects intent • Routes messages • Manages language   │
└──────┬──────────────┬──────────────┬────────────────────┘
       │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌────▼───────┐
│ BUDGET      │ │ INSIGHT    │ │ ALERT      │
│ AGENT       │ │ AGENT      │ │ AGENT      │
│             │ │            │ │            │
│ • Records   │ │ • Analyzes │ │ • Projects │
│   expenses  │ │   patterns │ │   month-end│
│ • Records   │ │ • Detects  │ │ • Warns    │
│   income    │ │   anomalies│ │   early    │
│ • Summaries │ │ • Advises  │ │ • Suggests │
└──────┬──────┘ └─────┬──────┘ └────┬───────┘
       │              │              │
┌──────▼──────────────▼──────────────▼───────┐
│              MCP SERVERS                    │
│  currency_server    │    calendar_server    │
│  • Live FCFA rates  │  • Recurring events  │
│  • Multi-currency   │  • Cultural dates    │
│  • Conversion       │  • Tontine reminders │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│            LOCAL STORAGE (tools/)            │
│     JSON per user — fully private data       │
└─────────────────────────────────────────────┘
```

### Agent Roles

**Orchestrator Agent** — The brain. Receives every user message, detects language (FR/EN/Fon/Yo) and intent (budget/insight/alert/general), then routes to the appropriate sub-agent.

**Budget Agent** — Extracts transaction data from natural language. Understands "j'ai dépensé 2500 FCFA au marché" as well as "MTN na mì 15 000 FCFA". Confirms before saving.

**Insight Agent** — Analyzes spending patterns, detects anomalies, generates culturally adapted advice. Never judges social or ceremonial expenses.

**Alert Agent** — Projects end-of-month financial situation based on current spending rate. Issues color-coded alerts (🟢🟡🔴) with concrete action plans.

### MCP Servers

**currency_server** — Provides live FCFA exchange rates (EUR, USD, NGN, GHS) with automatic fallback. Enables multi-currency transaction recording.

**calendar_server** — Manages financial calendar events: recurring expenses (rent, utilities, tontines), cultural dates (Vodoun Festival, national holidays), and custom events.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Model** | Google Gemini 2.0 Flash (via Google AI Studio) |
| **Agent Framework** | Google ADK (multi-agent architecture) |
| **MCP Protocol** | Model Context Protocol (2 custom servers) |
| **Backend API** | FastAPI + Uvicorn |
| **Frontend** | Vanilla HTML/CSS/JS (no framework dependency) |
| **Storage** | Local JSON (privacy-first, no cloud) |
| **CLI** | Rich (beautiful terminal interface) |
| **Language** | Python 3.14+ |

---

## 📋 Prerequisites

- Python 3.10+
- Git
- A Google AI Studio API key (free tier works)
- Linux / macOS / Windows (WSL recommended)

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/pocketsage.git
cd pocketsage
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your Google AI Studio API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
APP_PORT=8000
DATA_DIR=./data
DEFAULT_LANG=fr
```

Get your free API key at: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 5. Run PocketSage

**Option A — Web Dashboard (recommended)**
```bash
python api.py
```
Then open http://localhost:8000 in your browser.

**Option B — CLI Interface**
```bash
python main.py
```

---

## 🎮 Usage

### Web Dashboard

The dashboard has 4 sections:

- **Dashboard** — Financial overview: income, expenses, balance, recent transactions
- **Assistant** — Chat interface to record transactions and get advice
- **Transactions** — Full transaction history with month filter
- **Alerts** — Current financial situation and end-of-month projection

### Chat Examples

Record a market expense:
```
J'ai dépensé 2 500 FCFA au marché ce matin
```

Record Mobile Money income:
```
MTN m'a crédité 45 000 FCFA pour la livraison
```

Get spending analysis:
```
Analyse mes dépenses de ce mois
```

Check end-of-month projection:
```
Est-ce que je vais tenir jusqu'à la fin du mois ?
```

In Fon:
```
Un sɔ́ 3000 FCFA dó azan jɛjɛ
```

In Yoruba:
```
Mo nà 5000 FCFA lóní owurọ̀
```

### REST API

```bash
# Health check
GET  /health

# Chat with agents
POST /chat
{
  "user_id": "user_demo",
  "message": "J'ai dépensé 2500 FCFA",
  "lang": "fr"
}

# Get financial summary
GET  /summary/{user_id}?month=2026-06

# Get transactions
GET  /transactions/{user_id}?month=2026-06&limit=50

# Get alerts
GET  /alerts/{user_id}?lang=fr

# Get insights
GET  /insight/{user_id}?month=2026-06&lang=fr

# Add transaction manually
POST /transaction
{
  "user_id": "user_demo",
  "type": "depense",
  "montant": 2500,
  "categorie": "alimentation",
  "description": "Marché du matin",
  "source": "cash"
}
```

---

## 🔒 Security & Privacy

PocketSage was designed with **privacy as a core principle**, not an afterthought:

- **Local storage only** — All user financial data is stored as JSON files on the user's own machine. No cloud, no external database.
- **No data sharing** — Transaction data never leaves the device. API keys are stored in `.env` and never committed to Git.
- **`.gitignore` protection** — `.env` and `data/*.json` are excluded from version control.
- **No authentication required** — The app runs locally; no account creation, no password storage.
- **CORS configured** — API only accepts requests from trusted origins.

---

## 📁 Project Structure

```
pocketsage/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py      # Central router — detects intent & language
│   ├── budget_agent.py      # Records transactions via conversation
│   ├── insight_agent.py     # Analyzes spending patterns
│   └── alert_agent.py       # Proactive financial alerts
├── mcp_servers/
│   ├── __init__.py
│   ├── currency_server.py   # MCP: Live FCFA exchange rates
│   └── calendar_server.py   # MCP: Financial calendar & cultural events
├── tools/
│   ├── __init__.py
│   └── storage.py           # Local JSON storage (privacy-first)
├── web/
│   ├── index.html           # Dashboard UI
│   ├── style.css            # Design system (West African colors)
│   └── app.js               # Frontend logic & API calls
├── data/                    # User data (gitignored)
├── tests/
│   └── test_agents.py       # Unit tests
├── api.py                   # FastAPI server
├── main.py                  # CLI interface
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Test a specific agent
python -m pytest tests/test_agents.py::test_budget_agent -v
```

---

## 🌐 Deployment

### Local (development)
```bash
python api.py
# Available at http://localhost:8000
```

### Production (Render.com — free tier)

1. Push your code to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repository
4. Set environment variables:
   - `GOOGLE_API_KEY` = your Gemini API key
   - `APP_PORT` = 10000
5. Build command: `pip install -r requirements.txt`
6. Start command: `python api.py`

### Production (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

---

## 🗺️ Roadmap

- [ ] **Voice input** — Speak transactions instead of typing (Gemini TTS)
- [ ] **MTN/Moov API integration** — Auto-import Mobile Money transactions
- [ ] **Group tontine management** — Multi-user tontine tracking
- [ ] **Offline mode** — Full PWA with service workers
- [ ] **SMS interface** — For users without smartphones
- [ ] **WhatsApp bot** — Meet users where they already are
- [ ] **Multi-country** — Expand to Côte d'Ivoire, Sénégal, Mali, Togo

---

## 🎯 Hackathon: Course Concepts Applied

This project demonstrates the following concepts from the **Kaggle AI Agents Intensive Course**:

| Concept | Implementation |
|---------|---------------|
| **Multi-Agent System (ADK)** | 4 specialized agents + Orchestrator routing |
| **MCP Servers** | `currency_server` + `calendar_server` |
| **Antigravity** | `models/antigravity-preview-05-2026` integrated for financial reasoning |
| **Security features** | Local storage, `.gitignore`, no API keys in code, CORS |
| **Deployability** | FastAPI + Render/Railway deployment ready |
| **Agent Skills** | Budget recording, insight analysis, proactive alerting |

---

## 👤 Author

Built with ❤️ for West Africa during the **Kaggle AI Agents Intensive Vibe Coding Capstone 2026**.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Google AI Studio & Gemini team for the powerful free-tier API
- Kaggle for organizing this capstone
- The West African developer community for the inspiration
- All the market vendors, mobile money agents, and tontine organizers whose financial lives inspired this project