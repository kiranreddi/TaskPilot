from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("/{run_id}", response_model=schemas.RunResponse)
def get_run(
    run_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    run = db.query(models.Run).filter(
        models.Run.id == run_id,
        models.Run.org_id == current_user["org_id"],
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

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


@router.post("/{run_id}/cancel", response_model=schemas.RunResponse)
def cancel_run(
    run_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    run = db.query(models.Run).filter(
        models.Run.id == run_id,
        models.Run.org_id == current_user["org_id"],
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    if run.status not in ("QUEUED", "RUNNING"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel run with status {run.status}",
        )

    run.status = "CANCELED"
    db.commit()
    db.refresh(run)

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
