
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    price = Column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    billing_period_days = Column(
        Integer,
        nullable=False,
        default=30,
    )

    max_posts = Column(
        Integer,
        nullable=False,
        default=1,
    )

    max_images_per_post = Column(
        Integer,
        nullable=False,
        default=1,
    )

    max_likes = Column(
        Integer,
        nullable=False,
        default=10,
    )

    max_comments = Column(
        Integer,
        nullable=False,
        default=10,
    )

    max_image_size_mb = Column(
        Integer,
        nullable=False,
        default=2,
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    subscriptions = relationship(
        "Subscription",
        back_populates="plan",
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=False,
    )

    started_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    status = Column(
        String(20),
        default="active",
        nullable=False,
    )

    transaction_id = Column(
        String(100),
        nullable=True,
    )

    plan = relationship(
        "SubscriptionPlan",
        back_populates="subscriptions",
    )

    user = relationship(
        "User",
        back_populates="subscriptions",
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=True,
    )

    invoice_number = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    transaction_id = Column(
        String(100),
        nullable=False,
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False,
    )

    currency = Column(
        String(10),
        default="INR",
        nullable=False,
    )

    invoice_path = Column(
        String(500),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="invoices",
    )
