Devi creare la base tecnica di un portale web per la gestione e il monitoraggio di una Comunità Energetica Rinnovabile italiana.

Obiettivo del progetto:
Realizzare un MVP che consenta di caricare dati di consumo e produzione energetica, normalizzarli tramite timestamp, calcolare produzione, consumo, energia condivisa stimata e indicatori economici preliminari, e visualizzare tutto in una dashboard web.

Contesto:
Il portale dovrà distinguere chiaramente tra:

1. dati tecnici stimati/non validati, provenienti da CSV, XLSX, inverter, datalogger o smart meter;
2. dati ufficiali/validati, che in una fase successiva potranno essere importati da fonti GSE, distributori o altri portali.

Per ora non implementare integrazioni reali con GSE, distributori o API proprietarie. Predisponi però un’architettura modulare che permetta di aggiungerle in seguito.

Stack tecnico richiesto:

* Backend: Python con FastAPI.
* Database: PostgreSQL, predisposto per TimescaleDB ma funzionante anche come PostgreSQL standard.
* Frontend: React con Vite.
* Grafici: libreria frontend adeguata per serie temporali, ad esempio Recharts o equivalente.
* Autenticazione: struttura predisposta per ruoli utente, anche se nella prima versione può essere semplificata.
* Containerizzazione: Docker Compose per avviare backend, frontend e database.
* Migrazioni database: Alembic o soluzione equivalente.
* Testing: predisporre almeno test minimi sul motore di calcolo.

Funzionalità MVP:

1. Gestione anagrafica CER:
    * comunità energetica;
    * membri;
    * POD;
    * impianti di produzione;
    * ruolo del membro: consumer, producer, prosumer;
    * potenza impianto;
    * riferimento alla cabina primaria o area convenzionale;
    * regola di ripartizione benefici, per ora semplice e parametrica.
2. Import dati:
    * endpoint per caricare file CSV;
    * predisposizione successiva per XLSX;
    * struttura dati minima: timestamp, pod_id, energy_kwh, direction.
    * direction può essere:
        * consumption;
        * production;
        * grid_withdrawal;
        * grid_injection.
    * validazione del timestamp;
    * normalizzazione timezone Europe/Rome;
    * gestione di dati orari o quartorari;
    * segnalazione errori per righe non valide.
3. Motore di calcolo:
    Per ogni intervallo temporale calcolare:
    * produzione totale;
    * consumo totale;
    * energia condivisa stimata = minimo tra produzione immessa/condivisibile e consumi della configurazione nello stesso intervallo;
    * autoconsumo virtuale stimato;
    * percentuale di condivisione;
    * incentivo stimato configurabile in €/kWh;
    * valore economico stimato;
    * ripartizione semplificata tra membri secondo percentuale o criterio proporzionale ai consumi.
    Nota importante:
    Il calcolo deve essere etichettato come “stima tecnica non validata” e non come calcolo ufficiale GSE.
4. Dashboard amministratore:
    * produzione totale;
    * consumo totale;
    * energia condivisa stimata;
    * incentivo stimato;
    * grafico temporale produzione/consumo/energia condivisa;
    * tabella membri con consumi, quota energia condivisa e beneficio stimato;
    * filtri per periodo: giorno, mese, anno, intervallo personalizzato.
5. Dashboard membro:
    * vista semplificata del singolo membro;
    * consumo nel periodo;
    * quota stimata di energia condivisa;
    * beneficio economico stimato;
    * grafico storico.
6. Reportistica:
    * endpoint backend che restituisce riepilogo JSON mensile;
    * predisposizione futura per export PDF/XLSX, ma non implementare il PDF nella prima fase.
7. Qualità architetturale:
    * separare chiaramente modelli database, servizi di calcolo, API, validatori e componenti frontend;
    * documentare nel README come avviare il progetto;
    * includere esempi di CSV validi;
    * includere seed data/demo;
    * evitare hardcoding di regole GSE definitive;
    * predisporre un file di configurazione per parametri economici e granularità temporale.

Deliverable richiesti:

* struttura completa del repository;
* Docker Compose funzionante;
* backend FastAPI avviabile;
* frontend React avviabile;
* schema database iniziale;
* endpoint principali documentati in OpenAPI;
* esempio CSV;
* README operativo;
* test minimi del motore di calcolo.

Prima di scrivere codice, analizza il repository esistente. Se è vuoto, crea tu la struttura. Procedi per commit logici e spiega le scelte principali nel README.
