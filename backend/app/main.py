from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, users, integrations, workflows, runs, templates, billing, admin

app = FastAPI(title="TaskPilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    import app.models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine)

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
