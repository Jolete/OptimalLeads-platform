# OptimalLeads Principles

Aquest document defineix el criteri funcional del producte OptimalLeads.

## 1. Un projecte, diversos microserveis

OptimalLeads no és una sola API amb moltes rutes. És un producte compost per microserveis petits que es poden desplegar, provar i escalar de manera separada.

## 2. REST per fora, contractes forts per dins

Les APIs públiques s'exposen per REST. La comunicació entre serveis interns es fa amb contractes explícits i, quan té sentit, amb gRPC.

## 3. Persistència per servei

Cada microservei pot tenir la seva pròpia base de dades. No s'ha d'assumir una sola BD compartida per tot el producte.

## 4. Canvis fiables

Quan un servei canvia estat, el canvi s'ha de poder publicar de manera fiable. L'outbox és la base per evitar pèrdua d'esdeveniments.

## 5. Lectura desacoblada

Les consultes no han de dependre de la mateixa estructura d'escriptura. CQRS ens permet optimitzar lectures i reduir dependències.

## 6. Coordinació de processos

Quan una acció travessa diversos serveis, la SAGA ha de coordinar el flux i, si cal, les compensacions.

## 7. Observabilitat des del principi

Logs, traces i health checks no són opcionals. Han de ser part del producte des del principi.

## 8. Núcli reutilitzable

El core reutilitzable es manté a `packages/` i no ha de dependre dels projectes concrets.

## 9. Capes per microservei

Cada microservei manté les seves pròpies capes: `domain`, `application`, `infrastructure` i `presentation`. El producte només composa microserveis i, si cal, ofereix una landing o gateway.

## 10. Implementació incremental però real

No volem només contractes futurs. Volem funcionalitat mínima real que es pugui executar i ampliar.
# Principles

- Core packages contain reusable abstractions and domain primitives.
- Application packages contain use cases, commands, DTOs and orchestration.
- Infrastructure packages contain adapters, persistence and external technology integration.
- Hosts expose the application through FastAPI, MCP, Aura or CLI.
- Projects contain business-specific domain and application logic for one product.
- External technology must always be behind a port or adapter.
- Persistence can vary per project: SQL, Mongo, Redis, memory or other stores.
- LLM providers can vary per project: OpenAI, Anthropic, Ollama or custom providers.
