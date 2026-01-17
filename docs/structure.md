# Project Structure

This document explains the organization of the `shortURL` project and the purpose of each folder/file.

---

## Root Directory

```
shortURL/
├── .gitignore                     # Git ignore rules
├── .env.example                   # Template env file (committed)
├── .env.local                     # Local env (ignored)
├── .env.production                # Production env (ignored)
├── .env.test                      # Test environment variables
│
├── pytest.ini                     # Pytest configuration
│
├── data/                          # Runtime data (ignored)
│   └── test.db                    # SQLite test database (auto-created)
│
├── docs/                          # Project documentation
│   ├── setup.md                   # Setup & local development guide
|   ├── test.md                    # Testing guide
│   ├── api.md                     # API endpoints & usage
│   └── structure.md               # Project structure explanation
│
├── src/                           # Main application source code
│
├── tests/                         # Test suite
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_services.py
│   ├── test_utils.py
│
├── README.md                      # Entry-point documentation
└── venv/                          # Virtual environment (ignored)

```

## `src/` Directory

```
src/
├── main.py # Application entry point
├── config.py # Environment configuration management
├── database.py # Database initialization & connection helpers
│
├── models/ # Data models
│   └── schemas.py # Pydantic models for request/response validation
│
├── routers/ # FastAPI route definitions
│   ├── auth.py # Authentication endpoints
│   ├── urls.py # URL shortening & management endpoints
│   ├── health.py # Health & readiness endpoints
│   └── pages.py # Template rendering pages
│
├── services/ # Business logic
│   ├── auth_service.py # Authentication logic
│   └── url_service.py # URL shortening logic
│
├── utils/ # Utility modules
│   ├── password.py # Password hashing helpers
│   ├── jwt_handler.py # JWT token helpers
│   └── short_code.py # Random/custom short code generation
│
├── templates/ # Jinja2 templates
│   ├── base.html # Base layout with navigation
│   ├── index.html # Homepage with URL shortening form
│   ├── dashboard.html # Analytics dashboard
│   ├── login.html # Login page
│   └── signup.html # Signup page
│
└── requirements.txt # Python dependencies
```


## `docs/` Directory

- `setup.md` — Instructions to set up local dev, virtual environments, and run the app
- `api.md` — Details of all API endpoints, request/response examples, and usage
- `structure.md` — This file: explains folders and responsibilities

---

## Key Notes

- **`data/`**: Stores the runtime SQLite database; ignored by git.
- **`src/config.py`**: Loads `.env` files, manages all configurable settings.
- **`routers/`**: All API endpoints are grouped here.
- **`services/`**: Core logic separated from routes for maintainability.
- **`utils/`**: Reusable helper functions (passwords, JWT, codes).
- **`templates/`**: All frontend pages are rendered with Jinja2; no JS frameworks required.
- **`main.py`**: Entry point that starts FastAPI.
- **`docs/`**: Contains focused, modular documentation instead of a giant README.
