# shortURL — URL Shortener

A production-ready URL shortener built with **Python**, **FastAPI**, **Jinja2 templates**, and **SQLite**.

The project focuses on simplicity, clean architecture, and zero heavy frontend frameworks while still providing a modern UI and robust backend features.



## ✨ Features

### Core Functionality
- Shorten long URLs with random or custom aliases
- Redirect using short codes (302 redirects)
- Track click counts and analytics
- Optional user authentication
- Anonymous URL shortening supported

### Technical Highlights
- FastAPI backend
- Jinja2 templates (no React / no frontend frameworks)
- SQLite (file-based, zero setup)
- Tailwind CSS via CDN
- Health & readiness endpoints (production-friendly)



## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 Templates
- **Database**: SQLite
- **Styling**: Tailwind CSS
- **Auth**: JWT (optional)
- **Runtime**: Uvicorn



## 🚀 Quick Start (Local)

```bash
# Clone the repository
git clone <repo-url>
cd shortURL

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Create env file
cp .env.example .env.local

# Run the application
uvicorn src.main:app --reload
```

The application will be available at:
    ```
    http://localhost:8001
    ```


## 📚 Documentation
Detailed documentation is split into small, focused files:

- **Setup & Environment →** [docs/setup.md](docs/setup.md)
- **API Endpoints & Usage →** [docs/api.md](docs/api.md)
- **Project Structure →** [docs/structure.md](docs/structure.md)


## 🩺 Health Endpoints

- `/api/health` — Liveness probe
- `/api/ready` — Readiness probe