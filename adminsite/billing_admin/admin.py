
from django.contrib import admin

from .models import (
    SubscriptionPlan,
    Subscription,
    Invoice,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "billing_period_days",
        "max_posts",
        "max_images_per_post",
        "max_likes",
        "max_comments",
        "max_image_size_mb",
        "active",
    )

    list_filter = ("active",)

    search_fields = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "plan",
        "started_at",
        "expires_at",
        "status",
        "transaction_id",
    )

    list_filter = (
        "status",
        "plan",
    )

    search_fields = (
        "transaction_id",
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "invoice_number",
        "user_id",
        "subscription_id",
        "transaction_id",
        "amount",
        "currency",
        "created_at",
    )

    list_filter = ("currency",)

    search_fields = (
        "invoice_number",
        "transaction_id",
    )