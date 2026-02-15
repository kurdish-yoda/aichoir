![AI Choir Hero](./public/hero-screenshot.png)

# AI Choir

AI Choir is an AI integration agency that works alongside businesses to surgically automate the right parts of their workflow — not everything, just the parts where AI removes friction without sacrificing the human touch that matters.

## What We Do

We identify exactly where AI saves your team time, then build and integrate the tools to make it happen. That means custom automations, internal tooling, and AI-assisted workflows — built scalpel-precise for your specific operation.

## This Repository

This is the agency's public-facing landing site, built with React, TypeScript, and Vite. It also includes an internal **Court Search** tool — a Florida and New York civil court records lookup used for lending due diligence.

### Tech Stack

- **React 19** + **TypeScript** + **Vite**
- **GSAP** — scroll-driven and entrance animations
- **Lenis** — smooth scrolling
- **Flask** (Python) — backend API for the Court Search tool
- **Playwright** — headless browser automation for scraping public court portals
- **Deployed on Render**

### Getting Started

**Frontend**
```bash
npm install
npm run dev
```

**Backend**
```bash
conda activate aichoir
cd backend
pip install -r requirements.txt
playwright install chromium
python app.py
```

See `architectureplan.md` for the full integration architecture.
