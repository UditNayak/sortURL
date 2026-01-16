# Setup & Local Development

This document explains how to set up the project locally, manage environment variables, and run the application.



## 📁 Prerequisites

- Python **3.9+**
- `pip`
- `git`

Verify Python:

```bash
python --version
```

## 🐍 Virtual Environment Setup
Create and activate a virtual environment in the project root:

```bash
python -m venv venv
source venv/bin/activate     # macOS / Linux
# venv\Scripts\activate      # Windows
```

Upgrade pip (recommended):

```bash
pip install --upgrade pip
```

## 📦 Install Dependencies
Install backend dependencies:

```bash
pip install -r src/requirements.txt
```

## 🔐 Environment Variables

The project uses **environment-based configuration**.
No values are hardcoded in the source code.

### Environment File
| File              | Purpose                         | Git         |
| ----------------- | ------------------------------- | ----------- |
| `.env.example`    | Template for required variables | ✅ Committed |
| `.env.local`      | Local development config        | ❌ Ignored   |
| `.env.production` | Production config               | ❌ Ignored   |
| `.env.test`       | Test config (optional)          | ❌ Ignored   |

### Create Local Environment File

Copy the example file:
```bash
cp .env.example .env.local
```
Edit `.env.local` as needed.

## 🗄 Database Location
- SQLite database is created automatically
- Default location: `data/url_shortener.db`
The `data/` directory is ignored by git and used only for runtime files.

## ▶️ Running the Application
From the project root:
```bash
uvicorn src.main:app --reload
```

Server will start at:
```
http://localhost:8001
```

## 🩺 Health Checks

Verify the application is running:
```bash
curl http://localhost:8001/api/health
curl http://localhost:8001/api/ready
```

## 🧪 Notes
- `.env.local` is loaded automatically at startup
- Production deployments should use `.env.production`
- Never commit real secrets
- Database file is created on first run