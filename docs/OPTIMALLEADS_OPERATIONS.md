# OptimalLeads Operativa

Aquest document és la guia pràctica per treballar amb OptimalLeads: arquitectura, arrencada, migracions, creació de microserveis, core reutilitzable i estat actual de CQRS/behaviors.

## 1. Què tenim ara

OptimalLeads és un producte amb microserveis independents:

- `chat`
- `leads`
- `analytics`

I una landing principal al workspace:

- `http://127.0.0.1:8080/`
- docs globals d'OptimalLeads: `http://127.0.0.1:8080/docs`

Cada microservei té:

- la seva FastAPI pròpia
- el seu `main.py`
- el seu `settings.py`
- la seva capa `domain`
- la seva capa `application`
- la seva capa `infrastructure`
- la seva capa `presentation`
- la seva carpeta de persistència i migracions Alembic

## 2. Com s'engega tot

La manera recomanada és executar el launcher de workspace:

```powershell
.
\start_workspace.ps1
```

Aquest script obre 4 processos separats:

- landing principal a `8080`
- Chat a `8001`
- Leads a `8002`
- Analytics a `8003`

URLs útils:

- landing principal: `http://127.0.0.1:8080/`
- docs globals: `http://127.0.0.1:8080/docs`
- Chat docs: `http://127.0.0.1:8001/docs`
- Leads docs: `http://127.0.0.1:8002/docs`
- Analytics docs: `http://127.0.0.1:8003/docs`

## 3. Configuració per `.env`

La norma del projecte és clara: el comportament es controla des dels `.env` del microservei.

### Variables clau

Per cada microservei tenim:

- `BUSINESS_DATABASE_URL`
- `RESET_DATABASE_ON_STARTUP`
- `OUTBOX_DATABASE_URL` (opcional)
- `AUDIT_DATABASE_URL` (opcional)
- `EVENTS_DATABASE_URL` (opcional)
- `BROKER_PROVIDER`
- `BROKER_URL`
- `BROKER_TOPIC`
- `BROKER_QUEUE`
- `BROKER_CONSUMER_GROUP`
- `TELEMETRY_SERVICE_NAME`

### Regla de reset

- `RESET_DATABASE_ON_STARTUP=true` només per proves de recreació
- després s'ha de tornar a `false`
- si es deixa sempre a `true`, la BD es recrearà a cada arrencada

## 4. Flux de BD i migracions

Cada microservei fa el mateix patró:

1. Llegeix el seu `.env`
2. Arrenca el bootstrap de persistència
3. Si `RESET_DATABASE_ON_STARTUP=true`, elimina la BD existent
4. Crida `ensure_database_exists(...)`
5. Executa `alembic upgrade head`
6. Crea sessions, repositoris i runtime

### Què toca quan fem una nova migració

1. Canviar el model ORM o l'entitat del domini
2. Crear o modificar la migració Alembic dins del microservei
3. Validar l'arxiu `env.py` d'Alembic del microservei
4. Arrencar el servei i comprovar que `alembic upgrade head` s'executa
5. Validar la BD a SQL Server Management Studio

### Què toca quan afegim un camp nou

1. Actualitzar el Value Object o l'entitat del domini
2. Actualitzar el model ORM
3. Crear la migració Alembic corresponent
4. Arrencar amb reset si cal recrear la BD
5. Tornar el reset a `false` quan es validi

## 5. Com crear un microservei nou

Si cal afegir un microservei nou, l'ordre pràctic és:

1. Crear `projects/<nou_servei>/`
2. Crear `main.py`
3. Crear `settings.py`
4. Crear `domain/`
5. Crear `application/`
6. Crear `infrastructure/`
7. Crear `presentation/`
8. Crear `infrastructure/persistence/`
9. Afegir Alembic dins de `infrastructure/persistence/alembic/`
10. Crear `bootstrap.py` de runtime/persistència
11. Crear el `.env` propi del servei
12. Afegir el servei al launcher del workspace i a la landing si cal

### Mínim funcional d'un microservei nou

- una ruta de `health`
- un `main.py` amb `create_app()`
- un `settings.py` que llegeixi `.env`
- un bootstrap de persistència
- almenys una migració inicial

## 6. Core reutilitzable

El core reusable està a `packages/`.

### El que ja tenim implementat de veritat

#### `packages/core_domain`

- primitives de domini
- `AggregateRoot`
- `AggregateRootId`
- `Guid`
- `messaging.py` amb `Command`, `Query`, `Mediator`, `InMemoryMediator`
- `pipeline.py` amb `LoggingBehavior` i `TransactionBehavior`

#### `packages/core_infrastructure`

- drivers SQL Server
- driver genèric SQLAlchemy repository
- `database_bootstrap` per crear/eliminar BD SQL Server
- `alembic_runner` genèric
- factories i adaptadors compartits

### El que hi ha però encara és bàsic o stub

- `core_infrastructure.drivers.oracle.repository` és un stub
- `core_infrastructure.drivers.mongodb.repository` és un stub
- `core_infrastructure.drivers.sqlserver.repository` és un alias fi sobre SQLAlchemy
- no hi ha un driver SQLite genèric específic com a adaptador real de producte

## 7. CQRS i behaviors

### Estat actual

Hi ha infraestructura per CQRS i pipeline behaviors al core, però a OptimalLeads encara no està tot passat per un bus únic formal a tots els endpoints.

### El que ja existeix

- `Command` i `Query` al core
- `InMemoryMediator`
- `LoggingBehavior`
- `TransactionBehavior`

### El que fa ara el producte

- els routers HTTP invoquen els use cases directament
- els use cases fan la lògica de negoci
- els startup hooks inicialitzen runtime i persistència

### Si més endavant ho volem formalitzar

Podem portar-ho a un estil més MediatR:

1. command/query explícits
2. handlers separats
3. mediator central
4. behaviors per logging, transacció i validació

## 8. Com provar que tot funciona

Ordre recomanat:

1. arrencar el workspace amb `start_workspace.ps1`
2. obrir la landing principal
3. clicar Chat, Leads i Analytics
4. fer peticions als endpoints principals
5. comprovar que les BD s'han creat a SQL Server
6. comprovar que les migracions han pujat correctament

## 9. Estat funcional actual

### Fet

- landing principal del workspace
- docs globals d'OptimalLeads
- microserveis separats per Chat, Leads i Analytics
- BD per microservei
- migracions Alembic per microservei
- helper genèric `run_alembic_upgrade` al core
- helper SQL Server de create/drop BD al core
- settings carregats des dels `.env`

### Pendent o a reforçar

- CQRS formal complet a tots els endpoints
- behaviors connectats de forma homogènia a tota l'aplicació
- drivers Oracle i Mongo reals
- més tests d'integració de bootstrap + migracions
- documentar el procés de crear una migració nova amb exemple real

## 10. Regla d'or

Si una cosa és compartida i genèrica, va a `packages/`.
Si una cosa és específica d'un microservei, va dins de `projects/<microservei>/`.
