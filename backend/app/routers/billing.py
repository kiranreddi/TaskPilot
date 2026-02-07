from fastapi import APIRouter, Request

from app import schemas

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/webhook", response_model=schemas.BillingWebhookResponse)
async def stripe_webhook(request: Request):
    # In production, verify the Stripe signature here
    _body = await request.body()
    return schemas.BillingWebhookResponse(received=True)
