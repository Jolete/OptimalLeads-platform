# Observability

Aquest document explica com tenim separat el logging, les traces i la configuracio d'OpenTelemetry al workspace.

## Estat actual

Ara mateix tenim observabilitat local:

- els logs normals surten pel `logging` de Python
- els logs inclouen `trace_id` i `span_id` quan hi ha una traça activa
- les traces OpenTelemetry es creen per request HTTP, operacions CQRS, transaccions, outbox i dispatch d'events
- les traces s'exporten amb `ConsoleSpanExporter`
- el launcher `start_workspace.ps1` redirigeix stdout/stderr a `logs/*.log`

Per tant, avui els fitxers com `logs/chat.log`, `logs/leads.log` i `logs/analytics.log` poden contenir:

- logs d'aplicacio
- logs d'Uvicorn
- errors i stack traces
- spans OpenTelemetry impresos per consola

No hi ha encara un backend centralitzat configurat.

## Separacio de responsabilitats

- `logging_setup.py`: configura el format i la sortida del logging normal.
- `telemetry.py`: punt d'entrada de la configuracio de telemetry usada pels hosts.
- `packages/core_infrastructure/src/core_infrastructure/observability.py`: implementacio generica reutilitzable d'observability.
- `packages/core_domain/src/core_domain/pipeline/logging_behavior.py`: span per operacio CQRS i logging de durada.
- `packages/core_domain/src/core_domain/pipeline/transaction_behavior.py`: span de transaccio per command.
- `packages/core_infrastructure/src/core_infrastructure/services/outbox_worker.py`: span de publicacio d'outbox.
- `packages/core_infrastructure/src/core_infrastructure/services/event_dispatcher.py`: span de dispatch d'events.

La regla es:

- logging diu que ha passat
- tracing diu com ha passat, quant ha trigat i amb quin flux esta relacionat

## Backends possibles

### Console local

Es el que tenim ara.

- Dependencia actual: `opentelemetry-sdk`
- Exporter actual: `ConsoleSpanExporter`
- Configuracio actual: `core_infrastructure.observability.configure_telemetry`
- Sortida: stdout, i per launcher a `logs/*.log`

Serveix per validar que els spans es creen, pero no per consultar traces historicament.

### OTLP Collector

Opcio recomanada com a seguent pas generic.

Arquitectura:

```text
FastAPI services -> OTLP exporter -> OpenTelemetry Collector -> backend final
```

Backends finals habituals:

- Jaeger
- Grafana Tempo
- Elastic / ELK
- Azure Monitor / Application Insights
- Datadog
- New Relic

Canvis necessaris:

- afegir dependencia `opentelemetry-exporter-otlp`
- canviar `ConsoleSpanExporter` per `OTLPSpanExporter`
- afegir variables d'entorn per endpoint i protocol
- opcionalment afegir OpenTelemetry Collector a `docker-compose.yml`

Variables habituals:

```env
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_SERVICE_NAME=optimalleads-chat
```

El codi on aniria el canvi:

- `packages/core_infrastructure/src/core_infrastructure/observability.py`

### Jaeger

Jaeger es pot usar com a backend de traces local.

Opcio recomanada:

- serveis envien OTLP al Collector
- Collector exporta a Jaeger

Ports habituals:

- UI Jaeger: `http://localhost:16686`
- OTLP gRPC: `4317`
- OTLP HTTP: `4318`

No cal acoblar els serveis directament a Jaeger si ja usem OTLP Collector.

### Grafana Tempo

Tempo es una bona opcio si el stack de visualitzacio es Grafana.

Arquitectura habitual:

- serveis envien OTLP al Collector
- Collector exporta traces a Tempo
- Grafana consulta Tempo

Tempo no substitueix els logs; guarda traces.

### Elastic / ELK

ELK pot rebre logs i tambe traces si es configura Elastic APM o OTLP.

Opcions:

- logs normals cap a Filebeat/Logstash/Elastic
- traces via OTLP Collector cap a Elastic
- correlacio per `trace_id` i `span_id`

En aquest cas el mes important es mantenir `trace_id` als logs, cosa que ja fem amb `TraceContextFilter`.

### Azure Application Insights

Opcio natural si el desplegament va a Azure.

Canvis necessaris:

- afegir dependencia `azure-monitor-opentelemetry-exporter`
- configurar connection string com a secret
- canviar o condicionar l'exporter a `AzureMonitorTraceExporter`

Variable habitual:

```env
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
```

El codi on aniria el canvi:

- `packages/core_infrastructure/src/core_infrastructure/observability.py`

## On configurarem el backend

La configuracio tecnica ha d'estar centralitzada a:

- `packages/core_infrastructure/src/core_infrastructure/observability.py`

La configuracio per entorn hauria de sortir de variables d'entorn:

- `.env` dels microserveis
- secrets del pipeline
- variables del runtime de desplegament

No s'hauria de posar configuracio especifica del backend dins dels use cases ni routers.

## Proper pas recomanat

1. Mantenir `ConsoleSpanExporter` per desenvolupament local simple.
2. Afegir suport condicional per OTLP amb variables d'entorn.
3. Afegir OpenTelemetry Collector a `docker-compose.yml` si volem traces locals consultables.
4. Triar backend final: Jaeger/Tempo per local, App Insights si Azure, Elastic si ja hi ha ELK.
5. Propagar context pels brokers per completar la traça Chat -> Broker -> Leads -> Analytics.
