# Ethara AI – Inventory & Order Management System

Simplified Inventory & Order Management System with:
- **Backend**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: React (Vite) served via Nginx
- **Business rules**: unique product SKUs, unique customer emails, inventory validation, auto stock reduction on order placement
- **Containerized**: Docker + Docker Compose
- **Tests**: pytest + Testcontainers (runs against real PostgreSQL)

## Architecture
- Frontend served on `http://localhost:8080`
- Frontend proxies `/api/*` → backend (`backend:8000`)
- Backend connects to PostgreSQL (`db:5432`)

## Run locally (Docker)
1. Create env file:
   ```bash
   cp .env.example .env
   ```
2. Start everything:
   ```bash
   docker compose up --build
   ```
   If this errors, ensure **Docker Desktop / Docker daemon is running**.
3. Open:
   - UI: `http://localhost:8080`
   - API: `http://localhost:8000/healthz`

## Run Docker images directly (Docker Hub)
Backend:
```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="<YOUR_POSTGRES_DATABASE_URL>" \
  pranjalvashisth/ethara-oms-backend:latest
```

Frontend (point it to your backend URL):
```bash
docker run --rm -p 8080:8080 \
  -e API_UPSTREAM="http://host.docker.internal:8000" \
  pranjalvashisth/ethara-oms-frontend:latest
```
If your backend is deployed, set `API_UPSTREAM` to the public origin, e.g. `https://your-backend.example.com`.

## Run locally (without Docker)
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://ethara:ethara_password_change_me@localhost:5432/ethara_oms"
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend dev server proxies `/api` to `http://localhost:8000` via `frontend/vite.config.ts`.

## API Endpoints
- `GET /api/products`
- `POST /api/products`
- `PATCH /api/products/{id}`
- `DELETE /api/products/{id}`
- `GET /api/customers`
- `POST /api/customers`
- `PATCH /api/customers/{id}`
- `DELETE /api/customers/{id}`
- `GET /api/orders`
- `POST /api/orders` (validates stock & reduces inventory)
- `GET /api/orders/{id}`

## Run tests
Default tests run on SQLite (no Docker required). Optional integration tests use Testcontainers to spin up PostgreSQL.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

PostgreSQL integration tests (requires Docker daemon):
```bash
cd backend
source .venv/bin/activate
RUN_INTEGRATION=1 pytest -q -m integration
```

## Deployment (free platforms)
This repo is ready to deploy using free tiers:
- Backend: Render / Fly.io / Railway (PostgreSQL add-on required)
- Frontend: Netlify / Vercel (or deploy the Nginx container)

For submission, provide:
- GitHub repo link
- Docker Hub image links (build & push `backend` and `frontend`)
- Public URLs for hosted frontend and backend API

## Submission (my accounts)
GitHub user: `PranjalVashisth`  
Docker Hub user: `pranjalvashisth`

Suggested repo/image names (used below):
- GitHub repo: `ethara-inventory-oms`
- Backend image: `pranjalvashisth/ethara-oms-backend:latest`
- Frontend image: `pranjalvashisth/ethara-oms-frontend:latest`

Links to paste in the Google Form (after you create/push them):
- GitHub: `https://github.com/PranjalVashisth/ethara-inventory-oms`
- Docker Hub (backend): `https://hub.docker.com/r/pranjalvashisth/ethara-oms-backend`
- Docker Hub (frontend): `https://hub.docker.com/r/pranjalvashisth/ethara-oms-frontend`
