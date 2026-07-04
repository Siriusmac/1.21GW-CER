# 1.21GW-CER

Base tecnica per un portale web di gestione e monitoraggio di una Comunita Energetica Rinnovabile italiana.

Il progetto nasce come MVP: importa misure energetiche da CSV, normalizza i timestamp su `Europe/Rome`, calcola indicatori tecnici stimati e mostra una dashboard amministratore e membro. Tutti i risultati di calcolo sono etichettati come **stima tecnica non validata**: non sono calcoli ufficiali GSE.

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL, compatibile con TimescaleDB
- Frontend: React, Vite, Recharts
- Container: Docker Compose
- Test: pytest sul motore di calcolo

## Avvio rapido

```bash
docker compose up --build
```

Servizi:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- OpenAPI: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## Backend locale

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend locale

```bash
cd frontend
npm install
npm run dev
```

## CSV di esempio

Un file valido deve contenere:

```csv
timestamp,pod_id,energy_kwh,direction
2026-01-01T00:00:00+01:00,POD-CONS-001,12.4,consumption
2026-01-01T00:00:00+01:00,POD-PROD-001,8.1,production
```

Esempi disponibili in [data/sample/energy_readings.csv](/Users/simone/Documents/1.21GW-CER/data/sample/energy_readings.csv).

## Endpoints principali

- `GET /health`: stato API
- `GET /api/v1/cer`: anagrafica demo CER
- `POST /api/v1/import/csv`: validazione e import CSV
- `GET /api/v1/dashboard/admin`: indicatori aggregati admin
- `GET /api/v1/dashboard/member/{member_id}`: vista membro
- `GET /api/v1/reports/monthly`: riepilogo mensile JSON
- `GET /api/v1/config/economics`: parametri economici correnti

## Scelte architetturali

- `models`: schema database iniziale, pronto per PostgreSQL standard e TimescaleDB.
- `schemas`: contratti API e validazione Pydantic.
- `services/importer.py`: validazione CSV, timezone e granularita.
- `services/calculation.py`: motore di calcolo puro e testabile.
- `services/demo_data.py`: seed in memoria usato dalla prima milestone.
- `core/config.py`: parametri economici e granularita configurabili via variabili ambiente.

La prima milestone evita hardcoding di regole GSE definitive: l'incentivo e la granularita sono parametri, e le integrazioni ufficiali sono lasciate a provider futuri.

## Test

```bash
cd backend
pytest
```

## Prossimi passi consigliati

1. Collegare gli endpoint al database invece dei dati demo in memoria.
2. Aggiungere autenticazione reale e ruoli.
3. Implementare import XLSX.
4. Aggiungere export PDF/XLSX per la reportistica.
5. Introdurre connector separati per fonti ufficiali quando disponibili.
