from fastapi import FastAPI

from app.routers import auth, users, integrations, workflows, runs, templates, billing, admin

app = FastAPI(title="TaskPilot API", version="0.1.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(integrations.router)
app.include_router(workflows.router)
app.include_router(runs.router)
app.include_router(templates.router)
app.include_router(billing.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}
