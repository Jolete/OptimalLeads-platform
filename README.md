
# Quantion Workspace

Aquest workspace conté dos projectes al mateix nivell:

- [projects/optimalleads](projects/optimalleads) és el producte principal que volem construir
- [projects/etrto](projects/etrto) és un altre projecte independent

El root [main.py](main.py) només actua com a índex de projectes. La documentació funcional d'OptimalLeads viu a [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) i [docs/PRINCIPLES.md](docs/PRINCIPLES.md).
La guia operativa del dia a dia és a [docs/OPTIMALLEADS_OPERATIONS.md](docs/OPTIMALLEADS_OPERATIONS.md). La guia de logging, traces i backends d'observability és a [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md).

## Què arrenca cada cosa

- [main.py](main.py) mostra els dos projectes del workspace
- [bootstrap.py](bootstrap.py) arrenca la landing principal del workspace
- [projects/optimalleads/main.py](projects/optimalleads/main.py) mostra els microserveis interns d'OptimalLeads
- [projects/optimalleads/chat/main.py](projects/optimalleads/chat/main.py) arrenca el microservei Chat
- [projects/optimalleads/leads/main.py](projects/optimalleads/leads/main.py) arrenca el microservei Leads
- [projects/optimalleads/analytics/main.py](projects/optimalleads/analytics/main.py) arrenca el microservei Analytics
- [projects/etrto/main.py](projects/etrto/main.py) arrenca l'API d'ETRTO

## Arrencada completa

Primero arrenca la landing principal del workspace:

```powershell
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn bootstrap:app --reload --port 8080
```

Després arrenca els microserveis:

```powershell
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn projects.optimalleads.chat.main:create_app --factory --reload --port 8001
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn projects.optimalleads.leads.main:create_app --factory --reload --port 8002
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn projects.optimalleads.analytics.main:create_app --factory --reload --port 8003
```

Obre aquestes URLs:

- Landing principal: `http://127.0.0.1:8080/`
- Chat docs: `http://127.0.0.1:8001/docs`
- Leads docs: `http://127.0.0.1:8002/docs`
- Analytics docs: `http://127.0.0.1:8003/docs`

## Execució

Per arrencar el workspace global:

```bash
uvicorn bootstrap:app --reload
```

Per arrencar només OptimalLeads:

```python
from projects.optimalleads.main import create_app

app = create_app()
```

## Extensió per `.http`

Per executar els fitxers `.http` directament a VS Code i veure el botó `Send Request`, cal tenir una extensió de client REST instal·lada. La que he trobat més adequada per aquest workspace és:

- [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)

Alternatives que també vaig trobar, però no són les que fan servir ara mateix els fitxers del workspace:

- [HTTP Client](https://marketplace.visualstudio.com/items?itemName=mkloubert.vscode-http-client)
- [Simple REST Client](https://marketplace.visualstudio.com/items?itemName=tino.simple-rest-client)

El workspace també ho recomana automàticament amb [.vscode/extensions.json](.vscode/extensions.json).

## Com arrencar OptimalLeads

Tots els serveis llegeixen la configuració dels seus fitxers `.env` propis. Usa sempre la venv del workspace:

```powershell
& f:\Projects\QUANTION\Phyton\.venv\Scripts\Activate.ps1
```

### Landing del producte

```powershell
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn bootstrap:app --reload --port 8080
```

Si estrenes el repo en una altra màquina, primer executa el bootstrap de dependències equivalent a un `npm install` o `dotnet restore`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap-optimalleads-deps.ps1
```

Després ja pots usar el launcher de workspace, que també el crida automàticament:

```powershell
.\start_workspace.cmd
```

### Chat

```powershell
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn projects.optimalleads.chat.main:create_app --factory --reload --port 8001
```

### Leads

```powershell
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn projects.optimalleads.leads.main:create_app --factory --reload --port 8002
```

### Analytics

```powershell
& f:\Projects\QUANTION\Phyton\.venv\Scripts\python.exe -m uvicorn projects.optimalleads.analytics.main:create_app --factory --reload --port 8003
```

## Configuració `.env`

Cada microservei d'OptimalLeads carrega el seu propi `.env` local o de plantilla, segons el cas:

- [projects/optimalleads/chat/.env](projects/optimalleads/chat/.env)
- [projects/optimalleads/leads/.env](projects/optimalleads/leads/.env)
- [projects/optimalleads/analytics/.env](projects/optimalleads/analytics/.env)

Els fitxers de plantilla i els valors de prova que ara queden versionats són aquests:

- [projects/optimalleads/chat/.env.example](projects/optimalleads/chat/.env.example)
- [projects/optimalleads/leads/.env.example](projects/optimalleads/leads/.env.example)
- [projects/optimalleads/analytics/.env.example](projects/optimalleads/analytics/.env.example)

Si canvies d'ordinador, el flux recomanat és:

1. Clonar el repo.
2. Executar el task o script de bootstrap si vols regenerar el workspace local.
3. Ajustar les credencials locals a cada `.env` si estàs treballant fora de la plantilla.

El valor de `PERSISTENCE_PROVIDER` surt del `.env` i el CORE decideix quin driver/bootstrapping usar. No cal tocar codi per canviar de backend.

Per defecte, l'escenari principal d'OptimalLeads és SQL Server als tres microserveis. `outbox`, `audit` i `events` poden compartir la mateixa BD o anar a una BD diferent, però això s'ha de declarar explícitament al `.env`.

### Opcions suportades

- `memory`: útil per proves ràpides i desenvolupament local sense BD física.
- `sqlite`: útil per tenir persistència local lleugera.
- `sqlserver`: opció habitual per l'entorn real.

### Exemple: memòria

```env
PERSISTENCE_PROVIDER=memory
RESET_DATABASE_ON_STARTUP=false
BUSINESS_DATABASE_URL=memory://chat
BROKER_PROVIDER=in_memory
BROKER_URL=
BROKER_TOPIC=chat-events
BROKER_QUEUE=chat-events
BROKER_CONSUMER_GROUP=chat
TELEMETRY_SERVICE_NAME=optimalleads-chat
```

### Exemple: SQLite

```env
PERSISTENCE_PROVIDER=sqlite
RESET_DATABASE_ON_STARTUP=true
BUSINESS_DATABASE_URL=sqlite+aiosqlite:///./data/chat.db
OUTBOX_DATABASE_URL=sqlite+aiosqlite:///./data/chat.db
BROKER_PROVIDER=in_memory
BROKER_URL=
BROKER_TOPIC=chat-events
BROKER_QUEUE=chat-events
BROKER_CONSUMER_GROUP=chat
TELEMETRY_SERVICE_NAME=optimalleads-chat
```

### Exemple: SQL Server

```env
PERSISTENCE_PROVIDER=sqlserver
RESET_DATABASE_ON_STARTUP=false
BUSINESS_DATABASE_URL=mssql+aioodbc://sa:Password12345@localhost:14331/optimalleads_chat?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
OUTBOX_DATABASE_URL=
AUDIT_DATABASE_URL=
EVENTS_DATABASE_URL=
BROKER_PROVIDER=faststream_kafka
BROKER_URL=localhost:9092
BROKER_TOPIC=optimalleads.chat.events
BROKER_QUEUE=optimalleads.chat.events
BROKER_CONSUMER_GROUP=optimalleads-chat-group
TELEMETRY_SERVICE_NAME=optimalleads-chat
```

### Exemple: SQL Server amb audit separat

```env
PERSISTENCE_PROVIDER=sqlserver
RESET_DATABASE_ON_STARTUP=false
BUSINESS_DATABASE_URL=mssql+aioodbc://sa:Password12345@localhost:14331/optimalleads_chat?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
OUTBOX_DATABASE_URL=
AUDIT_DATABASE_URL=mssql+aioodbc://sa:Password12345@localhost:14331/optimalleads_audit?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
EVENTS_DATABASE_URL=
BROKER_PROVIDER=faststream_kafka
BROKER_URL=localhost:9092
BROKER_TOPIC=optimalleads.chat.events
BROKER_QUEUE=optimalleads.chat.events
BROKER_CONSUMER_GROUP=optimalleads-chat-group
TELEMETRY_SERVICE_NAME=optimalleads-chat
```

### Mapeig per microservei

- Chat usa el mateix patró de variables però amb `optimalleads-chat` i la seva BD.
- Leads usa `optimalleads-leads` i la seva BD.
- Analytics usa `optimalleads-analytics` i la seva BD.

Si vols provar en memòria, canvia només `PERSISTENCE_PROVIDER=memory` i posa un `BUSINESS_DATABASE_URL` simbòlic. Si vols persistència real, posa `sqlite` o `sqlserver` i apunta les URL a la base corresponent.

L'escenari recomanat per arrencar i provar ara mateix és `sqlserver` als tres serveis, amb `OUTBOX_DATABASE_URL`, `AUDIT_DATABASE_URL` i `EVENTS_DATABASE_URL` buits si vols que comparteixin BD amb `BUSINESS_DATABASE_URL`.

### Ordre recomanat per provar BD i migracions

1. Arrenca Chat amb `OPTIMALLEADS_CHAT_RESET_DATABASE_ON_STARTUP=true` per esborrar la BD i recrear-la.
2. Arrenca Chat un segon cop amb `OPTIMALLEADS_CHAT_RESET_DATABASE_ON_STARTUP=false` per veure que no recrea res.
3. Fes un canvi de model i crea una migració nova.
4. Torna a arrencar Chat amb `reset=false` per veure l'update de schema.
5. Repeteix el mateix patró amb Leads i després Analytics.

### Base de dades a SQL Server Management Studio

- Chat: `optimalleads_chat`
- Leads: `optimalleads_leads`   
- Analytics: `optimalleads_analytics`

Connexió típica:

- Server: `localhost,1433`
- User: `sa`
- Password: `Password12345`
- Authentication: `SQL Server Authentication`

## Arquitectura

La idea és tenir un producte amb microserveis que ja sigui útil de veritat:

- REST per a consum extern
- gRPC per a comunicació interna entre microserveis
- CQRS per separar escriptura i lectura
- SAGA per coordinar transaccions distribuïdes
- Outbox per garantir publicació fiable d'esdeveniments

El core reusable segueix sota [packages](packages) i no depèn de cap projecte concret.
