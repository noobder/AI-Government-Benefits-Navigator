# AI Government Benefits Navigator

**Making government benefits easier to discover, understand, and access.**

Government schemes already exist. The problem is access: people don't know
which schemes they qualify for, what documents they need, or how to apply.
This app lets someone describe their situation in plain language (typed or
spoken, in English, Hindi, or Tamil) and returns transparent, explainable
matches against a verified scheme database — never a hallucinated answer.

Built for low-literacy and first-time users specifically: a Simple Mode with
bigger buttons and less text, read-aloud-with-captions on every page, an
experimental hand-sign (yes/no) input for people who'd rather not type or
speak, and a guided in-app tutorial — on top of guest-first usage (no account
ever required) with optional accounts and a full admin console for managing
the scheme database.

> ⚠️ **This is a hackathon MVP.** All 14 schemes in `data/seed_schemes.json`
> are clearly labeled `[DEMO]`/`is_demo: true` **sample data for
> demonstration only** — they are not real government schemes. Swap in
> verified official data before using this for anything beyond a demo.

## Submission assets

- **Demo video**: [`demo/flow_recording.mp4`](demo/flow_recording.mp4) — a
  narrated, ~2:40 screen recording of the actual running app (student
  scholarship chat flow, why/documents/details, guided profile, benefits
  dashboard), recorded with Playwright against the real Docker stack and
  narrated with offline Windows TTS. Regenerate it any time with the scripts
  in `video-tools/` (`synthesize_narration.ps1` then `record_demo.py` then
  `finalize_video.py`, with `docker compose up -d` running first).

## How it works

```
Natural Language (text or voice)
        ↓
LLM: understand + extract structured profile   (never decides eligibility)
        ↓
RAG retrieval over the verified scheme database
        ↓
Deterministic eligibility engine (AND/OR rule evaluation, transparent)
        ↓
Explainable ranking → "Why this scheme?" / "What am I missing?"
        ↓
Document checklist + application steps + official source link
```

The LLM is used **only** for understanding language, extracting a profile,
phrasing follow-up questions, and light translation. It is never the source
of truth for scheme existence, eligibility, documents, or URLs — those
always come from `data/seed_schemes.json` via the deterministic eligibility
engine (`backend/app/services/eligibility_service.py`).

## Project structure

```
backend/            FastAPI app (API, services, RAG, eligibility engine, auth)
backend/alembic/    Database migrations (see "Database migrations" below)
frontend/           React + TypeScript + Vite + Tailwind UI
ingestion/          Document ingestion pipeline for supplementary docs
data/seed_schemes.json   Structured, verified (demo) scheme database, with
                         per-language (hi/ta) translations embedded
video-tools/        Scripts that generated demo/flow_recording.mp4
docker-compose.yml
.env.example
```

See inline comments in `backend/app/services/*` for how each piece
(profile extraction, eligibility, ranking, RAG, voice, translation) is
isolated and swappable.

## Running locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env       # then optionally add your Gemini/OpenAI key (see Configuration)
uvicorn app.main:app --reload
```

Runs on `http://127.0.0.1:8000`. On startup it creates a local SQLite DB
(`benefits_navigator.db`) and seeds it from `data/seed_schemes.json`
automatically — no manual seeding step needed.

API docs: `http://127.0.0.1:8000/docs`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173` and proxies `/api/*` to the backend.

### Docker (production-style, verified working)

```powershell
docker compose up --build -d
```

This brings up three containers wired together and health-checked:

- **postgres** — PostgreSQL 16, with a healthcheck gating startup order.
- **backend** — FastAPI on Uvicorn, waits for Postgres to be healthy, creates
  tables and seeds the 14 demo schemes on boot, exposes `GET /api/health`
  (checks real DB connectivity, not just process liveness).
- **frontend** — production Vite build served by nginx, which reverse-proxies
  `/api/*` to the backend container so the browser only ever talks to one
  origin (no CORS needed in this path).

Open **http://localhost:8080** — that's the whole app on one port. Check
container health with `docker compose ps` (all three should show `healthy`
after ~15–20s). Tear down with `docker compose down` (add `-v` to also drop
the Postgres volume).

## Deploying to a cloud host

The images are plain Docker, so any container host works:

- **Single VM / VPS**: `git clone`, then `docker compose up --build -d`. Put
  a reverse proxy (Caddy/nginx) with TLS in front of port 8080, or change
  the frontend's published port in `docker-compose.yml`.
- **Render / Railway / Fly.io**: deploy `backend/` and `frontend/` as two
  separate services from their Dockerfiles, plus a managed Postgres add-on.
  Set `DATABASE_URL` on the backend service to the managed Postgres URL, and
  `CORS_ORIGINS` to the frontend's public URL (since they won't share an
  origin the way the nginx-proxied docker-compose setup does). The backend
  Dockerfile already respects an injected `$PORT` env var, which these
  platforms set automatically.
- **Kubernetes**: the `HEALTHCHECK` directives in both Dockerfiles map
  directly to liveness/readiness probes (`GET /api/health` for the backend,
  `GET /` for the frontend).

## Configuration

Copy `.env.example` to `.env` — in `backend/` for local runs, or in the repo
root (next to `docker-compose.yml`) for Docker — and adjust as needed.
Everything works out of the box with zero API keys.

### Using Gemini or OpenAI (recommended for best results)

The default `mock` provider is an offline regex/keyword extractor. For
natural, free-form understanding of any phrasing in English, Hindi, or Tamil,
plug in a real LLM key:

```env
# Google Gemini (key from https://aistudio.google.com/apikey)
LLM_PROVIDER=gemini
LLM_API_KEY=your-key-here
# LLM_MODEL=gemini-2.5-flash      # optional, this is the default

# ...or OpenAI (key from https://platform.openai.com/api-keys)
LLM_PROVIDER=openai
LLM_API_KEY=your-key-here
# LLM_MODEL=gpt-4o-mini           # optional, this is the default
```

Restart the backend (or `docker compose up -d`) after changing `.env`. The
startup log states which provider is active. If the key is missing or a call
fails (bad key, quota, network), the app logs a warning and falls back to the
offline extractor instead of erroring. The LLM still never decides
eligibility — it only turns the user's words into a structured profile.

- `LLM_PROVIDER=mock` — the offline default (see `MockLLMProvider` in
  `llm_service.py`); handles profile extraction for English, Hindi, and Tamil.
- `EMBEDDING_PROVIDER=keyword` — a pure-Python TF-IDF vector store
  (`KeywordVectorStore`) powers retrieval with no external calls. The
  `VectorStore` interface is ready to swap in FAISS/Chroma/Qdrant.
- Voice input/output runs **in the browser** via the Web Speech API
  (English, Hindi, and Tamil supported in Chromium browsers) — no backend
  speech service required. `SPEECH_TO_TEXT_API_KEY` / `TEXT_TO_SPEECH_API_KEY`
  are there for wiring up a real cloud provider later.
- Auth (`SECRET_KEY`, `COOKIE_SECURE`, `ADMIN_EMAIL`/`ADMIN_PASSWORD`) — see
  "Accounts & admin" below. `SECRET_KEY` must be overridden in any real
  deployment (`openssl rand -hex 32`).

## Accounts & admin

Guest usage is always fully functional — no login is ever required for the
core product. An account is optional and only adds cross-device sync of your
profile and saved schemes:

- `POST /api/auth/register` / `/login` / `/logout` / `/refresh`, `GET /api/auth/me`.
  Passwords are bcrypt-hashed; sessions are short-lived JWT access tokens +
  rotating refresh tokens delivered as httpOnly cookies (never readable by
  page JavaScript). Login is rate-limited (10/min) and an account locks for
  15 minutes after 5 failed attempts.
- **Admin** is a separate role, seeded from `ADMIN_EMAIL`/`ADMIN_PASSWORD` env
  vars on first boot (idempotent) — there's no open admin self-registration
  endpoint. Signed-in admins get `/admin` in the app: full scheme CRUD
  (create/edit/delete, including a JSON editor for eligibility rules and
  per-language translations), an accounts list, and an audit log of every
  admin action (`admin_audit_log` table).
- All of this is behind `require_user`/`require_admin` FastAPI dependencies
  (`backend/app/api/deps.py`) — a non-admin gets 403, a guest gets 401,
  both covered by tests.

## Accessibility

- **Dark / light / system theme**, high-contrast and large-text toggles, all
  independent of each other, built on CSS custom properties so every
  component actually re-themes (not just a contrast filter over the light
  palette).
- **Simple Mode** (Settings): restructures the home page into a few large,
  stacked actions and bigger category tiles for a first-time or low-literacy
  visitor.
- **Read-aloud with captions**: a floating 🔊 button on every page reads the
  visible content aloud in the active language, with the text shown as a
  caption at the same time — never audio-only.
- **Guided tutorial + scoped help assistant** (❓ button): a 6-step guided
  tour that narrates while actually navigating the real app, and a
  question-answering assistant scoped only to "how do I use this app"
  questions (it explicitly declines general-knowledge questions rather than
  guessing) — see `backend/app/services/help_assistant_service.py`.
- **"Fill with AI"** on the guided profile form: describe yourself in one
  sentence (typed or spoken) instead of tabbing through every field; reuses
  the same extraction the chat uses, so it never fabricates a value the form
  wouldn't otherwise accept.
- **Experimental hand-sign input** (opt-in, Settings): recognizes exactly two
  static hand poses — 👍 thumbs up ("yes") and ✋ open palm ("no") — via
  on-device MediaPipe hand-landmark detection (no video leaves the browser),
  as a fast alternative to typing/speaking for yes/no questions. This is a
  small-vocabulary gesture recognizer, not sign-language understanding, and
  is labeled as such everywhere it appears; tapping always still works.

## Multi-language support (English / Hindi / Tamil)

Every layer is localized, not just the UI shell:

- **Frontend**: `react-i18next` with `frontend/src/locales/{en,hi,ta}.json` —
  every component uses translation keys, none of the old per-component
  ternary hacks remain. A Vitest test (`locales.test.ts`) fails the build if
  the three locale files ever drift out of key-parity.
- **Profile extraction**: `MockLLMProvider` (`llm_service.py`) has separate
  regex/keyword rules for Hindi and Tamil (age, income, state names,
  farmer/student detection, land ownership, gender, disability, employment),
  covered by dedicated Hindi extraction tests.
- **Eligibility explanations**: the deterministic engine
  (`eligibility_service.py`) builds every "why"/"what's missing" sentence
  from templates in `app/i18n/strings.py`, parameterized by language — field
  names, boolean yes/no, and the surrounding sentence are all translated,
  not just scheme names.
- **Scheme content**: `data/seed_schemes.json` carries a `translations`
  field per scheme (`{"hi": {...}, "ta": {...}}` — name, description,
  benefits, documents, application steps), with automatic fallback to
  English for anything not yet translated. Admins can edit these per-scheme
  from `/admin`.
- **Voice**: the browser's Web Speech API is used for both STT and TTS in
  all three languages (`hi-IN`/`ta-IN`/`en-IN`), with live interim results
  shown as you speak and a plain-language error if nothing was heard.

## Database migrations

Schema changes go through Alembic (`backend/alembic/`), not just
`Base.metadata.create_all()` — the app runs `alembic upgrade head` on every
boot (`backend/app/main.py`), which correctly handles both a brand-new
database and an existing one that needs incremental changes applied. It also
detects and self-heals the one-time case of adopting Alembic on a database
that predates it (stamps the baseline revision instead of erroring on
"table already exists").

To add a schema change: edit `backend/app/models/*.py`, then run
`.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "description"`
from `backend/`, review the generated file (autogenerate gets nullable/NOT
NULL details wrong often enough that it's always worth checking), and let
the app apply it on next boot — or run `alembic upgrade head` manually.

## Testing

```powershell
# Backend — 50 tests: eligibility engine, profile extraction (EN/HI/TA),
# Gemini/OpenAI providers + fallback, scheme matching, auth flows, admin
# CRUD + audit log, help assistant, and localization (Hindi/Tamil
# eligibility explanations + scheme content)
cd backend
.\.venv\Scripts\python.exe -m pytest -v

# Frontend — 20 tests: Button accessibility sizing, EligibilityBadge status
# mapping, useVoice's interim-results behavior (the fix for the original
# "voice input does nothing" bug), and locale-file key-parity
cd frontend
npm run test
```

A full cross-cutting regression pass (`video-tools/regression_pass.py`)
additionally drives every route in all 3 languages and both themes through
Playwright against the live Docker stack, asserting no console errors and
that every page actually renders content.

## Demo scenarios

**Student:** *"I am a 20-year-old engineering student from Tamil Nadu. My
family income is ₹1.5 lakh per year. What scholarships can I apply for?"*
→ matches the demo Tamil Nadu Engineering Scholarship as `likely_eligible`,
plus several `missing_information` matches asking for e.g. previous academic
percentage.

**Farmer:** *"I'm a 45 year old farmer from Tamil Nadu. I have 2 acres of
land and my annual income is around ₹2 lakh."* → matches Farm Mechanization
Subsidy as `likely_eligible`; Small Farmer Income Support asks for
`land_ownership` since eligibility depends on owned vs. leased land.

**Tamil voice:** Select தமிழ் in the language switcher, tap 🎤, and speak —
the browser transcribes Tamil speech, the same workflow runs, and the
assistant replies (and can speak back) in Tamil.

**Hindi, fully localized:** *"मैं तमिलनाडु का 20 वर्षीय इंजीनियरिंग छात्र हूं। मेरी वार्षिक आय 1.5 लाख रुपये है।"*
→ the scheme name, description, eligibility explanation ("आपकी बताई गई छात्र
स्थिति (हां) इस आवश्यकता को पूरा करती है"), documents, and application steps
all come back in Hindi — not just the surrounding chat UI.

## Production readiness

This has been verified running as a real containerized deployment, not just
local dev servers:

- `docker compose up --build -d` was run end-to-end on this machine: all
  three containers (`postgres`, `backend`, `frontend`) reach `healthy`, the
  backend correctly persists to Postgres (not SQLite) in that mode, and the
  full chat → eligibility → recommendation flow was exercised through the
  nginx entrypoint on port 8080.
- Unhandled backend errors are caught by a global exception handler and
  return a safe message instead of a stack trace or a crash.
- LLM extraction failures and RAG retrieval failures are individually
  caught in the workflow and fall back to the already-known profile /
  plain structured search, per the app's "never hallucinate, degrade
  gracefully" requirement — they don't take down the request.
- The eligibility engine supports arbitrarily nested `AND`/`OR` condition
  trees with correct three-valued logic (true/false/"we don't know yet"),
  not just a single flat rule group.
- Input is validated at the API boundary (age/income/percentage ranges,
  message length limits) via Pydantic constraints.
- `CORS_ORIGINS` and `SEED_DATA_PATH` are environment-driven so the same
  images work locally, in docker-compose, and on a cloud host without code
  changes.

## Trust & safety principles

- Every scheme shows its source name, last-verified date, and an official
  URL — sourced only from structured data, never invented.
- Eligibility statuses are `likely_eligible` / `possibly_eligible` /
  `missing_information` / `not_matching` / `unable_to_determine` — never an
  arbitrary confidence percentage.
- Missing information is always asked for, never assumed (e.g. "I farm on
  my uncle's land" extracts `land_ownership: family`, not `owned`).
- No Aadhaar numbers, passwords, OTPs, or bank account numbers are ever
  collected.
- `GET /api/metrics` reports only actual measured counts from the local
  database — the app never fabricates user/impact numbers.
