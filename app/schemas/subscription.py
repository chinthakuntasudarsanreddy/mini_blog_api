from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PlanCreate(BaseModel):
    name: str
    price: Decimal = Decimal("0.00")
    billing_period_days: int = 30
    max_posts: int = 5
    max_image_size_mb: int = 2
    active: bool = True


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    billing_period_days: int
    max_posts: int
    max_image_size_mb: int
    active: bool


class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int
    auto_renew: bool = False


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    plan_id: int
    status: str
    started_at: datetime
    expires_at: datetime
    auto_renew: bool


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    subscription_id: int
    user_id: int
    amount: Decimal
    currency: str
    status: str
    issued_at: datetime
    pdf_path: str | None = None