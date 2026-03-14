# Architecture Overview

## System Components
1. Data Collectors (Python)
2. Scoring Engine (Python)
3. Database (PostgreSQL)
4. API (FastAPI)
5. Frontend (Next.js)

## Data Flow
User Request → API → Check Cache → Collectors → Scoring → Database → Response

## Tech Stack
- Backend: Python 3.11 + FastAPI
- Database: PostgreSQL 15
- Cache: Redis (later)
- Frontend: Next.js 14
- Hosting: Railway (backend), Vercel (frontend)