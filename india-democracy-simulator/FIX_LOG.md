# India Election Simulator — FIX LOG

All bugs fixed. All UI screens redesigned. Date: 2026-05-02.

---

## 🔧 Part 1: Bugs Fixed

### 1. PostgreSQL → SQLite Migration
**Problem**: Backend required a running PostgreSQL instance with `asyncpg`, `JSONB`, `ARRAY(String)`, and `UUID(as_uuid=True)` — all PostgreSQL-specific. Without PostgreSQL, the backend crashes on import.

**Fix**:
- Replaced `asyncpg` with `aiosqlite` in `requirements.txt`
- Changed `DATABASE_URL` from `postgresql+asyncpg://...` to `sqlite+aiosqlite:///./india_democracy_sim.db`
- Replaced all `JSONB` → `JSON` (portable SQLAlchemy type)
- Replaced all `ARRAY(String)` → `JSON` (store arrays as JSON)
- Replaced all `UUID(as_uuid=True)` → `String(36)` with `str(uuid.uuid4())`
- Added `connect_args={"check_same_thread": False}` for SQLite async
- Updated `database.py`, `models/__init__.py`, all routers, `game_engine.py`, and `seed_constituencies.py`

### 2. EmailStr Import Error
**Problem**: `schemas/__init__.py` imported `EmailStr` from pydantic but `email-validator` was not in `requirements.txt`. This causes `ImportError` on import.

**Fix**: Removed unused `EmailStr` import. Email fields already use `str` type.

### 3. Pydantic Protected Namespace Warning
**Problem**: Settings fields `model_endpoint`, `model_timeout_seconds`, `model_max_retries` conflict with Pydantic v2's reserved `model_` namespace.

**Fix**: Added `"protected_namespaces": ()` to Settings `model_config`.

### 4. Next.js Route Group URL Paths
**Problem**: All `router.push("/(auth)/login")`, `Link href="/(auth)/login"`, `router.push("/(game)/war-room")` etc. used Next.js route group folder names as URL paths. Route groups `(auth)` and `(game)` are **organizational only** — they don't appear in URLs.

**Fix**: Changed all paths:
- `/(auth)/login` → `/login`
- `/(game)/role-select` → `/role-select`
- `/(game)/war-room` → `/war-room`
- `/(game)/results` → `/results`
- `/(game)/leaderboard` → `/leaderboard`

### 5. Unused Import in EventCard
**Problem**: `OpponentMove` imported but never used in `components/event-card/index.tsx`.

**Fix**: Removed unused import.

### 6. TypeScript Error in Leaderboard
**Problem**: `getLeaderboard().then((data) => ...)` — `data` inferred as `unknown` because `apiFetch<T>` was called without type parameter.

**Fix**: Added explicit `any` type annotation to the parameter.

### 7. SSR ReferenceError in Zustand Store
**Problem**: `localStorage.getItem("ids_token")` at Zustand store initialization level caused `ReferenceError: location is not defined` during Next.js static generation.

**Fix**: Changed initial token to `null`, wrapped localStorage access in try/catch.

### 8. Missing .env.example
**Problem**: No documentation of required environment variables.

**Fix**: Created `.env.example` with all necessary vars.

### 9. Seed Script PostgreSQL Syntax
**Problem**: Seed script used PostgreSQL-specific `CAST(:lean AS JSONB)` syntax.

**Fix**: Rewrote to use `json.dumps()` with plain JSON column type.

---

## 🎨 Part 2: UI Redesign

### Design System (`globals.css`)
- **New palette**: Base `#0A0F1E`, accent saffron `#FF6B2B`, India green `#138808`
- **Glassmorphism**: `backdrop-filter: blur(24px) saturate(1.2)` with subtle borders
- **Typography**: Inter + Outfit with extrabold weights, uppercase tracking labels
- **Component classes**: `.glass-card`, `.glass-card-glow`, `.btn-saffron`, `.btn-ghost`, `.choice-btn`, `.input-field`, `.badge-*`, `.week-dot`
- **Animations**: Float particles, shimmer loading, pulse glow, slow spin, count pulse

### Pages Redesigned
1. **Landing** — Ambient glow orbs, tricolor gradient title, 4 role preview cards with difficulty badges, animated seat bar with majority marker, feature cards
2. **Login** — Tricolor accent line, glassmorphism card with glow, animated icon, loading spinner in button, styled input fields
3. **Role Select** — 3-step wizard with progress dots, party cards with seat bars, campaign briefing summary, difficulty selector grid
4. **War Room** — Sticky header with week progress dots, 4 stat cards with icons, redesigned seat tally with gradient fills, event cards with effect previews, opposition feed with ping indicator
5. **Results** — Dramatic 3-step reveal animation, win/loss conditional styling, key numbers grid, NDTV-style post-mortem sections, civics insight panels
6. **Leaderboard** — Gold/silver/bronze row gradients, empty state with CTA, responsive table, color-coded margins

### Components Redesigned
- `<EventCard>` — Typed event badges, numbered choices with saffron indicators, inline effect previews
- `<SeatTallyBar>` — Animated gradient bar fills with inner shine, majority marker dot, scale markings
- `<OpponentFeed>` — Live ping indicator, move-type icons, state target pills, gradient accent bars

---

## ✅ Verification Results

| Check | Status |
|-------|--------|
| Backend imports | ✅ `from app.main import app` — no errors |
| Backend starts | ✅ `uvicorn app.main:app` on :8000 |
| Health endpoint | ✅ `{"status":"ok","app":"India Democracy Simulator"}` |
| DB seeded | ✅ 563 constituencies (443 safe, 102 swing, 18 super_swing) |
| API works | ✅ `/api/v1/constituencies?state=Delhi` returns 7 constituencies |
| Frontend builds | ✅ All 6 routes: `/`, `/login`, `/role-select`, `/war-room`, `/results`, `/leaderboard` |
| Frontend runs | ✅ `next dev` on :3000 |
| TypeScript | ✅ Zero type errors |
