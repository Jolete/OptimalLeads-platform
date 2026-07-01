# OptimalLeads Architecture

OptimalLeads és el producte principal del workspace. La idea no és tenir una sola API gran, sinó diversos microserveis autònoms amb capes pròpies i una composició mínima al nivell de producte.

## Objectiu funcional

Volem un producte amb diversos microserveis que treballin junts:

- un microservei de Chat per gestionar converses i missatges
- un microservei de Leads per gestionar leads, etapes i notes
- un tercer servei consumidor, més endavant, per lectura o coordinació de processos

La interfície externa serà REST. La comunicació interna entre serveis pot fer-se amb gRPC o amb una capa d'intercanvi d'esdeveniments, segons el cas d'ús.

## Principis de disseny

- cada microservei té la seva FastAPI pròpia
- cada microservei té les seves pròpies capes: `domain`, `application`, `infrastructure` i `presentation`
- cada microservei pot tenir la seva pròpia base de dades
- els esdeveniments del domini es publiquen de forma fiable amb outbox
- les lectures es poden materialitzar en projeccions CQRS
- les operacions multi-pas s'han de coordinar amb SAGA o una orchestració equivalent

## Estructura funcional esperada

### Workspace

- `main.py` mostra els projectes actius
- `projects/optimalleads` conté el producte OptimalLeads
- `projects/etrto` conté l'altre projecte del workspace

### OptimalLeads

- `projects/optimalleads/main.py` és només la composició/landing del producte
- `projects/optimalleads/chat` conté el microservei de Chat i totes les seves capes
- `projects/optimalleads/leads` conté el microservei de Leads i totes les seves capes
- `projects/optimalleads/analytics` conté el microservei de read-side / projeccions
- qualsevol contracte transversal de producte només ha d'existir si realment és compartit; si no, va dins del microservei o a `packages/`

## Política de capes reutilitzables

### `packages/core_domain`

- Ports, contractes i primitives compartides.
- Events base, envelopes i tipus comuns.
- Cap dependència de tecnologies concretes.

### `packages/core_application`

- Primitives d'aplicació reutilitzables.
- Commands, queries, DTOs, errors i helpers comuns.
- No conté casos d'ús de negoci específics.

### `packages/core_infrastructure`

- Implementacions reutilitzables i genèriques.
- Drivers de tecnologia: SQLAlchemy, Mongo, Oracle, HTTP clients, Salesforce, etc.
- Subcapas específiques com `brokers`, `drivers`, `persistence`, `security`, `services`.
- Tot el que sigui compartit pels serveis i no tingui lògica de negoci pròpia.

### `projects/<microservei>/infrastructure`

- Capa transversal del microservei.
- Composition root, wiring i adaptació a l'entorn del servei.
- Seguretat, context d'usuari, telemetry, exporters, serveis comuns.
- No ha de contenir lògica de domini ni casos d'ús.

### `projects/<microservei>/infrastructure/persistence`

- Tot el que sigui persistència específica del microservei.
- Settings de connexió a BD.
- Engines, sessions, DbContext equivalent, models ORM, repositoris, unit of work.
- Migracions, creació de taules, outbox persistence i suport a múltiples BDs o esquemes si cal.

### `projects/<microservei>/infrastructure/auditing`

- Persistència i flux d'auditoria si el servei la necessita.
- Pot usar una BD o esquema separat.

### `projects/<microservei>/infrastructure/events`

- Persistència de domain events / integration events si el servei en necessita una banda específica.
- Outbox, consumers i materialització si escau.

### `projects/<microservei>/infrastructure/security`

- Autenticació, autorització, policies i context de request compartits dins del microservei.

### `projects/<microservei>/infrastructure/common`

- Helpers i serveis transversals del microservei que no són persistència ni seguretat.

## Comunicació entre serveis

### REST externa

REST és l'entrada principal des de fora del sistema. Serveix per consumir APIs públiques, administració i integracions simples.

### gRPC interna

gRPC s'utilitza per comunicació interna quan un microservei necessita consultar un altre amb contracte fort, baixa latència i menys soroll que REST. Si no hi ha gateway, no cal una capa global de contractes a l'arrel del producte.

### Com encaixa gRPC aquí

gRPC encaixa especialment bé quan un microservei necessita fer una crida síncrona a un altre microservei i vol un contracte fort, tipus RPC, amb menys overhead que REST.

En OptimalLeads, gRPC podria servir per casos com:

- un orquestrador que consulta o invoca Leads de forma síncrona
- un servei intern que necessita validar estat abans de completar una passa
- una crida controlada dins d'una SAGA quan no es vol dependre només d'events asíncrons

### gRPC vs REST en aquest cas

- REST és més simple per exposició pública i proves amb `.http`.
- gRPC és més eficient i més estricte per comunicació interna.
- REST encaixa bé per comandos públics i debugging.
- gRPC encaixa bé per passos interns del workflow quan un servei necessita esperar resposta immediata.

### gRPC i SAGA

Una SAGA no obliga a fer servir només events asíncrons. També pot tenir passos síncrons:

- Chat publica event
- SAGA consumeix l'event
- SAGA crida Leads per gRPC o HTTP intern
- Leads respon
- SAGA continua amb el següent pas

Això vol dir que gRPC pot ser el mecanisme d'invocació entre serveis dins de la SAGA, mentre que l'outbox i el broker continuen sent la via fiable de publicació i recepció d'events.

### Quan prefereixo events i quan gRPC

- events: quan vols desacoblament, integració i projeccions
- gRPC: quan necessites una resposta immediata d'un servei intern

Per al flux Chat -> Lead -> Analytics, la combinació més natural és:

- event per desencadenar el flux
- gRPC o command intern per executar la passa síncrona cap a Leads
- events per informar a Analytics i altres consumidors

### Events i outbox

Quan un servei canvia estat, publica un esdeveniment de domini. Aquest esdeveniment es guarda a outbox i després es transmet al broker o al consumidor corresponent. Cada microservei ha de tenir la seva pròpia infraestructura de persistència i outbox si fa falta.

### CQRS

Les rutes d'escriptura no han de compartir la mateixa estructura que les rutes de lectura. Les lectures es poden materialitzar amb projeccions específiques per reduir coupling i simplificar consultes.

### SAGA

Quan una operació implica més d'un microservei, cal una coordinació explícita. La SAGA permet avançar i compensar passos en cas d'error, sense dependre d'una transacció distribuïda única.

## SAGA en OptimalLeads

En OptimalLeads, la SAGA no ha de viure dins del `handler` del microservei que origina l'acció. El microservei origen només ha de fer la seva feina de domini, persistir estat i publicar un event fiable amb outbox. La coordinació entre serveis ha de viure en una capa externa d'orquestració o en un process manager dedicat.

### Què fa cada peça

- `Chat` crea converses i missatges.
- `Leads` crea i modifica leads.
- `Analytics` consumeix events i manté snapshots de lectura.
- `OutboxWorker` només drena events persistits i els publica al broker configurat.
- `Broker` només transporta missatges entre serveis o consumidors.
- `SAGA / Orchestrator` conté la lògica de negoci que encadena un event d'un servei amb un command d'un altre.

### Què no fa l'outbox

- No decideix cap flux de negoci.
- No crea leads.
- No coordina dos passos de negoci.
- No compensa errors entre serveis.

### Què fa realment el broker

- Rep events publicats per l'outbox worker.
- Els entrega a un consumidor, process manager o un altre servei.
- No executa lògica de domini per ell mateix.

### Flux recomanat per `ConversationCreated -> CreateLeadCommand`

1. Un client fa `POST /conversations` a Chat.
2. Chat persisteix la conversa.
3. Chat crea `ConversationCreated` i el desa a outbox.
4. L'outbox worker publica l'event al broker de Chat.
5. Un consumidor d'integració o un servei SAGA escolta `ConversationCreated`.
6. Aquest consumidor crea i envia `CreateLeadCommand` a Leads.
7. Leads persisteix el lead i publica `LeadCreated`.
8. Analytics consumeix `ConversationCreated` i `LeadCreated` i actualitza el snapshot.

### Qui crea `CreateLeadCommand`

No el crea Chat. Tampoc l'outbox. El crea el component de coordinació:

- un microservei SAGA dedicat
- o un consumer d'integració dins d'un servei específic d'orquestració

Aquest component pot fer la crida a Leads per HTTP/CQRS intern o bé publicar un event cap al broker de Leads, segons el disseny triat.

### Amb brokers diferents per microservei

Si cada microservei té el seu broker, el patró normal és:

- Chat publica al seu broker
- el SAGA consumeix d'aquest broker
- el SAGA executa el pas següent contra Leads o publica al broker de Leads
- Analytics pot consumir d'un broker compartit, o bé rebre events replicats per un bridge

Això vol dir que, si hi ha brokers diferents, cal una peça intermèdia que faci de pont. Aquesta peça pot ser:

- un SAGA service central
- un bridge de missatgeria
- un process manager

### Lloc de la lògica

- Lògica de domini: dins de cada microservei.
- Coordinació de passos: dins del SAGA / orchestrator.
- Traducció d'events a commands: dins del SAGA / orchestrator.
- Projeccions de lectura: dins d'Analytics o del servei lector corresponent.

### `correlation_id`

`correlation_id` no és la saga en si. És l'identificador que permet seguir una mateixa història a través de múltiples serveis.

S'usa per:

- relacionar logs
- relacionar events de domini i d'integració
- seguir la cadena de `ConversationCreated -> CreateLeadCommand -> LeadCreated`
- ajudar a depurar i traçar el flux complet

### `causation_id`

Si es vol més precisió, `causation_id` indica quin event o command ha provocat el següent pas. És útil per a cadenes de múltiples salts.

### `Snapshot` a Analytics

`Snapshot` és una projecció de lectura, no la font de veritat. Analytics pot reconstruir estat agregat a partir d'events com:

- `ConversationCreated`
- `ConversationMessageAppended`
- `LeadCreated`
- `LeadStageChanged`

### Patró recomanat per a OptimalLeads

Per simular una arquitectura distribuïda realista, el millor patró és:

- Chat emet events de conversa.
- SAGA escolta events de Chat.
- SAGA ordena la creació de Lead.
- Leads emet events propis.
- Analytics consumeix tots dos fluxos i construeix snapshots.

### Opcions d'implementació

#### Opció A: SAGA com a microservei dedicat

- més clara per demostrar arquitectura distribuïda
- millor separació de responsabilitats
- ideal quan hi ha múltiples serveis i brokers

#### Opció B: Process manager dins d'un microservei existent

- més simple de començar
- menys infraestructura
- menys clar si es vol simular una arquitectura distribuïda gran

#### Opció C: Bridge de missatgeria

- útil quan hi ha brokers diferents
- fa de pont entre Chat i Leads
- pot coexistir amb un SAGA service

### Recomanació per aquest workspace

Per OptimalLeads, la recomanació més neta és crear un quart servei dedicat a SAGA / orchestration si es vol mostrar el flux complet entre serveis:

- rep events de Chat
- decideix passos següents
- crea commands per Leads
- eventualment notifica Analytics o publica events normalitzats

Això fa el cas d'ús global més entenedor i manté cada microservei amb la seva responsabilitat estricta.

### Exemple operatiu

Un flux concret podria ser aquest:

1. `Chat` rep `POST /conversations` amb `correlation_id = corr-123`.
2. `Chat` persisteix la conversa i publica `ConversationCreated` amb `correlation_id = corr-123`.
3. El `SAGA service` consumeix `ConversationCreated`.
4. El `SAGA service` decideix crear el lead i envia `CreateLeadCommand` a `Leads` mantenint `correlation_id = corr-123`.
5. `Leads` crea el lead i publica `LeadCreated` amb el mateix `correlation_id`.
6. `Analytics` consumeix `ConversationCreated` i `LeadCreated` i actualitza el snapshot.

Si una etapa falla:

- la SAGA pot reintentar
- pot compensar passos anteriors si el cas d'ús ho necessita
- pot deixar l'event en una cua de reprocessament o dead-letter

### Cas amb el mateix broker

Si Chat, Leads i Analytics comparteixen el mateix broker, el `SAGA service` pot llegir directament del mateix bus i publicar commands o events al mateix sistema. Això simplifica routing i monitoratge.

### Cas amb brokers diferents

Si cada servei té el seu broker, el `SAGA service` necessita un connector o bridge:

- o bé consumeix del broker de Chat i invoca Leads per HTTP/CQRS intern
- o bé consumeix del broker de Chat i reemeteix cap al broker de Leads

En aquest cas, el broker no fa de coordinador: només és la via de transport.

### Si fem servir el mateix broker

Si tots els microserveis publiquen i consumeixen sobre el mateix broker o sobre el mateix bus lògic, la SAGA és més simple:

- no cal fer bridge entre brokers
- el process manager només necessita subscriure's als topics/queues rellevants
- un mateix event pot ser llegit per Leads i per Analytics si els consumers estan configurats amb grups diferents o amb routing diferent

Encara així, la lògica de coordinació continua sense viure dins del broker.

### Si cada microservei té el seu broker

Si Chat, Leads i Analytics tenen brokers diferents, llavors sí que cal una peça de pont:

- un bridge que llegeixi del broker de Chat i publiqui al sistema de Leads
- o un SAGA central que consumeixi d'un broker i publiqui al següent
- o un process manager que faci HTTP/CQRS cap als altres serveis

Això és més complex, però pot servir per simular una arquitectura realment distribuïda i heterogènia.

### Resposta curta a la pregunta de fons

- amb un sol broker compartit: la coordinació és més fàcil
- amb brokers separats: la coordinació necessita bridge o orchestrator
- en tots dos casos: la SAGA és qui decideix els passos de negoci, no l'outbox ni el broker

## Exemple de flux

1. Un client crea una conversa a Chat per REST.
2. Chat persisteix l'estat i genera un esdeveniment.
3. L'esdeveniment entra a outbox.
4. Un consumidor envia l'esdeveniment a altres serveis o projeccions.
5. Leads pot reaccionar a aquest esdeveniment o consultar Chat via gRPC si cal.

## Què volem veure implementat

- endpoints públics clars per a cada microservei
- un landing intern d'OptimalLeads amb els serveis exposats
- serveis independents però connectables entre ells
- cada microservei amb les seves capes pròpies
- base preparada per afegir persistència real, projeccions i orquestració

## Mapa del template

### Root del workspace

- `main.py` és només índex de projectes
- `bootstrap.py` centralitza logging i telemetria del workspace
- `packages/` conté el core reusable

### Core reutilitzable

- `packages/core_domain` defineix ports i contractes compartits
- `packages/core_infrastructure` aporta adaptadors i factories genèriques
- cap paquet del core ha de dependre d'un microservei concret

### Microserveis d'OptimalLeads

- `projects/optimalleads/main.py` és la composició/landing del producte
- `projects/optimalleads/chat` conté Chat amb les seves capes pròpies
- `projects/optimalleads/leads` conté Leads amb les seves capes pròpies
- `projects/optimalleads/analytics` conté Analytics com a read-side i projeccions

### Dins de cada microservei

- `domain` per entitats, events i regles
- `application` per casos d'ús, CQRS i ports
- `infrastructure` per wiring transversal, seguretat, telemetry i adaptadors
- `infrastructure/persistence` per BD, models, repositoris, outbox i migracions
- `presentation` per FastAPI i rutes HTTP
- `settings.py` per carregar `.env` propi del servei

### Tasques ja fetes

- Broker abstraction amb `BrokerConfig`
- Factory de brokers amb selecció per `BROKER_PROVIDER`
- Adaptadors FastStream per Kafka, RabbitMQ i Azure Service Bus
- Wiring de Chat amb Kafka
- Wiring de Leads amb RabbitMQ
- Wiring d'Analytics amb Azure Service Bus
- Compose local amb Kafka, RabbitMQ i Azurite
- Instruccions de Copilot per mode concís
- Validació de compilació dels slices tocats

## Seguiment de Chat

### Fet

- Estructura per capes: `domain`, `application`, `infrastructure`, `presentation`
- Settings des de `.env` propi del servei
- Broker seleccionat per factory i no per codi hardcoded
- Models, repository i unit of work bàsics
- Casos d'ús per crear conversa i afegir missatge
- Outbox i worker bàsics
- Endpoint de health i landing del servei
- Payloads HTTP tipats amb Pydantic

### Parcial

- Transacció única i estricta entre write i outbox
- Errors d'aplicació més fins i coherents
- Separació completa entre router i coordinació d'aplicació
- Observabilitat més completa per request, event i worker
- Tests de domini, aplicació, repo i router

### Pendent

- CQRS real amb comandos i queries separats
- Projeccions de lectura dedicades
- Consumers asíncrons més formals
- Idempotència i retry complet de l'outbox
- Migracions SQL Server i flux d'operació més madur

### Ordre recomanat per acabar Chat

1. Tancar errors i models d'aplicació.
2. Fer coherent la transacció save + outbox.
3. Separar més el router de la coordinació d'ús.
4. Afegir tests mínims per cada capa.
5. Endurir observabilitat.

## Què no volem

- wiring directament acoblat a carpetes velles
- hooks ficticis sense implementació
- un únic servei monolític disfressat de microserveis
- dependre del workspace root per entendre cada projecte
