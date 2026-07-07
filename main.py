from __future__ import annotations

from html import escape

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import HTMLResponse

from projects.optimalleads.analytics.presentation.api.router import router as analytics_router
from projects.optimalleads.chat.presentation.api.router import router as chat_router
from projects.optimalleads.leads.presentation.api.router import router as leads_router
from telemetry import configure_http_tracing


def create_app(projects: list[str] | None = None) -> FastAPI:
    app = FastAPI(title="Quantion Workspace")
    configure_http_tracing(app)

    def _service_routes(router) -> list[APIRoute]:
        return [route for route in router.routes if isinstance(route, APIRoute) and route.path != "/"]

    def _route_methods(route: APIRoute) -> str:
        return ", ".join(sorted(method for method in (route.methods or []) if method not in {"HEAD", "OPTIONS"}))

    def _render_service_section(title: str, router, docs_url: str, health_url: str) -> str:
        routes = _service_routes(router)
        items = []
        for route in sorted(routes, key=lambda current: (current.path, sorted(current.methods or []))):
            items.append(
                f"<li><span class='method'>{escape(_route_methods(route))}</span> <code>{escape(route.path)}</code> <span class='route-name'>{escape(route.name)}</span></li>"
            )
        return f"""
            <section class='service'>
                <div class='service-head'>
                    <div>
                        <h2>{escape(title)}</h2>
                        <p>{len(routes)} rutes registrades</p>
                    </div>
                    <div class='service-links'>
                        <a href='{escape(docs_url)}' target='_blank' rel='noreferrer'>Swagger</a>
                        <a href='{escape(health_url)}' target='_blank' rel='noreferrer'>Health</a>
                    </div>
                </div>
                <ul class='route-list'>
                    {''.join(items) if items else '<li>No hi ha rutes registrades.</li>'}
                </ul>
            </section>
        """

    @app.get("/", include_in_schema=False, response_class=HTMLResponse)
    async def home() -> str:
        return """<!doctype html>
<html lang="ca">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Quantion Workspace</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #0f172a;
            --panel: #111827;
            --panel-2: #1f2937;
            --text: #e5e7eb;
            --muted: #9ca3af;
            --accent: #22c55e;
            --accent-2: #38bdf8;
        }
        body {
            margin: 0;
            font-family: Segoe UI, Arial, sans-serif;
            background: radial-gradient(circle at top, #1e293b, var(--bg));
            color: var(--text);
        }
        main {
            max-width: 960px;
            margin: 0 auto;
            padding: 48px 24px;
        }
        h1 {
            margin: 0 0 12px;
            font-size: 3rem;
        }
        p {
            color: var(--muted);
            margin: 0 0 24px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 24px;
        }
        .card {
            display: block;
            padding: 20px;
            border-radius: 18px;
            background: linear-gradient(180deg, var(--panel), var(--panel-2));
            color: inherit;
            text-decoration: none;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .card h2 { margin: 0 0 8px; }
        .card p { margin: 0; }
        .chip {
            display: inline-block;
            margin-top: 12px;
            padding: 8px 12px;
            border-radius: 999px;
            color: #03120a;
            background: linear-gradient(90deg, var(--accent), var(--accent-2));
            font-weight: 700;
        }
    </style>
</head>
<body>
    <main>
        <h1>Quantion Workspace</h1>
        <p>El root mostra la landing i l'enllaç a la documentació sencera d'OptimalLeads.</p>
        <div class="grid">
            <a class="card" href="/docs">
                <h2>OptimalLeads Docs</h2>
                <p>Documentació completa del producte.</p>
                <span class="chip">Obrir docs globals</span>
                <p style="margin-top: 12px; font-size: 0.95rem; color: var(--muted);">URL: /docs</p>
            </a>
            <a class="card" href="/overview">
                <h2>Veure-ho tot</h2>
                <p>Totes les rutes dels 3 serveis agrupades en una sola vista.</p>
                <span class="chip">Vista completa</span>
                <p style="margin-top: 12px; font-size: 0.95rem; color: var(--muted);">URL: /overview</p>
            </a>
            <a class="card" href="http://127.0.0.1:8001/docs" target="_blank" rel="noreferrer">
                <h2>Chat</h2>
                <p>Converses i missatges.</p>
                <span class="chip">Swagger de Chat</span>
                <p style="margin-top: 12px; font-size: 0.95rem; color: var(--muted);">Health: http://127.0.0.1:8001/health</p>
            </a>
            <a class="card" href="http://127.0.0.1:8002/docs" target="_blank" rel="noreferrer">
                <h2>Leads</h2>
                <p>Lead lifecycle i canvis d'etapa.</p>
                <span class="chip">Swagger de Leads</span>
                <p style="margin-top: 12px; font-size: 0.95rem; color: var(--muted);">Health: http://127.0.0.1:8002/health</p>
            </a>
            <a class="card" href="http://127.0.0.1:8003/docs" target="_blank" rel="noreferrer">
                <h2>Analytics</h2>
                <p>Ingesta i snapshot de lectura.</p>
                <span class="chip">Swagger d'Analytics</span>
                <p style="margin-top: 12px; font-size: 0.95rem; color: var(--muted);">Health: http://127.0.0.1:8003/health</p>
            </a>
        </div>
    </main>
</body>
</html>"""

    @app.get("/overview", include_in_schema=False)
    async def overview() -> HTMLResponse:
        html = f"""<!doctype html>
<html lang="ca">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>OptimalLeads Overview</title>
    <style>
        :root {{
            color-scheme: dark;
            --bg: #0f172a;
            --panel: #111827;
            --panel-2: #1f2937;
            --text: #e5e7eb;
            --muted: #9ca3af;
            --accent: #22c55e;
            --accent-2: #38bdf8;
            --border: rgba(255,255,255,.08);
        }}
        body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: radial-gradient(circle at top, #1e293b, var(--bg)); color: var(--text); }}
        main {{ max-width: 1120px; margin: 0 auto; padding: 48px 24px 64px; }}
        h1 {{ margin: 0 0 12px; font-size: 2.5rem; }}
        p {{ color: var(--muted); margin: 0; }}
        .hero {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 24px; }}
        .hero a {{ color: inherit; text-decoration: none; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }}
        .service {{ padding: 20px; border-radius: 20px; background: linear-gradient(180deg, var(--panel), var(--panel-2)); border: 1px solid var(--border); box-shadow: 0 20px 60px rgba(0,0,0,.25); }}
        .service-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 16px; }}
        .service h2 {{ margin: 0 0 4px; }}
        .service-links {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .service-links a {{ display: inline-block; padding: 8px 12px; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); color: #03120a; text-decoration: none; font-weight: 700; }}
        .route-list {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }}
        .route-list li {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 14px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.06); }}
        .method {{ display: inline-block; min-width: 64px; text-align: center; padding: 6px 10px; border-radius: 999px; background: rgba(56, 189, 248, .15); color: #7dd3fc; font-weight: 700; }}
        .route-list code {{ font-family: Consolas, monospace; font-size: .95rem; color: #f8fafc; }}
        .route-name {{ color: var(--muted); font-size: .92rem; }}
    </style>
</head>
<body>
    <main>
        <div class="hero">
            <div>
                <h1>OptimalLeads Overview</h1>
                <p>Totes les rutes agrupades per servei en una sola vista.</p>
            </div>
            <a href="/" target="_self">Tornar al root</a>
        </div>
        <div class="grid">
            {_render_service_section('Chat', chat_router, 'http://127.0.0.1:8001/docs', 'http://127.0.0.1:8001/health')}
            {_render_service_section('Leads', leads_router, 'http://127.0.0.1:8002/docs', 'http://127.0.0.1:8002/health')}
            {_render_service_section('Analytics', analytics_router, 'http://127.0.0.1:8003/docs', 'http://127.0.0.1:8003/health')}
        </div>
    </main>
</body>
</html>"""
        return HTMLResponse(html)

    app.include_router(chat_router, prefix="/chat")
    app.include_router(leads_router, prefix="/leads")
    app.include_router(analytics_router, prefix="/analytics")

    return app
