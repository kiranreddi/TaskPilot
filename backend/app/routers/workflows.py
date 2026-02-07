from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.workflow_engine import execute_workflow, validate_definition

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

DEFAULT_DEFINITION = {
    "steps": [
        {"id": "s1", "tool": "taskpilot.llm.summarize", "args": {"items_ref": "input", "style": "default"}}
    ]
}


@router.get("", response_model=list[schemas.WorkflowResponse])
def list_workflows(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org_id = current_user["org_id"]
    workflows = db.query(models.Workflow).filter(models.Workflow.org_id == org_id).all()
    return [schemas.WorkflowResponse.model_validate(w) for w in workflows]


@router.post("", response_model=schemas.WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    req: schemas.WorkflowCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    definition = req.definition or DEFAULT_DEFINITION

    valid, err = validate_definition(definition)
    if not valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)

    workflow = models.Workflow(
        org_id=current_user["org_id"],
        name=req.name,
        description=req.description,
        created_by=current_user["user_id"],
    )
    db.add(workflow)
    db.flush()

    version = models.WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        definition_json=definition,
    )
    db.add(version)
    db.commit()
    db.refresh(workflow)

    return schemas.WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/run", response_model=schemas.RunResponse)
def run_workflow(
    workflow_id: str,
    req: schemas.WorkflowRunRequest = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req is None:
        req = schemas.WorkflowRunRequest()

    workflow = db.query(models.Workflow).filter(
        models.Workflow.id == workflow_id,
        models.Workflow.org_id == current_user["org_id"],
    ).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    version = db.query(models.WorkflowVersion).filter(
        models.WorkflowVersion.workflow_id == workflow_id
    ).order_by(models.WorkflowVersion.version.desc()).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No workflow version found")

    # Check org approval policy
    org = db.query(models.Org).filter(models.Org.id == current_user["org_id"]).first()
    require_approval = org.require_approval_for_write if org else True

    run = models.Run(
        workflow_version_id=version.id,
        org_id=current_user["org_id"],
        initiated_by=current_user["user_id"],
        input_json=req.inputs,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    run = execute_workflow(
        db=db,
        run=run,
        definition=version.definition_json,
        require_approval_for_write=require_approval,
        approval_token=req.approval_token,
    )

    return schemas.RunResponse(
        id=run.id,
        workflow_version_id=run.workflow_version_id,
        org_id=run.org_id,
        status=run.status,
        initiated_by=run.initiated_by,
        input_json=run.input_json,
        output_summary=run.output_summary,
        started_at=run.started_at,
        finished_at=run.finished_at,
        steps=[schemas.RunStepResponse.model_validate(s) for s in run.steps],
    )
