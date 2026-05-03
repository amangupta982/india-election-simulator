<p align="center">
  <img src="https://img.shields.io/badge/Lok_Sabha-543_Seats-FF6B2B?style=for-the-badge&logo=data:image/svg+xml;base64,..." alt="Lok Sabha" />
  <img src="https://img.shields.io/badge/Majority-272_Seats-138808?style=for-the-badge" alt="Majority" />
  <img src="https://img.shields.io/badge/Parties-42-000080?style=for-the-badge" alt="Parties" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License" />
</p>

<h1 align="center">🏛️ India Election Simulator</h1>

<p align="center">
  <strong>AI-Powered Lok Sabha Election Strategy Game</strong><br/>
  <em>Built on real 2024 Indian General Election data — 543 constituencies, 42 parties, one majority.</em>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#️-tech-stack">Tech Stack</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-gameplay">Gameplay</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 📖 About

**India Election Simulator** is a full-stack, AI-powered civic education game that lets players experience the complexity of Indian general elections. Players choose a political party, assume a strategic role, and navigate 8 weeks of campaign decisions — managing budgets, alliances, crises, and booth-level operations — all backed by a **Monte Carlo simulation engine** using real constituency-level data from the **2024 Lok Sabha Elections**.

Every decision teaches real Indian electoral mechanics: from FPTP voting and coalition arithmetic to caste politics, EVM controversies, and the Model Code of Conduct.

---

## ✨ Features

### 🎮 Core Gameplay
- **8-Week Campaign Simulation** — Navigate weekly strategic events across India's political landscape
- **5 Political Parties** — Play as BJP, INC, SP, TMC, or DMK with authentic alliance structures
- **4 Player Roles** — Party Leader (Hard), Campaign Manager (Medium), Swing Voter (Easy), Election Officer (Expert)
- **16+ Event Types** — Rallies, alliance crises, scams, media battles, caste politics, regional defense

### 🤖 AI & Simulation Engine
- **Monte Carlo Seat Projections** — 1,000-iteration probabilistic simulation across 543 constituencies
- **Adversarial Opponent AI** — Rule-based counter-strategy engine that responds to your every move
- **Dynamic Constituency Modeling** — Lean scores, volatility, and seat classifications (safe/swing/super-swing)
- **Alliance Engine** — NDA/INDIA bloc coalition math with negotiation mechanics and loyalty dynamics

### 📊 Real Data Foundation
- **563 Constituencies** seeded from official 2024 election CSV data
- **Actual margins, winners, and party affiliations** from the 18th Lok Sabha
- **State-wise seat math** covering all 36 States & UTs
- **Authentic party alliance structures** (NDA, INDIA bloc, swing parties)

### 📚 Civic Education
- **Civics Lessons** embedded in every game event explaining real electoral mechanics
- **Post-Game Analysis** with turning points, state breakdowns, and constitutional principles
- **Leaderboard System** to compare strategic performance across sessions

### 🎨 Premium UI/UX
- **Dark-themed glassmorphism design** with Indian tricolor accents (Saffron, White, Green)
- **Framer Motion animations** with particle effects, animated counters, and micro-interactions
- **Real-time seat projection charts** powered by Recharts
- **Responsive design** optimized for desktop and mobile

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async REST API framework |
| **SQLAlchemy 2.0** | Async ORM with mapped columns |
| **SQLite + aiosqlite** | Zero-config async database |
| **Pydantic v2** | Data validation & settings management |
| **Python-Jose** | JWT authentication |
| **Pandas / NumPy** | Data processing & constituency seeding |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 16** | React framework with App Router |
| **React 19** | UI library |
| **TypeScript** | Type-safe development |
| **Tailwind CSS 4** | Utility-first styling |
| **Zustand** | Lightweight state management |
| **Framer Motion** | Animation library |
| **Recharts** | Data visualization |
| **TanStack React Query** | Server state management |

---

## 🏗 Architecture

```
india-democracy-simulator/
├── backend/                    # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── config.py           # Pydantic settings (env-driven)
│   │   ├── database.py         # Async SQLAlchemy engine & sessions
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   └── __init__.py     # User, GameSession, Constituency, etc.
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── routers/            # API route handlers
│   │   │   ├── auth.py         # Registration & JWT login
│   │   │   ├── game.py         # Game lifecycle endpoints
│   │   │   ├── constituencies.py # Constituency data queries
│   │   │   └── leaderboard.py  # Scores & feedback
│   │   ├── services/           # Business logic layer
│   │   │   ├── game_engine.py  # Session lifecycle & turn management
│   │   │   ├── seat_math.py    # Monte Carlo simulation engine
│   │   │   ├── alliance_engine.py # Coalition math & negotiations
│   │   │   ├── opponent_ai.py  # Adversarial counter-strategy AI
│   │   │   └── ai_inference.py # Event generation (static pool → AI)
│   │   └── websocket/          # Real-time WebSocket manager
│   ├── scripts/
│   │   └── seed_constituencies.py  # CSV → database seeder
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # Next.js 16 React Frontend
│   ├── app/
│   │   ├── page.tsx            # Landing page with animated hero
│   │   ├── layout.tsx          # Root layout with fonts & metadata
│   │   ├── globals.css         # Design system (glassmorphism, tricolor)
│   │   ├── (auth)/login/       # Authentication flow
│   │   └── (game)/             # Game routes (grouped)
│   │       ├── role-select/    # Party & role selection
│   │       ├── war-room/       # Main gameplay screen
│   │       ├── results/        # Election results & post-mortem
│   │       └── leaderboard/    # Global leaderboard
│   ├── components/             # Reusable UI components
│   │   ├── event-card/         # Game event display
│   │   ├── seat-tally/         # Real-time seat projections
│   │   ├── polling-chart/      # Recharts visualizations
│   │   ├── opponent-feed/      # Opponent move tracker
│   │   └── post-mortem/        # Post-game analysis
│   ├── lib/api.ts              # API client (fetch wrapper)
│   └── store/gameStore.ts      # Zustand state management
│
├── data/
│   └── raw/
│       └── Indian_General_Elections_2024.csv  # Source election data
│
└── model/                      # ML model pipeline (Phase 2)
    ├── data/                   # Training data (processed/synthetic)
    ├── training/               # Model training scripts
    ├── inference/              # Inference server config
    └── prompts/                # LLM prompt templates
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** (LTS recommended)
- **npm** or **yarn**

### 1. Clone the Repository
```bash
git clone https://github.com/amangupta982/india-election-simulator.git
cd india-election-simulator
```

### 2. Backend Setup
```bash
cd india-democracy-simulator/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Seed constituency data (563 constituencies from 2024 CSV)
python scripts/seed_constituencies.py

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger documentation.

### 3. Frontend Setup
```bash
cd india-democracy-simulator/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## 🎮 Gameplay

### How It Works

1. **Register & Login** — Create an account or log in with existing credentials
2. **Choose Your Party** — Select from BJP, INC, SP, TMC, or DMK
3. **Pick Your Role** — Each role has different difficulty and perspective:
   - 👑 **Party Leader** — Full strategic control (Hard)
   - 📊 **Campaign Manager** — Budget & operations focus (Medium)
   - 🗳️ **Swing Voter** — Observe and decide (Easy)
   - ⚖️ **Election Officer** — Guard democracy (Expert)
4. **Navigate 8 Weeks** — Each week brings a new event (rally, crisis, alliance negotiation, etc.)
5. **Make Strategic Decisions** — Every choice affects seat projections, approval ratings, and budgets
6. **Watch the AI Respond** — The opponent AI counter-strategizes against your moves
7. **Election Day** — See if you crossed the **272-seat majority mark**!

### Key Mechanics

| Mechanic | Description |
|---|---|
| **Seat Projection** | Monte Carlo simulation projects your seat count in real-time |
| **Budget Management** | ₹500 crore starting budget — every rally and ad costs money |
| **Approval Rating** | National approval affects global seat lean (±3% per point) |
| **Alliance Math** | Coalition partners provide lean bonuses in their stronghold states |
| **Opponent AI** | Counter-rallies, attack ads, alliance poaching, and booth deployments |
| **Swing Seats** | Super-swing seats (margin < 5,000) are the battleground |

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login & receive JWT token |

### Game
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/game/start` | Start a new game session |
| `POST` | `/api/v1/game/{session_id}/decision` | Submit a player decision |
| `GET` | `/api/v1/game/{session_id}/state` | Get current game state |
| `GET` | `/api/v1/game/{session_id}/post-mortem` | Get post-game analysis |

### Data
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/constituencies` | List all constituencies |
| `GET` | `/api/v1/constituencies/swing` | Get swing constituencies |
| `GET` | `/api/v1/leaderboard` | Get global leaderboard |

### WebSocket
| Endpoint | Description |
|---|---|
| `ws://localhost:8000/ws/{session_id}` | Real-time game updates |

### Health Check
```bash
curl http://localhost:8000/health
# → {"status": "ok", "app": "India Democracy Simulator"}
```

---

## 🗄 Database Schema

The application uses **10 SQLAlchemy models** with the following core entities:

| Model | Description |
|---|---|
| `Constituency` | 563 Lok Sabha constituencies with 2024 results |
| `User` | Registered players with game statistics |
| `GameSession` | Individual game playthroughs |
| `GameStateSnapshot` | Weekly state snapshots (budget, approval, projections) |
| `GameEvent` | AI-generated or static game events |
| `PlayerDecision` | Player choices with applied effects |
| `OpponentMove` | AI opponent counter-strategies |
| `LeaderboardEntry` | High scores with party and role |
| `ModelFeedback` | User feedback on AI-generated events |

---

## 🧪 Game Engine Details

### Monte Carlo Simulation
The seat projection engine runs **1,000 iterations** per simulation:

```python
# Each constituency outcome = lean_score + Gaussian noise
outcome = rng.gauss(constituency.lean_score, constituency.volatility)
# outcome > 0 → player wins the seat
```

- **Safe seats** (margin > 100,000): lean ±0.8, volatility 0.08
- **Swing seats** (margin 5,000–100,000): lean ±0.4, volatility 0.20
- **Super-swing seats** (margin < 5,000): lean ±0.1, volatility 0.35

### Difficulty Modifiers
| Difficulty | Effect Multiplier |
|---|---|
| Easy | 1.3× (effects boosted) |
| Normal | 1.0× (baseline) |
| Hard | 0.7× (effects reduced) |
| Expert | 0.5× (effects halved) |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow **PEP 8** for Python code
- Use **TypeScript** strict mode for frontend
- Write meaningful commit messages following [Conventional Commits](https://www.conventionalcommits.org/)
- Add civics lessons to new game events

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Election Commission of India** — For maintaining the world's largest democratic exercise
- **2024 Lok Sabha Election Data** — Sourced from publicly available election results
- Built with ❤️ for civic education and democratic awareness

---

<p align="center">
  <strong>🗳️ Every vote matters. Mumbai North West was decided by 48 votes in 2024.</strong>
</p>
