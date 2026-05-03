<p align="center">
  <img src="https://img.shields.io/badge/Tests-87_Passing-138808?style=for-the-badge&logo=checkmarx" alt="Tests" />
  <img src="https://img.shields.io/badge/Coverage-68%25-FF6B2B?style=for-the-badge" alt="Coverage" />
  <img src="https://img.shields.io/badge/Google_Cloud-5_Services-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Google Cloud" />
  <img src="https://img.shields.io/badge/WCAG-AA_Compliant-138808?style=for-the-badge" alt="Accessibility" />
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Lok_Sabha-543_Seats-FF6B2B?style=for-the-badge" alt="Lok Sabha" />
  <img src="https://img.shields.io/badge/Majority-272_Seats-138808?style=for-the-badge" alt="Majority" />
  <img src="https://img.shields.io/badge/Parties-42-000080?style=for-the-badge" alt="Parties" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License" />
</p>

<h1 align="center">🏛️ India Election Simulator</h1>

<p align="center">
  <strong>AI-Powered Civic Education Platform for Indian Electoral Literacy</strong><br/>
  <em>Built on real 2024 Lok Sabha data • Powered by Google Cloud • WCAG AA Accessible</em>
</p>

<p align="center">
  <a href="#-the-problem">Problem</a> •
  <a href="#-our-solution">Solution</a> •
  <a href="#-google-cloud-architecture">Architecture</a> •
  <a href="#-features">Features</a> •
  <a href="#-testing">Testing</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-api-reference">API Reference</a>
</p>

---

## 🔴 The Problem

India is the world's largest democracy with **970 million eligible voters**, yet faces a critical civic education deficit:

- **Voter turnout: 65%** — First-time voters (18-25) show the lowest participation
- **Civic literacy gap**: Only 34% of Indian youth can correctly explain the FPTP voting system
- **Electoral misinformation**: EVM conspiracy theories and fake exit polls reach millions before corrections
- **Passive education**: Textbooks and PDFs fail to engage digital-native Gen Z voters

> *When citizens don't understand elections, they fall prey to misinformation, don't vote (48 votes decided Mumbai North West in 2024), and can't hold representatives accountable.*

## 💡 Our Solution

**India Election Simulator** is an AI-powered gamified civic education platform that teaches electoral literacy through **experiential learning** — not textbooks.

| Feature | Traditional Civics | India Election Simulator |
|---|---|---|
| **Format** | Textbooks, PDFs | Interactive AI-powered game |
| **Data** | Theoretical examples | Real 2024 Lok Sabha data (543 constituencies) |
| **Engagement** | Passive reading | Active decision-making with consequences |
| **Personalization** | None | AI adapts events via Vertex AI Gemini |
| **Assessment** | Written exams | In-game civics lessons + AI post-mortem |

### Measurable Impact KPIs

| Metric | Target |
|---|---|
| Civic literacy improvement | +40% quiz score after 1 playthrough |
| User engagement | >15 min avg. session duration |
| Knowledge retention | 85% can explain FPTP, coalition math, swing seats |
| Platform reach | 10,000 student users in first semester |

---

## ☁️ Google Cloud Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GOOGLE CLOUD                                │
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐      │
│  │  Cloud Run    │   │  Cloud Run   │   │  Vertex AI         │      │
│  │  (Frontend)   │   │  (Backend)   │   │  (Gemini 2.0)      │      │
│  │  Next.js 16   │   │  FastAPI     │   │  Dynamic Events    │      │
│  └──────┬───────┘   └──────┬───────┘   │  Campaign Advisor  │      │
│         │                  │            │  Post-mortem AI     │      │
│         │                  │            └────────┬───────────┘      │
│  ┌──────┴──────────────────┴─────────────────────┴──────────┐      │
│  │                  Google Cloud APIs                        │      │
│  ├──────────────┬──────────────┬──────────────┬──────────────┤      │
│  │  Firebase     │  Firestore   │   Cloud      │  Cloud       │      │
│  │  Auth         │  (Real-time  │   Storage    │  Logging     │      │
│  │  (Google      │   game DB)   │   (Assets)   │  (Monitoring)│      │
│  │   Sign-In)    │              │              │              │      │
│  └──────────────┴──────────────┴──────────────┴──────────────┘      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  CI/CD: GitHub Actions → Auto-test on push/PR → Cloud Run   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Google Cloud Services Used

| Service | Purpose in App | Integration Point |
|---|---|---|
| **Firebase Auth** | Google Sign-In for frictionless onboarding | `POST /api/v1/auth/google` |
| **Firestore** | Real-time game state sync + live leaderboard + analytics | `firestore_service.py` |
| **Vertex AI (Gemini 2.0)** | Dynamic event generation + AI campaign advisor + post-mortem | `vertex_ai_service.py` |
| **Cloud Storage** | User avatars + shareable game reports | `storage_service.py` |
| **Cloud Logging** | Structured JSON logs with request IDs | `cloud_logging.py` |
| **Cloud Run** | Auto-scaling deployment for frontend + backend | `Dockerfile` |

---

## ✨ Features

### 🎮 Core Gameplay
- **8-Week Campaign Simulation** — Navigate weekly strategic events across India's political landscape
- **5 Political Parties** — Play as BJP, INC, SP, TMC, or DMK with authentic alliance structures
- **4 Player Roles** — Party Leader (Hard), Campaign Manager (Medium), Swing Voter (Easy), Election Officer (Expert)
- **16+ Event Types** — Rallies, alliance crises, scams, media battles, caste politics, regional defense

### 🤖 AI & Simulation Engine
- **Monte Carlo Seat Projections** — 1,000-iteration probabilistic simulation across 543 constituencies
- **Vertex AI Gemini** — Dynamic, context-aware event generation that makes each playthrough unique
- **AI Campaign Advisor** — Real-time strategic advice powered by Gemini 2.0 (`GET /game/{id}/ai-advice`)
- **Adversarial Opponent AI** — Rule-based counter-strategy engine that responds to your every move
- **Alliance Engine** — NDA/INDIA bloc coalition math with negotiation mechanics

### 📊 Real Data Foundation
- **543 Constituencies** seeded from official 2024 election data
- **Actual margins, winners, and party affiliations** from the 18th Lok Sabha
- **State-wise seat math** covering all 36 States & UTs

### 📚 Civic Education
- **Civics Lessons** embedded in every event explaining real electoral mechanics
- **AI Post-Mortem** — Personalized election analysis powered by Vertex AI
- **Leaderboard System** with real-time Firestore sync

### ♿ Accessibility (WCAG 2.1 AA)
- **Skip-to-content link** for keyboard navigation
- **ARIA labels** on all interactive elements
- **Color contrast ≥ 4.5:1** on all text
- **`prefers-reduced-motion`** — animations disabled for motion-sensitive users
- **`prefers-contrast`** — high contrast mode support
- **Semantic HTML** — proper landmarks, roles, and heading hierarchy

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async REST API framework |
| **SQLAlchemy 2.0** | Async ORM with mapped columns |
| **SQLite + aiosqlite** | Zero-config async database |
| **Pydantic v2** | Data validation & settings management |
| **Firebase Admin SDK** | Google Sign-In token verification |
| **google-cloud-aiplatform** | Vertex AI Gemini integration |
| **google-cloud-storage** | Avatar & report file management |
| **google-cloud-logging** | Structured production logging |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 16** | React framework with App Router |
| **React 19** | UI library |
| **TypeScript** | Type-safe development |
| **Tailwind CSS 4** | Utility-first styling |
| **Firebase JS SDK** | Google Sign-In client |
| **Zustand** | Lightweight state management |
| **Framer Motion** | Animation library |
| **Recharts** | Data visualization |

---

## 🧪 Testing

### Test Suite: 87 Tests, 100% Passing

```
Backend:  71 tests (PyTest + pytest-asyncio)  — 68% coverage
Frontend: 16 tests (Jest + ts-jest)
```

| Test File | Tests | What It Covers |
|---|---|---|
| `test_auth.py` | 11 | Registration, login, JWT, protected routes |
| `test_game.py` | 9 | Game start, decisions, state, error handling |
| `test_seat_math.py` | 22 | Monte Carlo simulation, lean effects, difficulty |
| `test_alliance_engine.py` | 14 | Coalition math, negotiations, ally departure |
| `test_opponent_ai.py` | 9 | Counter-moves, budget depletion, game phases |
| `test_constituencies_router.py` | 6 | API filtering, swing seat queries |
| `gameStore.test.ts` | 8 | Zustand state management |
| `api.test.ts` | 8 | API client with mocked fetch |

### CI/CD Pipeline (GitHub Actions)

- **Trigger**: Push to `main`, PR to `main`
- **Backend Job**: Python 3.12 → `pytest --cov`
- **Frontend Job**: Node 20 → `jest` + `next build`
- **Lint Job**: ESLint type checking

```bash
# Run tests locally
cd india-democracy-simulator/backend && pytest --cov=app -v
cd india-democracy-simulator/frontend && npm test
```

---

## 🏗 Architecture

```
india-democracy-simulator/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app + middleware
│   │   ├── config.py             # Pydantic settings (GCP config)
│   │   ├── database.py           # Async SQLAlchemy engine
│   │   ├── firebase_config.py    # Firebase Admin SDK init
│   │   ├── cloud_logging.py      # Google Cloud Logging
│   │   ├── models/               # SQLAlchemy ORM (10 models)
│   │   ├── schemas/              # Pydantic request/response
│   │   ├── routers/
│   │   │   ├── auth.py           # JWT + Firebase Google Sign-In
│   │   │   ├── game.py           # Game lifecycle + AI advisor
│   │   │   ├── constituencies.py # Constituency data queries
│   │   │   └── leaderboard.py    # Scores & feedback
│   │   └── services/
│   │       ├── game_engine.py    # Session lifecycle
│   │       ├── seat_math.py      # Monte Carlo simulation
│   │       ├── alliance_engine.py# Coalition math
│   │       ├── opponent_ai.py    # Counter-strategy AI
│   │       ├── ai_inference.py   # Event generation (Vertex AI fallback)
│   │       ├── vertex_ai_service.py  # Gemini integration
│   │       ├── firestore_service.py  # Real-time sync
│   │       └── storage_service.py    # Cloud Storage
│   ├── tests/                    # 71 PyTest tests
│   ├── Dockerfile                # Cloud Run deployment
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Landing page (ARIA-labeled)
│   │   ├── layout.tsx            # Root layout (skip link, semantic)
│   │   ├── globals.css           # Design system + WCAG styles
│   │   ├── (auth)/login/         # Login + Google Sign-In
│   │   └── (game)/
│   │       ├── war-room/         # Main gameplay dashboard
│   │       ├── role-select/      # Party & role selection
│   │       ├── results/          # Post-game analysis
│   │       └── leaderboard/      # Global rankings
│   ├── components/ui/
│   │   └── GoogleSignInButton.tsx# Firebase Google Sign-In
│   ├── lib/
│   │   ├── api.ts                # API client
│   │   └── firebase.ts           # Firebase client SDK
│   ├── store/gameStore.ts        # Zustand state
│   ├── __tests__/                # 16 Jest tests
│   ├── Dockerfile                # Cloud Run deployment
│   └── jest.config.ts
│
├── .github/workflows/ci.yml     # CI/CD pipeline
└── PROBLEM_STATEMENT.md          # Civic education framing
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+ and Node.js 20+
- Google Cloud project (for Firebase Auth, Vertex AI)

### Backend Setup

```bash
cd india-democracy-simulator/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Seed the database with real 2024 election data
python -m scripts.seed_constituencies

# Run the backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd india-democracy-simulator/frontend
npm install

# Set API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Run the frontend
npm run dev
```

### Run Tests

```bash
# Backend (71 tests)
cd india-democracy-simulator/backend
pytest --cov=app -v

# Frontend (16 tests)
cd india-democracy-simulator/frontend
npm test
```

### Deploy to Cloud Run

```bash
# Backend
gcloud run deploy election-sim-backend \
  --source=india-democracy-simulator/backend \
  --region=us-central1 \
  --allow-unauthenticated

# Frontend
gcloud run deploy election-sim-frontend \
  --source=india-democracy-simulator/frontend \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_URL=<BACKEND_URL>/api/v1"
```

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | ❌ | Register with email/password |
| `POST` | `/api/v1/auth/login` | ❌ | Login, returns JWT |
| `POST` | `/api/v1/auth/google` | ❌ | Google Sign-In via Firebase |
| `POST` | `/api/v1/game/start` | ✅ | Start new game session |
| `POST` | `/api/v1/game/{id}/decision` | ✅ | Submit campaign decision |
| `GET` | `/api/v1/game/{id}/state` | ✅ | Get current game state |
| `GET` | `/api/v1/game/{id}/ai-advice` | ✅ | AI campaign strategy advisor |
| `GET` | `/api/v1/game/{id}/post-mortem` | ✅ | Post-game election analysis |
| `GET` | `/api/v1/constituencies` | ❌ | List constituencies (filterable) |
| `GET` | `/api/v1/constituencies/swing` | ❌ | Swing & super-swing seats |
| `GET` | `/api/v1/leaderboard` | ❌ | Global rankings |
| `POST` | `/api/v1/feedback/event` | ✅ | Submit event feedback |
| `GET` | `/health` | ❌ | Health check + GCP status |

---

## 🎮 Gameplay

1. **Register/Login** → Create account or sign in with Google
2. **Choose Party & Role** → Pick from BJP, INC, SP, TMC, DMK
3. **Campaign for 8 Weeks** → Make strategic decisions each week
4. **Learn While Playing** → Every event includes a real civics lesson
5. **Win the Election** → Reach 272 seats for a Lok Sabha majority
6. **Review Post-Mortem** → AI-powered analysis of your campaign

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built for the Google Cloud Hackathon 2025</strong><br/>
  <em>"Democracy is not just about voting. It's about understanding why your vote matters."</em>
</p>
