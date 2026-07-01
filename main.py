from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from projects.optimalleads.analytics.presentation.api.router import router as analytics_router
from projects.optimalleads.chat.presentation.api.router import router as chat_router
from projects.optimalleads.leads.presentation.api.router import router as leads_router


def create_app(projects: list[str] | None = None) -> FastAPI:
    app = FastAPI(title="Quantion Workspace")
    app.include_router(chat_router)
    app.include_router(leads_router)
    app.include_router(analytics_router)

    @app.get("/docs", include_in_schema=False)
    async def optimalleads_docs() -> HTMLResponse:
        return HTMLResponse("""<!doctype html>
<html lang="ca">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>OptimalLeads Docs</title>
    <style>
        body { margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #0f172a; color: #e5e7eb; }
        main { max-width: 960px; margin: 0 auto; padding: 48px 24px; }
        h1 { margin: 0 0 12px; font-size: 2.5rem; }
        p { color: #9ca3af; margin: 0 0 24px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
        a { display: block; padding: 20px; border-radius: 18px; background: #111827; color: inherit; text-decoration: none; border: 1px solid rgba(255,255,255,.08); }
        .chip { display: inline-block; margin-top: 12px; padding: 8px 12px; border-radius: 999px; background: linear-gradient(90deg, #22c55e, #38bdf8); color: #03120a; font-weight: 700; }
    </style>
</head>
<body>
    <main>
        <h1>OptimalLeads Docs</h1>
        <p>Documentació completa del producte i accessos directes als Swagger dels microserveis.</p>
        <div class="grid">
            <a href="http://127.0.0.1:8001/docs" target="_blank" rel="noreferrer"><strong>Chat</strong><br /><span class="chip">Swagger Chat</span></a>
            <a href="http://127.0.0.1:8002/docs" target="_blank" rel="noreferrer"><strong>Leads</strong><br /><span class="chip">Swagger Leads</span></a>
            <a href="http://127.0.0.1:8003/docs" target="_blank" rel="noreferrer"><strong>Analytics</strong><br /><span class="chip">Swagger Analytics</span></a>
        </div>
    </main>
</body>
</html>""")

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

    return app
