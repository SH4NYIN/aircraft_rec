# AircraftRec — Plane Spotting Tracker

A web application for aviation photography enthusiasts (plane spotters) to record and manage photographed aircraft across airlines. Special livery aircraft are pinned to the top, and spotted/unspotted status is clear at a glance.

Built with DeepSeek V4.0 Pro (Vibe coding is awesome)

## Features

- **Airline Browser** — list view + country filter + spotting progress bar
- **Fleet View** — special livery aircraft pinned & highlighted, standard fleet sorted by registration
- **Collection Tracker** — spotted aircraft shown in full color, unspotted grayed out (`grayscale`)
- **One-Click Toggle** — mark aircraft as spotted directly from the fleet page
- **Photo Upload** — replace default web images with your own shots (JPEG/PNG/WebP)
- **Search** — fuzzy search by registration or aircraft type
- **Stats** — total spotted, special livery collection progress, airline coverage

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Backend | Python 3.13 + FastAPI | Async web framework with built-in Swagger |
| Database | SQLite | Zero setup, included in Python standard library |
| ORM | SQLAlchemy 2.0 | Relational mapping with SQLite support |
| Frontend | Jinja2 + Vanilla JS + CSS | Server-side rendering, no Node required |
| Server | Uvicorn | ASGI server |

## Quick Start

### Requirements

- Python 3.10+

### Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the dev server
python main.py
```

Open **http://localhost:8000** in your browser.

- Home → Airline list → click an airline to view its fleet
- Each aircraft card has a "Mark Spotted" button at the bottom
- After marking, a photo upload prompt appears automatically

### Screenshots

Coming soon

## Project Structure

```
avi-rec/
├── main.py                     # FastAPI application entry point
├── database.py                 # Database models & connection
├── seed_data.py                # Seed data import script
├── requirements.txt            # Python dependencies
├── prd.md                      # Product requirements document
├── templates/
│   ├── base.html               # Base layout
│   ├── index.html              # Home page
│   ├── airlines.html           # Airline list
│   ├── airline_detail.html     # Airline fleet view
│   ├── aircraft_detail.html    # Aircraft detail view
│   └── search.html             # Search page
├── static/
│   ├── css/style.css           # Stylesheet
│   └── js/app.js               # Client-side logic
└── uploads/                    # User-uploaded photos (.gitignore)
```

## Roadmap

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | China Southern MVP (current) | 🚧 In Progress |
| Phase 2 | Guangzhou airlines expansion (Air China, China Eastern, Hainan Airlines, etc.) | 📋 Planned |
| Phase 3 | Foreign airlines + PWA support | 📋 Planned |

## Data Notes

Fleet data is manually curated from official airline sources. The SQLite database file is not included in the repository — it is generated locally on first run.
