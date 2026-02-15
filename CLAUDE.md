# CLAUDE.md — AI Choir + CourtSearch

This is the project context file for AI coding agents working on this codebase.

---

## What This Project Is

A dark, minimal agency landing page (AI Choir) with an integrated Court Search tool. The Court Search page allows internal users to run a Florida/NY civil court records lookup by name, powered by a Python Flask backend and the `CourtSearch/` scraper package.

The project is deployed as a single unit on Render: Flask serves the built React frontend and handles all `/api` routes.

---

## Repository Layout

```
aichoir/
├── components/               # Landing page React components (do not modify for CourtSearch work)
├── pages/
│   └── CourtSearchPage.tsx   # Court Search UI page
├── CourtSearch/              # Python scraper package — DO NOT MODIFY
│   ├── scrapers/             # Scraper classes (MiamiDade, Broward, NewYork)
│   ├── court_lookup.py       # CLI entrypoint (not used by backend)
│   └── requirements.txt      # CourtSearch-specific deps (use backend/requirements.txt instead)
├── backend/
│   ├── app.py                # Flask app — serves React + handles /api routes
│   └── requirements.txt      # Flask + all CourtSearch dependencies combined
├── App.tsx                   # React entry, Router, routes
├── vite.config.ts            # Vite config, /api proxy for dev
├── package.json
└── CLAUDE.md                 # This file
```

---

## Tech Stack

### Frontend
- **React 19** + **TypeScript**
- **Vite** (dev server + build)
- **GSAP 3** — all animations (`gsap`, `gsap/ScrollTrigger`)
- **Lenis** — smooth scroll (`@studio-freight/lenis`)
- **React Router DOM** — client-side routing
- **Tailwind CSS** (via CDN in index.html, utility classes throughout)

### Backend
- **Flask 3** — Python web framework
- **threading** — background job execution (no Celery/Redis)
- **CourtSearch scrapers** — imported directly from `../CourtSearch/scrapers`
- **Playwright** — headless Chromium for JavaScript-rendered court portals

---

## Design System

Always match the existing landing page aesthetic on any new UI work.

| Token | Value | Usage |
|---|---|---|
| Background | `#0E1117` | Page/section backgrounds |
| Primary text | `#E2DFD8` | Headlines, labels, active elements |
| Muted text | `#7A7D85` | Body copy, descriptions |
| Subtle text | `#4A4D55` | Micro-labels, secondary info |
| Border | `border-[#E2DFD8]/20` | Card borders, dividers |
| Accent glow | `rgba(226,223,216,0.08)` | Hover states, card fills |

**Fonts:**
- `font-['Syne']` — headlines, large text
- `font-['Inter']` — body copy, buttons
- `font-['JetBrains_Mono']` — labels, status text, code-like elements

**Animation patterns:**
- Entrance: `gsap.fromTo(el, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 1, ease: 'power2.out' })`
- Stagger lists: add `stagger: 0.08` to the vars
- ScrollTrigger: `trigger: el, start: 'top 80%'`
- Always use `useRef` + `useEffect` for GSAP, never inline styles

**Component pattern:**
```tsx
const MyComponent: React.FC = () => {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    gsap.fromTo(ref.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1 });
  }, []);

  return <section ref={ref}>...</section>;
};

export default MyComponent;
```

---

## Flask Backend

### Running locally
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
python app.py
# Runs on http://localhost:5001
```

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/search` | Start a search job. Body: `{ first_name, last_name, middle_name?, date_of_birth? }`. Returns `{ job_id }`. |
| `GET` | `/api/status/<job_id>` | Poll job status. Returns `{ status: "running"\|"complete"\|"error", message }`. |
| `GET` | `/api/results/<job_id>` | Fetch results. Returns full `get_api_response()` JSON. Only valid when status is `"complete"`. |

### Importing the scraper
```python
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'CourtSearch'))
from scrapers import SearchCriteria, search_court_records, get_api_response
```

### Job store
Simple in-memory dict — sufficient for internal single-user use:
```python
jobs = {}  # { job_id: { status, message, result, error } }
```

---

## Frontend Dev Server
```bash
npm install
npm run dev
# Runs on http://localhost:5173
# /api/* is proxied to Flask at :5001 (see vite.config.ts)
```

## Production Build
```bash
npm run build
# Output: dist/
# Flask's catch-all route serves dist/index.html for all non-API paths
```

---

## Routing

React Router is used. Two routes:
- `/` → Landing page (all existing components)
- `/court-search` → CourtSearchPage

The Navbar has a "Court Search" link using React Router `<Link>`.

Flask's catch-all serves `dist/index.html` for all routes so React Router handles client-side navigation in production.

---

## Deploying to Render

**Service type:** Web Service (not Static Site)

**Build command:**
```bash
npm install && npm run build && pip install -r backend/requirements.txt && playwright install chromium
```

**Start command:**
```bash
python backend/app.py
```

**Environment variables:**
- `PORT` — set automatically by Render, Flask reads it
- `FLASK_ENV=production`

Flask binds to `0.0.0.0:$PORT` in production.

---

## Key Rules for This Codebase

1. **Do not modify anything in `CourtSearch/`** — it's a standalone package. Import it, don't change it.
2. **All new UI must match the design system above.** No new colors, no new fonts.
3. **GSAP for all animations** — no CSS transitions for entrance animations (they won't respect Lenis scroll).
4. **The search takes minutes** — never make a synchronous HTTP request that waits for results. Always use the job/poll pattern.
5. **Flask runs on port 5001 in dev** to avoid macOS AirPlay conflict on 5000 and Vite on 5173.
6. **`dist/` is gitignored** — it's generated by `npm run build`, not committed.

---

## CourtSearch Package — Quick Reference

```python
from scrapers import SearchCriteria, search_court_records, get_api_response

criteria = SearchCriteria(
    first_name="John",        # required
    last_name="Doe",          # required
    middle_name="Q",          # optional, helps disambiguate
    date_of_birth="01/01/1980",  # optional, MM/DD/YYYY
    county=None               # None = search all jurisdictions
)

cases = search_court_records(criteria)       # List[CourtCase], takes 1-3 minutes
response = get_api_response(cases, criteria) # JSON-serializable dict
```

The `response` dict shape is documented in `CourtSearch/README.md`.

Scrapers: MiamiDadeScraper, BrowardScraper, NewYorkScraper. All use Playwright headless Chromium.
