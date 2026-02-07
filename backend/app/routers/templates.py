import json
import os

from fastapi import APIRouter

from app import schemas

router = APIRouter(prefix="/api", tags=["templates"])

TEMPLATES = []


def _load_templates():
    global TEMPLATES
    if TEMPLATES:
        return

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    template_files = [
        ("clean_inbox", os.path.join(repo_root, "clean_inbox.json")),
        ("weekly_revenue_report", os.path.join(repo_root, "weekly_revenue_report.json")),
    ]

    for template_id, filepath in template_files:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
            TEMPLATES.append(
                schemas.TemplateResponse(
                    id=template_id,
                    name=data["metadata"]["name"],
                    description=data["metadata"]["description"],
                    tags=data["metadata"].get("tags", []),
                    definition=data,
                )
            )


@router.get("/templates", response_model=list[schemas.TemplateResponse])
def list_templates():
    _load_templates()
    return TEMPLATES
