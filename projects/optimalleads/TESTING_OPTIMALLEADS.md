# OptimalLeads Testing Guide

This guide shows how to validate the three OptimalLeads microservices end-to-end with SQL Server, CQRS, validation, transaction pipeline, and outbox flush.

## 1. What you should see

- `chat` on `http://127.0.0.1:8001`
- `leads` on `http://127.0.0.1:8002`
- `analytics` on `http://127.0.0.1:8003`
- Each service should start in `sqlserver` mode
- If `RESET_DATABASE_ON_STARTUP=true`, the service should drop and recreate its database on startup, then run migrations
- Commands should go through CQRS and the pipeline
- Reads should come from the query side
- `chat` should expose `/outbox/flush` to publish pending events

## 2. Recommended startup

Use the same workspace startup you already have, but make sure the three OptimalLeads services are started with SQL Server and reset enabled.

Example environment variables:

- `OPTIMALLEADS_CHAT_PERSISTENCE_PROVIDER=sqlserver`
- `OPTIMALLEADS_CHAT_RESET_DATABASE_ON_STARTUP=true`
- `OPTIMALLEADS_LEADS_PERSISTENCE_PROVIDER=sqlserver`
- `OPTIMALLEADS_LEADS_RESET_DATABASE_ON_STARTUP=true`
- `OPTIMALLEADS_ANALYTICS_PERSISTENCE_PROVIDER=sqlserver`
- `OPTIMALLEADS_ANALYTICS_RESET_DATABASE_ON_STARTUP=true`

For the SQL Server baseline, the business DB should be the main DB. Leave `OUTBOX_DATABASE_URL`, `AUDIT_DATABASE_URL` and `EVENTS_DATABASE_URL` empty if you want them to reuse the business DB. Set them explicitly only if you want a separate DB for audit or events.

For more `.env` examples in memory, SQLite and SQL Server modes, see the workspace README:

- [README.md](../../README.md)

## 3. Health checks

```bash
curl http://127.0.0.1:8002/health
curl http://127.0.0.1:8002/leads/health
curl http://127.0.0.1:8003/health
```

Expected responses:

- `{"service":"chat","status":"ok"}`
- `{"service":"leads","status":"ok"}`
- `{"service":"analytics","status":"ok"}`

### Update a conversation

```bash
curl -X PUT http://127.0.0.1:8001/conversations/<conversation-id> \
  -H "Content-Type: application/json" \
  -d '{"title":"Chat updated","summary":"Updated from PUT","messages":["Hello from CQRS 2","Second message from PUT"],"correlation_id":"chat-upd-001"}'
```

## 4. Chat test flow

### Create five conversations

```bash
  -d '{"name":"Lead updated","stage":"qualified","notes":["First note from PUT","Second note from PUT"],"correlation_id":"lead-upd-001"}'
  -H "Content-Type: application/json" \
  -d '{"title":"Chat CQRS 1","correlation_id":"chat-001"}'

curl -X POST http://127.0.0.1:8001/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Chat CQRS 2","correlation_id":"chat-002"}'

curl -X POST http://127.0.0.1:8001/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Chat CQRS 3","correlation_id":"chat-003"}'

curl -X POST http://127.0.0.1:8001/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Chat CQRS 4","correlation_id":"chat-004"}'

curl -X POST http://127.0.0.1:8001/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Chat CQRS 5","correlation_id":"chat-005"}'
```

### Chat read-back via CQRS query endpoints

```bash
curl http://127.0.0.1:8001/conversations
curl http://127.0.0.1:8001/conversations/<conversation-id>
```

### Append a message

```bash
curl -X POST http://127.0.0.1:8001/conversations/<conversation-id>/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello from CQRS","correlation_id":"chat-msg-001"}'
```

### Delete a conversation

```bash
curl -X DELETE "http://127.0.0.1:8001/conversations/<conversation-id>?correlation_id=chat-del-001"
```

### Flush the outbox

```bash
curl -X POST http://127.0.0.1:8001/outbox/flush
```

Expected response format:

```json
{"published":5}
```

## 5. Leads test flow

### Create five leads

```bash
curl -X POST http://127.0.0.1:8002/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Lead CQRS 1","correlation_id":"lead-001"}'

curl -X POST http://127.0.0.1:8002/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Lead CQRS 2","correlation_id":"lead-002"}'

curl -X POST http://127.0.0.1:8002/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Lead CQRS 3","correlation_id":"lead-003"}'

curl -X POST http://127.0.0.1:8002/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Lead CQRS 4","correlation_id":"lead-004"}'

curl -X POST http://127.0.0.1:8002/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Lead CQRS 5","correlation_id":"lead-005"}'
```

### Read back via CQRS query endpoints

```bash
curl http://127.0.0.1:8002/leads
curl http://127.0.0.1:8002/leads/<lead-id>
```

### Update a lead

```bash
curl -X PUT http://127.0.0.1:8002/leads/<lead-id> \
  -H "Content-Type: application/json" \
  -d '{"name":"Lead updated","stage":"qualified","correlation_id":"lead-upd-001"}'
```

### Advance the stage

```bash
curl -X POST http://127.0.0.1:8002/leads/<lead-id>/stage \
  -H "Content-Type: application/json" \
  -d '{"stage":"proposal","correlation_id":"lead-stage-001"}'
```

### Delete a lead

```bash
curl -X DELETE "http://127.0.0.1:8002/leads/<lead-id>?correlation_id=lead-del-001"
```

## 6. Analytics test flow

Analytics is read-side oriented and currently exposes snapshot/query style endpoints plus ingest.

### Health

```bash
# Important: do not hardcode `occurred_at` in a real test unless you want a fixed historical timestamp.
# Use the actual timestamp emitted by the service or a current UTC value.
curl http://127.0.0.1:8003/health
```

### Snapshot

```bash
curl http://127.0.0.1:8003/analytics/snapshot
curl http://127.0.0.1:8003/analytics
```

### Ingest an event

Use an event envelope from the outbox output.

```bash
curl -X POST http://127.0.0.1:8003/analytics/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "event_id":"evt-001",
    "aggregate_id":"agg-001",
    "event_name":"ConversationCreated",
    "event_kind":"domain",
    "correlation_id":"corr-001",
    "causation_id":null,
    "occurred_at":"<current-utc-timestamp>",
    "payload":{"conversation_id":"agg-001","title":"Demo"}
  }'
```

## 7. SQL verification

After the commands, check SQL Server directly:

- `chat_conversations`
- `chat_outbox`
- `leads`
- `projections`

Useful checks:

```sql
SELECT * FROM chat_conversations ORDER BY created_at DESC;
SELECT * FROM chat_outbox ORDER BY created_at DESC;
SELECT * FROM leads ORDER BY id DESC;
SELECT * FROM projections ORDER BY id DESC;
```

## 8. Notes

- If a service does not answer on its port, it is not running or it is using a different startup environment.
- If the database is not recreated, confirm `RESET_DATABASE_ON_STARTUP=true` for that service and that it is running with `persistence_provider=sqlserver`.
- `chat` and `leads` are the write-side services with CQRS + outbox.
- `analytics` is read-side oriented and may need its own event ingest flow depending on the scenario.
