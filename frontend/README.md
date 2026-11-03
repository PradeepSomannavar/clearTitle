<div align="center">
  <img width="220" alt="clearTitle logo" src="src/assets/clearTitle.png" />
  <h1>clearTitle — AI Property Title Verification</h1>
  <p><em>Deeds, ECs, e-Khatas &amp; audits — one tamper-proof place.</em></p>
</div>

<p align="center">
  <strong>Run your property business without the chaos.</strong><br />
  AI + Blockchain property title verification platform built in Belagavi, Karnataka.
</p>

## What it does

clearTitle automates Indian property due diligence end-to-end — from raw Kannada/Hindi land deeds to a cryptographic proof of ownership on-chain.

- **Intake & OCR** — Digital processing of Sale Deeds, Encumbrance Certificates (EC), e-Khata, and sanctioned layout plans.
- **VLM Analysis** — Vision-Language Models parse complex Indian-language & regional land terminology.
- **Trust Score & Red Flags** — Unified verification status highlighting Chain of Title, area discrepancies, and potential fraud risks.
- **Blockchain Layer** — Future-ready property tokenization with tamper-evident ownership & immutable transaction history on Polygon.

## Pages

| Route | What it is |
| ----- | ---------- |
| `/` | Landing page — hero, four-step pipeline, live audit demo, market & revenue, FAQ |
| `/#/app` | Verification Dashboard — upload PDFs, run the OCR pipeline, view results, run agentic verification, browse case history |

## Tech Stack

| Layer   | Technology |
| ------- | ---------- |
| Frontend| React 19, Vite 6, TypeScript, Tailwind CSS 4, lucide-react |
| Dev host| Express + tsx dev server (static/Vite middlewares only — no API routes) |
| AI      | Gemini 2.5 Flash / Groq fallback — called by the FastAPI backend |
| 3D/UI   | three.js (interactive hero background) |

## Getting Started

**Prerequisites:** Node.js 18+

1. Install dependencies:

   ```bash
   npm install
   ```

2. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

   - `FASTAPI_URL` — where the FastAPI backend lives (default `http://localhost:8000`). All real API traffic is proxied there.

3. Run the app (dev server with API + Vite HMR on port 3000):

   ```bash
   npm run dev
   ```

## Scripts

| Command        | Description                                        |
| -------------- | -------------------------------------------------- |
| `npm run dev`  | Start dev server (Express + Vite middleware) on :3000 |
| `npm run build`| Build the Vite frontend and bundle the Express server to `dist/` |
| `npm start`    | Run the production server from `dist/`             |
| `npm run lint` | Type-check the project with `tsc --noEmit`         |

> In the Docker deployment the built SPA is served by the FastAPI backend instead of this Express server.

## API

The Express server hosts **no API routes** — it is purely a dev/static host.
All endpoints live in the FastAPI backend (see the root `README.md`); in
development Vite proxies `/api`, `/auth`, `/health` and `/static` there
automatically (`.env.example` → `FASTAPI_URL`).

## Project Structure

```
├── src/
│   ├── components/      # Landing-page sections (Navbar, Hero, FAQ, ...)
│   ├── dashboard/       # Verification Dashboard — upload, results, report, history
│   ├── api/backend.ts   # API client used by the dashboard
│   ├── data/            # Static landing-page content
│   ├── pages/           # Home, How-It-Works, Pricing, Login, OCR viewer
│   ├── App.tsx          # Routes: homepage + /#/app dashboard
│   └── index.css        # Tailwind + brand fonts/gradients
├── public/              # Favicon & static assets
├── src/assets/          # Brand assets (logo PNG)
├── server.ts            # Express dev server (Vite middleware / static serving)
├── index.html
└── vite.config.ts
```

## UI Design System

- **Palette** — Cream `#FFF8F2`, stone neutrals, orange brand (`#ea580c`, `#f97316`, amber `#fbbf24`)
- **Fonts** — Inter (body), Plus Jakarta Sans (display), Instrument Serif (accent italics)
- **Icons** — lucide-react

## Deployment

```bash
npm run build
npm start
```
