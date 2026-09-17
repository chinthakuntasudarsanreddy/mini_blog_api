
from django.db import models


class SubscriptionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period_days = models.IntegerField()

    max_posts = models.IntegerField()
    max_images_per_post = models.IntegerField()
    max_likes = models.IntegerField()
    max_comments = models.IntegerField()
    max_image_size_mb = models.IntegerField()

    active = models.BooleanField()

    class Meta:
        managed = False
        db_table = "subscription_plans"
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    plan = models.ForeignKey(
        SubscriptionPlan,
        db_column="plan_id",
        on_delete=models.DO_NOTHING,
        related_name="subscriptions",
    )
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = "subscriptions"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"User {self.user_id} - {self.plan.name}"


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    subscription_id = models.IntegerField(
        null=True,
        blank=True,
    )
    invoice_number = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    invoice_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "invoices"
        verbose_name = "Billing History"
        verbose_name_plural = "Billing History"

    def __str__(self):
        return self.invoice_number
