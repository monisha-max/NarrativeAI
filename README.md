# NarrativeAI

**The AI-Native News Intelligence Platform**

Problem Statement #8 

Business news in 2026 is delivered the same way it was in 2005: static text articles, a one-size-fits-all homepage, and the same format for everyone. NarrativeAI replaces scattered articles with living intelligence dossiers that remember what you know, show what you don't, predict what comes next, and argue against your own biases.

---

## Table of Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Core Features](#core-features)
- [Additional Intelligence Tools](#additional-intelligence-tools)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Demo Data](#demo-data)
- [Setup Instructions](#setup-instructions)
- [Project Structure](#project-structure)
- [Evaluation Alignment](#evaluation-alignment)

---

## The Problem

If you want to understand the Byju's crisis right now, The Economic Times offers 47 separate articles spanning 3 years. Each article assumes you just arrived. No connections between events. No memory of what you already know. No predictions about what comes next. When a story goes quiet, products stop showing it. When one story affects another, nobody connects them.

NarrativeAI fixes all of this.

---

## The Solution

Every major business story becomes a single **Living Dossier** — a persistent, evolving intelligence document that replaces the article as the unit of news consumption. One dossier. Complete understanding.

---

## Demo Video

[![NarrativeAI Demo](https://img.shields.io/badge/Watch%20Demo-Google%20Drive-blue)](https://drive.google.com/file/d/11pM2jtCoZwewoZgDqfPQoxwJ0eIDDCwD/view?usp=sharing)

[Watch the 3-minute demo video](https://drive.google.com/file/d/11pM2jtCoZwewoZgDqfPQoxwJ0eIDDCwD/view?usp=sharing)

## Core Features

### Living Dossier
Every story is one evolving document, not 47 scattered articles. Interactive D3.js timeline with colour-coded events (corporate, regulatory, financial, management, market, legal). Zoom, filter, click any event for detail. 43 real events for the Byju's dossier alone.

### Story DNA — Archetype Detection
Every business story follows a pattern. The system fingerprints stories against 5 archetype patterns (Corporate Governance Collapse, Short Attack Playbook, Regulatory Escalation, Founder vs Board, M&A Saga) and tells you exactly which phase you're in with confidence scores and historical parallels. "You are in Phase 3 of a Corporate Governance Collapse. In 80% of similar cases, Phase 4 followed within 60-90 days."

### Fog of War
A visual overlay on the timeline showing where information is thin. Red-tinted areas have limited sources and unverified claims. Clear areas have multiple independent sources. You literally see what you don't know. No news product in the world does this.

### Silence Detection
When a story goes abnormally quiet, the system flags it. "The audit story has been silent for 42 days. In 73% of similar cases, this kind of silence preceded a major disclosure." The system watches for what ISN'T happening.

### Delta Engine — Persistent Narrative Memory
Every visit is a continuation, not a new session. The system remembers what you've read and shows only what changed since your last visit, ranked by significance. Tracks sentiment shifts, new entities, and predictions tested.

### 60-Second Mode
One tap. Three things across all your followed stories: most important change, biggest risk, one actionable insight. The AI makes the judgment call about what matters most.

### Contrarian Detector
Every story shows both sides: consensus view vs the strongest credible dissent. Side-by-side evidence comparison with confidence scores. Plus a list of questions neither side has answered.

### "What If I'm Wrong?"
The system figures out what you believe, then builds the absolute strongest case against your own position. Evidence you may be overlooking, historical cases where similar views were wrong, and the one question you should be asking yourself. No news product has ever built this.

### Perspective Dial
5 sliders you control: Conservative/Aggressive, Bull/Bear, Investor/Founder/Employee/Regulator, India-First/Global, Quick Take/Deep Evidence. Same facts, different analytical frame. The content visibly transforms when you switch perspectives.

### Personalised Cognition
6 user types: Student, Retail Investor, Founder, CFO, Journalist, Policy Maker. The explanation layer adapts; a student gets jargon expanded with analogies, a CFO gets margin analysis and balance sheet implications. Same facts, different explanation depth.

### Briefing Room
9 guided intelligence prompts: Explain the story, What changed today, Who is exposed, Give me opposing takes, Explain like I'm 19, What if I'm wrong, Relevant to my portfolio, What's the story's DNA, 60-second version. Streaming AI responses via Claude. Plus free-form questions.

### Claims vs Facts
Tracks every claim in a story against its outcome. Confirmed (green), Invalidated (red), Unverified (amber). With source attribution and dates. Epistemic accountability.

### Cross-Story Ripple Detection
When a development in one dossier affects another, the system detects it automatically through shared entities, sector linkage, regulatory chains, and financial connections. "An RBI rate decision just changed the debt servicing assumptions for Byju's restructuring."

### Entity Relationship Graph (Money Map)
D3.js force-directed graph showing all players: companies, people, regulators, investors. Colour-coded by type. Connection lines show relationships (ownership, regulatory, legal, financial, employment). Interactive: drag, zoom, click for detail.

### Consequence Engine
For any development: who gains, who loses. First-order and second-order effects. Three scenarios (best/base/worst) with probability and triggers.

### Vernacular Translation
8 Indian languages: Hindi, Telugu, Tamil, Bengali, Marathi, Kannada, Gujarati, Malayalam. Culturally adapted, not literally translated. Jargon explained in the local context. A Hindi-speaking student gets a different complexity than a Hindi-speaking CFO.

---

## Additional Intelligence Tools

Six features that no Indian news platform currently offers:

### AI Chat Assistant
WhatsApp-style conversational news assistant. Ask anything about Indian markets in natural language. 7 quick commands (/market, /sectors, /earnings, /ipo, /rbi, /budget, /global). Streaming responses are adapted to the user type.

### Bull vs Bear Debate Arena
Enter any market topic. Two AI analysts debate in 3 rounds. Bull argues the growth case with data. Bear counters with risks and precedent. A neutral judge evaluates evidence quality and delivers a verdict with the strongest and weakest arguments.

### Smart Earnings Decoder
Select any company and get AI-decoded quarterly results instantly. Visual segment breakdown with growth bars. Analysis adapts to who you are: a student gets jargon explained, a CFO gets margin and valuation analysis. Head-to-head company comparison.

### Rumour vs Reality Tracker
Tracks market rumours from the moment they surface to their final outcome. Status tracking: Confirmed, Debunked, Partially True, Unresolved. Accuracy scores and market impact logged. Paste any rumour for AI credibility analysis with a verification checklist.

### Portfolio Impact Simulator
Select a portfolio with real Indian stocks. Type any hypothetical event ("RBI cuts 50 bps", "crude hits $120"). AI analyses stock-by-stock impact on your specific holdings. Estimated value change in rupees. Immediate action recommendations (hold, buy more, reduce, hedge).

### Market Pulse Live
Real-time market dashboard: 4 major indices, top gainers and losers with volume, FII/DII money flow direction. 8-sector heatmap where green = up, red = down. Click any sector for an AI deep-dive analysis. AI-generated market commentary.

---

## Architecture

![NarrativeAI_Pitch pptx](https://github.com/user-attachments/assets/4434d100-eb93-44ea-a261-81b2a103049b)

### 7-Agent Pipeline

The system is built on a multi-agent architecture with real orchestration — not API wrappers pretending to be agents. The Orchestrator manages a two-phase pipeline:

**Phase 1 — Sequential:**
1. **Ingestion Agent**: Scrapes ET articles and Google News RSS feeds. Deduplicates, scores relevance, and stores in PostgreSQL and Elasticsearch.
2. **Entity Agent**: Runs spaCy NER with custom Indian business entity patterns (RBI, SEBI, NCLT, BSE/NSE codes). Uses Claude for entity classification. Builds co-occurrence relationship graphs.

**Phase 2 — Parallel (asyncio.gather):**
Results from Phase 1 are passed as context to four agents running simultaneously:
3. **Synthesis Agent**: Constructs timelines, computes multi-dimensional sentiment (4 axes), calculates Fog of War information density, tracks claims vs facts, and generates consequence maps.
4. **Archetype Agent**: Fingerprints story against 5 archetype patterns. Identifies current phase. Generates phase predictions with confidence scores. Detects silence anomalies against archetype-specific baselines.
5. **Contrarian Agent**: Mines counter-narratives from the corpus. Scores credibility. Builds consensus vs dissent comparison. Constructs "What If I'm Wrong" arguments against the user's inferred position.
6. **Ripple Agent**: Evaluates cross-story impact across all active dossiers via entity overlap, sector linkage, regulatory chains, and financial connections. Generates ripple alerts with magnitude scoring.

### 9 Backend Services

| Service | Purpose |
|---------|---------|
| Claude API | Anthropic SDK with async streaming, JSON mode, rate limiting |
| NLP Service | spaCy with custom Indian business entity ruler |
| Sentiment | 4-dimension scoring: market confidence, regulatory heat, media tone, stakeholder sentiment |
| Fog Engine | Information density calculation from source count, diversity, official sources, conflicting reports |
| Silence Detector | Baseline cadence calculation, anomaly detection, archetype-aware severity scoring |
| Delta Engine | Persistent session memory, change detection, significance ranking, engagement tracking |
| Scraper | ET article parsing, Google News RSS, rate-limited bulk scraping, relevance scoring |
| Redis Service | Session state, dossier caching, with in-memory fallback if Redis unavailable |
| Elasticsearch | Full-text article search with field weighting, graceful degradation if unavailable |

### Progressive WebSocket Rendering

The Orchestrator supports progressive rendering via WebSocket. As each agent completes, partial results are streamed to the frontend — the timeline appears first, then entities, then synthesis, then archetype and contrarian in parallel. The user sees the dossier building in real time.

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js 15, React 19, TypeScript, D3.js (timelines, force graphs, sentiment charts), Framer Motion (animations), Zustand with localStorage persistence, Tailwind CSS, react-markdown |
| Backend | Python FastAPI, 17 API routers, 40+ endpoints, WebSocket for progressive rendering, async pipeline with parallel agent dispatch, structlog for structured logging |
| AI / NLP | Claude API (Anthropic) with streaming and structured JSON output, spaCy NER with custom Indian business entity patterns, multi-dimensional sentiment analysis, culturally-adapted vernacular translation |
| Database | PostgreSQL 16 (10 async SQLAlchemy models), Redis 7 (session memory, caching), Elasticsearch 8 (full-text search, optional) |
| Infrastructure | Docker Compose, Makefile, Alembic migrations, graceful degradation (Redis falls back to in-memory, Elasticsearch is optional), seed scripts for demo data |

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 22+
- PostgreSQL 16
- Redis 7
- Anthropic API key

### 1. Clone the Repository
```
git clone https://github.com/monisha-max/NarrativeAI.git
cd NarrativeAI
```

### 2. Install Backend Dependencies
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Install Frontend Dependencies
```
cd frontend
npm install
```

### 4. Start Infrastructure
Using Homebrew (macOS):
```
brew install postgresql@16 redis
brew services start postgresql@16
brew services start redis
```

Or using Docker:
```
docker-compose up -d postgres redis elasticsearch
```

### 5. Create Database
```
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
createuser narrativeai
createdb -O narrativeai narrativeai
psql -d narrativeai -c "ALTER USER narrativeai WITH PASSWORD 'narrativeai_dev';"
```

### 6. Configure Environment
```
cp .env.example backend/.env
```

Edit `backend/.env` and add your Anthropic API key:
```
DATABASE_URL=postgresql+asyncpg://narrativeai:narrativeai_dev@localhost:5432/narrativeai
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=
ANTHROPIC_API_KEY=your-api-key-here
```

### 7. Start the Backend
```
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 8. Start the Frontend
```
cd frontend
npm run dev
```

### 9. Open the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

---

## Project Structure

```
NarrativeAI/
├── backend/
│   ├── app/
│   │   ├── agents/           # 7 AI agents + system prompts
│   │   │   ├── orchestrator.py
│   │   │   ├── ingestion.py
│   │   │   ├── entity.py
│   │   │   ├── synthesis.py
│   │   │   ├── archetype.py
│   │   │   ├── contrarian.py
│   │   │   ├── ripple.py
│   │   │   └── prompts/
│   │   ├── api/v1/           # 17 API routers
│   │   │   ├── dossiers.py
│   │   │   ├── briefing.py
│   │   │   ├── chat.py
│   │   │   ├── debate.py
│   │   │   ├── earnings.py
│   │   │   ├── market_pulse.py
│   │   │   ├── portfolio_impact.py
│   │   │   ├── rumor_tracker.py
│   │   │   └── ws.py
│   │   ├── models/           # 10 SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # 9 shared services
│   │   │   ├── claude.py
│   │   │   ├── nlp.py
│   │   │   ├── sentiment.py
│   │   │   ├── fog.py
│   │   │   ├── silence.py
│   │   │   ├── delta.py
│   │   │   ├── scraper.py
│   │   │   ├── redis.py
│   │   │   └── elasticsearch.py
│   │   ├── core/             # Exceptions, logging, constants
│   │   └── db/               # Database session management
│   ├── data/
│   │   ├── archetypes/       # 5 archetype JSON definitions
│   │   └── corpus/           # 94-event demo corpus
│   ├── scripts/              # Seed and precompute scripts
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/              # 13 Next.js pages
│       │   ├── page.tsx              # Dashboard
│       │   ├── welcome/              # Cinematic onboarding
│       │   ├── dossier/[slug]/       # Living Dossier view
│       │   ├── briefing/[slug]/      # Briefing Room
│       │   ├── chat/                 # AI Chat
│       │   ├── debate/               # Debate Arena
│       │   ├── earnings/             # Earnings Decoder
│       │   ├── market-pulse/         # Market Pulse
│       │   ├── rumor-tracker/        # Rumor Tracker
│       │   ├── portfolio-impact/     # Portfolio Simulator
│       │   ├── search/               # Search/Create Dossiers
│       │   └── settings/             # User Settings
│       ├── components/
│       │   ├── dossier/      # Timeline, EntityGraph, StoryDNA, FogOfWar, etc.
│       │   ├── briefing/     # BriefingRoom, StreamingResponse, PromptCard
│       │   ├── dashboard/    # SixtySecondMode, DeltaCards, SilenceAlert
│       │   ├── controls/     # PerspectiveDial, LanguageSwitcher
│       │   └── ui/           # AIText (markdown renderer)
│       ├── hooks/            # useWebSocket, useDossier, useStreamingResponse
│       ├── stores/           # Zustand stores (user, perspective, session)
│       ├── lib/              # API client, constants, utilities
│       └── types/            # TypeScript type definitions
├── docker-compose.yml
├── Makefile
└── presentation/             # Pitch deck and architecture diagram
```

---
*Articles are dead. The dossier is alive.*
