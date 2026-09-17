
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class BillingHistory(Base):
    __tablename__ = "billing_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=False,
        index=True
    )

    plan_name = Column(
        String(50),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    transaction_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    invoice_path = Column(
        String(500),
        nullable=True
    )

    start_date = Column(
        DateTime,
        nullable=False
    )

    end_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # User relationship
    user = relationship(
        "User",
        back_populates="billing_history"
    )

    # Subscription relationship
    subscription = relationship(
        "SubscriptionPlan",
        back_populates="billing_history"
    )
