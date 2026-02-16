# Architecture Overview:


## Repository Structure

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
