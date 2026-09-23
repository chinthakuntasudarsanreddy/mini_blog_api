from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.subscription_plan import (
    SubscriptionPlan,
    Subscription,
    Invoice,
)
from app.services.invoice import generate_invoice_pdf
from app.services.notifications import create_notification


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions & Billing"],
)


# ---------------------------------------------------------
# PLAN LIMITS
# ---------------------------------------------------------

PLAN_LIMITS = {
    "Basic": {
        "max_posts": 1,
        "max_images_per_post": 1,
        "max_likes": 10,
        "max_comments": 10,
        "max_image_size_mb": 2,
    },
    "Premium": {
        "max_posts": 2,
        "max_images_per_post": 2,
        "max_likes": 50,
        "max_comments": 50,
        "max_image_size_mb": 5,
    },
    "Pro": {
        "max_posts": -1,
        "max_images_per_post": -1,
        "max_likes": -1,
        "max_comments": -1,
        "max_image_size_mb": -1,
    },
}


# ---------------------------------------------------------
# SUBSCRIBE TO PLAN
# ---------------------------------------------------------

@router.post("/{user_id}/{plan_name}")
def subscribe_to_plan(
    user_id: int,
    plan_name: str,
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # FIND USER
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    # -----------------------------------------------------
    # NORMALIZE PLAN NAME
    # -----------------------------------------------------

    requested_plan_name = plan_name.strip().lower()

    # -----------------------------------------------------
    # FIND ACTIVE PLAN
    # -----------------------------------------------------

    plans = (
        db.query(SubscriptionPlan)
        .filter(
            SubscriptionPlan.active.is_(True)
        )
        .all()
    )

    plan = next(
        (
            item
            for item in plans
            if item.name.lower() == requested_plan_name
        ),
        None,
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found.",
        )

    # -----------------------------------------------------
    # CHECK PLAN LIMITS
    # -----------------------------------------------------

    limits = PLAN_LIMITS.get(plan.name)

    if not limits:
        raise HTTPException(
            status_code=400,
            detail="Invalid subscription plan.",
        )

    # -----------------------------------------------------
    # EXPIRE PREVIOUS ACTIVE SUBSCRIPTIONS
    # -----------------------------------------------------

    active_subscriptions = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
        )
        .all()
    )

    for old_subscription in active_subscriptions:
        old_subscription.status = "expired"

    # -----------------------------------------------------
    # CREATE NEW SUBSCRIPTION
    # -----------------------------------------------------

    started_at = datetime.utcnow()

    expires_at = started_at + timedelta(
        days=plan.billing_period_days
    )

    transaction_id = (
        f"TXN-{uuid4().hex[:12].upper()}"
    )

    subscription = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        status="active",
        started_at=started_at,
        expires_at=expires_at,
        transaction_id=transaction_id,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    # -----------------------------------------------------
    # CREATE SUBSCRIPTION NOTIFICATION
    # -----------------------------------------------------

    notification = create_notification(
        db=db,
        user_id=user.id,
        message=(
            f"Your {plan.name} subscription has been "
            f"activated successfully."
        ),
        notification_type="subscription",
    )

    print("\n========== SUBSCRIPTION NOTIFICATION ==========")
    print("NOTIFICATION ID:", notification.id)
    print("NOTIFICATION TYPE:", notification.notification_type)
    print("USER ID:", user.id)
    print("PLAN:", plan.name)
    print("===============================================\n")

    # -----------------------------------------------------
    # CREATE INVOICE NUMBER
    # -----------------------------------------------------

    invoice_number = (
        f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        f"-{subscription.id}"
    )

    # -----------------------------------------------------
    # GENERATE INVOICE PDF
    # -----------------------------------------------------

    pdf_path = generate_invoice_pdf(
        invoice_number=invoice_number,
        user_name=user.username,
        user_email=user.email,
        plan_name=plan.name,
        amount=plan.price,
        currency="INR",
        started_at=subscription.started_at,
        expires_at=subscription.expires_at,
    )

    # -----------------------------------------------------
    # CREATE INVOICE RECORD
    # -----------------------------------------------------

    invoice = Invoice(
        invoice_number=invoice_number,
        transaction_id=transaction_id,
        subscription_id=subscription.id,
        user_id=user.id,
        amount=plan.price,
        currency="INR",
        invoice_path=pdf_path,
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "message": "Subscription activated successfully.",

        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },

        "subscription": {
            "id": subscription.id,
            "plan": plan.name,
            "price": float(plan.price),
            "start_date": subscription.started_at,
            "end_date": subscription.expires_at,
            "status": subscription.status,
            "transaction_id": subscription.transaction_id,
        },

        "invoice": {
            "invoice_number": invoice.invoice_number,
            "invoice_path": invoice.invoice_path,
        },

        "limits": limits,

        "notification": {
            "id": notification.id,
            "type": notification.notification_type,
            "message": notification.message,
        },
    }