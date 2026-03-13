# Research Journal Finder & ETL

A full-stack web application designed to process, search, and filter academic journals based on SCImago Journal Rank (SJR) and Web of Science (WoS) metrics.

## 🚀 Features
- **ETL Pipeline:** Combine and clean massive `.csv` datasets (SJR & WoS) into a local SQLite database (`output/journals.db`).
- **REST API:** High-performance FastAPI back-end with Swagger UI and filtering logic.
- **Modern UI:** Clean React/Vite/Tailwind front-end featuring dynamic filtering by **Subject**, **Rank**, **Publishers**, and direct links to search for the official websites.

## 🛠️ Tech Stack
- **Backend:** Python 3, Pandas, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React (Vite), Tailwind CSS, Axios, Lucide React

---

## 💻 Setup Instructions

### 1. Build DB & Start Backend
Open terminal at the root directory:

```bash
# Install Python dependencies
pip install -r requirements.txt

# 1. Run the ETL Pipeline (Generates output/journals.db using files in data/)
python src/pipeline/etl_pipeline.py

# 2. Start the Backend API Server (Runs on http://localhost:8000)
uvicorn src.api.main:app --reload
```

### 2. Start Frontend
Open a **new terminal window** at the root directory:

```bash
cd frontend
npm install
npm run dev
# Vite will start on http://localhost:5173
```

## 🌐 API Documentation
With the backend running, view the interactive API Documentation at:
👉 `http://127.0.0.1:8000/docs`