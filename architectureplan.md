# Architecture Plan: CourtSearch Integration

## Overview

Add a Court Search page to the existing AI Choir landing site. The page will match the existing dark, GSAP-animated aesthetic, and connect to a Flask Python backend that runs the existing CourtSearch scraper. The whole project will be deployed as one unit on Render.

---

## Repository Structure (after integration)

```
aichoir/
├── components/               # Existing landing page components (untouched)
├── pages/
│   └── CourtSearchPage.tsx   # New Court Search page (React)
├── CourtSearch/              # Existing Python scraper package (untouched)
│   ├── scrapers/
│   ├── court_lookup.py
│   └── requirements.txt
├── backend/
│   ├── app.py                # Flask app (new)
│   └── requirements.txt      # Flask + all CourtSearch deps combined (new)
├── App.tsx                   # Add routing / page switching
├── index.tsx
├── index.html
├── vite.config.ts            # Add /api proxy for dev
├── package.json              # Add react-router-dom
├── tsconfig.json
├── CLAUDE.md
└── architectureplan.md
```

---

## Frontend Changes

### 1. Add React Router
```bash
npm install react-router-dom
```

Wrap `App.tsx` in `<BrowserRouter>`. Add two routes:
- `/` → existing landing page (all current components unchanged)
- `/court-search` → new `CourtSearchPage`

### 2. CourtSearchPage.tsx (`pages/CourtSearchPage.tsx`)
Matches landing page design exactly:
- Background: `#0E1117`
- Fonts: Syne (headings), Inter (body), JetBrains Mono (labels/status)
- Color tokens: `#E2DFD8` (primary text), `#7A7D85` (muted), `#4A4D55` (subtle)
- Border style: `border-[#E2DFD8]/20`
- Animations: GSAP for entrance, loading state, results reveal

**Page sections:**
1. **Header** — page title + disclaimer badge (same style as landing labels)
2. **Search Form** — First Name*, Last Name*, Middle Name (optional), DOB (optional)
   - Input styling to match landing page button/border aesthetic
   - Submit triggers POST `/api/search`
3. **Loading State** — animated progress bar + live status polling text
   - JetBrains Mono log lines ticking through: "Searching Miami-Dade...", "Searching Broward...", etc.
   - GSAP-animated pulsing indicator
4. **Results Panel** — cards per case, styled like the Process/Stats components
   - Open cases highlighted (accent color or border glow)
   - Summary bar at top (total / open / closed counts)
   - Disclaimer footer

### 3. Navbar update
Add a "Court Search" link to the Navbar component. Use React Router `<Link>` rather than an anchor tag.

### 4. Vite proxy config (`vite.config.ts`)
Forward `/api/*` to Flask during development to avoid CORS:
```ts
server: {
  proxy: {
    '/api': 'http://localhost:5001'
  }
}
```

---

## Backend

### Flask app (`backend/app.py`)

Three endpoints:

#### `POST /api/search`
- Accepts JSON: `{ first_name, last_name, middle_name?, date_of_birth? }`
- Validates inputs
- Starts scraper in a background thread (Python `threading.Thread`)
- Returns immediately: `{ job_id: "uuid4" }`

#### `GET /api/status/<job_id>`
- Returns: `{ status: "running" | "complete" | "error", message: "..." }`
- `message` is the current county being searched (updated by scraper callbacks)

#### `GET /api/results/<job_id>`
- Returns the full `get_api_response()` JSON from CourtSearch
- Only valid once status is `"complete"`

**Job management:** Simple in-memory dict `jobs = {}` keyed by UUID. Sufficient for single-user/internal tool use. Not thread-safe at scale but fine for this use case.

**Flask serves the built React frontend:**
```python
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join('dist', path)):
        return send_from_directory('dist', path)
    return send_from_directory('dist', 'index.html')
```

Flask runs on port 5001 in development, port from `$PORT` env var on Render.

### `backend/requirements.txt`
Combines Flask + all CourtSearch dependencies:
```
flask>=3.0.0
flask-cors>=4.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
playwright>=1.40.0
tabulate>=0.9.0
python-dateutil>=2.8.0
playwright-stealth>=1.0.6
```

---

## Data Flow (Runtime)

```
User fills form
    │
    ▼
POST /api/search  →  Flask creates job_id, starts background thread
    │                  Thread: calls search_court_records(criteria)
    ▼
Frontend polls GET /api/status/<job_id> every 3 seconds
    │                  (shows which county is being searched)
    ▼ (status = "complete")
GET /api/results/<job_id>  →  Returns full CourtCase JSON
    │
    ▼
React renders results cards with GSAP entrance animation
```

---

## Local Development Workflow

```bash
# Terminal 1 — Frontend (hot reload)
npm run dev

# Terminal 2 — Backend
cd backend
pip install -r requirements.txt
playwright install chromium
python app.py

# Visit: http://localhost:5173
# /api/* proxied to Flask at :5001
```

---

## Production Build & Deploy Workflow

```bash
# Build frontend static files
npm run build
# Output: dist/

# Then Flask serves dist/ + handles /api routes
python backend/app.py
```

### Render Deployment

**Platform:** Render Web Service (not static site)

**Build command:**
```bash
npm install && npm run build && pip install -r backend/requirements.txt && playwright install chromium
```

**Start command:**
```bash
python backend/app.py
```

**Environment variables on Render:**
- `PORT` — set automatically by Render
- `FLASK_ENV=production`

**Migration from Vercel:**
- Remove the project from Vercel
- Point domain DNS to Render

---

## Key Constraints & Decisions

| Decision | Rationale |
|---|---|
| Background threads (not Celery) | Simpler, no Redis dependency. Fine for single-user internal tool. |
| In-memory job store | No persistence needed. Jobs are ephemeral — start search, get results, done. |
| React Router over plain state toggle | Gives the Court Search page its own URL, bookmarkable, cleaner code |
| Keep CourtSearch/ directory unchanged | It already has a clean `get_api_response()` API. No need to modify it. |
| Flask on port 5001 in dev | Avoids conflict with Vite's 5173 and common 5000 AirPlay conflict on macOS |
| Flask serves `dist/` in production | One process, no separate static host. Simple Render deployment. |

---

## Files to Create

| File | Action |
|---|---|
| `pages/CourtSearchPage.tsx` | Create new |
| `backend/app.py` | Create new |
| `backend/requirements.txt` | Create new |
| `vite.config.ts` | Edit — add proxy |
| `App.tsx` | Edit — add Router + routes |
| `components/Navbar.tsx` | Edit — add Court Search link |
| `package.json` | Edit — add react-router-dom |

---

## Files Not To Touch

- `CourtSearch/` — entire directory stays as-is
- All existing `components/*.tsx` — landing page is untouched except Navbar
- `index.html`, `index.tsx`, `tsconfig.json` — no changes needed
