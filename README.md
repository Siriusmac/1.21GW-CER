# 1.21GW-CER

Base tecnica per un portale web di gestione e monitoraggio di una Comunita Energetica Rinnovabile italiana.

Il progetto nasce come MVP: importa misure energetiche da CSV, normalizza i timestamp su `Europe/Rome`, calcola indicatori tecnici stimati e mostra una dashboard amministratore e membro. Tutti i risultati di calcolo sono etichettati come **stima tecnica non validata**: non sono calcoli ufficiali GSE.

## Stato per agenti futuri

Questo repository e nato da una repo GitHub inizialmente quasi vuota, con `PROJECT_BRIEF.md` come sorgente funzionale principale. La milestone 1 e stata implementata direttamente su `main` con una base MVP completa.

Stato attuale:

- branch di lavoro: `main`;
- remoto: `https://github.com/Siriusmac/1.21GW-CER.git`;
- credenziali Git locali: configurate sul repository tramite helper di GitHub Desktop (`git-credential-desktop`);
- ultima verifica nota: backend tests `17 passed`, frontend build Vite riuscita;
- API e dashboard usano dati demo in memoria, non ancora persistenza reale su database;
- database, modelli e migrazioni sono predisposti ma gli endpoint non leggono/scrivono ancora da PostgreSQL.

Regola operativa con l'utente:

- non fare push impliciti su `main`;
- se il messaggio chiede esplicitamente "fai push", "pusha su main" o equivalente, e consenso valido per quel turno;
- se il push da CLI fallisce, GitHub Desktop e gia stato usato con successo come fallback.

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

### Mappa codice

- [backend/app/main.py](/Users/simone/Documents/1.21GW-CER/backend/app/main.py): istanzia FastAPI, CORS e router.
- [backend/app/api/routes.py](/Users/simone/Documents/1.21GW-CER/backend/app/api/routes.py): endpoint MVP; oggi lavorano sui dati demo.
- [backend/app/services/demo_data.py](/Users/simone/Documents/1.21GW-CER/backend/app/services/demo_data.py): anagrafica CER e misure usate dalla dashboard.
- [backend/app/services/importer.py](/Users/simone/Documents/1.21GW-CER/backend/app/services/importer.py): parsing CSV, timezone, DST, granularita e validazione righe.
- [backend/app/services/calculation.py](/Users/simone/Documents/1.21GW-CER/backend/app/services/calculation.py): motore puro di calcolo energetico ed economico.
- [backend/alembic/versions/0001_initial_schema.py](/Users/simone/Documents/1.21GW-CER/backend/alembic/versions/0001_initial_schema.py): schema iniziale database.
- [frontend/src/main.jsx](/Users/simone/Documents/1.21GW-CER/frontend/src/main.jsx): dashboard React admin/membro.
- [data/sample/energy_readings.csv](/Users/simone/Documents/1.21GW-CER/data/sample/energy_readings.csv): CSV valido di esempio.

### Regole del motore di calcolo

- I timestamp importati vengono normalizzati su `Europe/Rome`.
- Gli intervalli sono aggregati internamente in UTC, per non fondere le due ore locali duplicate nel passaggio da ora legale a ora solare.
- Timestamp locali ambigui o inesistenti durante i cambi ora vengono rifiutati se non includono un offset esplicito.
- Sono accettati intervalli orari e quartorari.
- Per evitare doppio conteggio nello stesso POD e timestamp:
  - lato produzione, `grid_injection` prevale su `production` quando entrambe sono presenti;
  - lato domanda, `consumption` prevale su `grid_withdrawal` quando entrambe sono presenti;
  - righe duplicate della stessa direzione vengono sommate.
- Gli output restano sempre marcati come `stima tecnica non validata`.

### Casi gia coperti dai test

- produzione maggiore dei consumi;
- consumi maggiori della produzione;
- dati mancanti per un intervallo;
- POD multipli nello stesso timestamp;
- valori negativi o anomali;
- timestamp duplicati;
- normalizzazione `Europe/Rome`;
- cambio ora legale/solare, incluse ore locali inesistenti o ambigue;
- assenza di doppio conteggio tra misure tecniche alternative.

### Decisioni da preservare

- `production` e `grid_injection` non vanno sommati automaticamente nello stesso POD/intervallo: se esiste `grid_injection`, viene usata come produzione condivisibile stimata.
- `consumption` e `grid_withdrawal` non vanno sommati automaticamente nello stesso POD/intervallo: se esiste `consumption`, viene usato come consumo lato membro.
- Duplicati della stessa direzione nello stesso POD/intervallo sono sommati, per supportare file spezzati o righe parziali.
- L'aggregazione temporale interna e in UTC, l'output torna in `Europe/Rome`.
- Timestamp senza offset sono ammessi solo se non cadono in un'ora locale ambigua o inesistente.
- La ripartizione benefici oggi e semplificata: percentuali fisse oppure proporzionale ai consumi.
- Non implementare logiche GSE definitive senza una milestone dedicata.
- Non introdurre integrazioni reali con GSE, distributori o API proprietarie in questa fase.

### Debito tecnico intenzionale

- Gli endpoint usano `DEMO_COMMUNITY` e `DEMO_READINGS`; il collegamento a PostgreSQL e il prossimo passaggio naturale.
- L'autenticazione e solo predisposta a livello concettuale; mancano utenti, sessioni e autorizzazioni reali.
- Import XLSX e fonti ufficiali sono solo predisposizioni, non implementazioni.
- Il limite anomalo `MAX_ENERGY_KWH = 1_000_000` e una guardrail tecnica provvisoria, da sostituire con soglie configurabili per POD/impianto.
- La dashboard e operativa ma non ancora coperta da test UI automatici.
- Il filtro giorno/mese/anno nel frontend e presente come controllo, ma solo l'intervallo personalizzato invia date esplicite al backend.

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
6. Rendere configurabili soglie anomale e granularita accettate.
7. Aggiungere test API e test frontend essenziali.
