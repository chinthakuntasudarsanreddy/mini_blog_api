
from app.core.database import SessionLocal
from app.models.subscription_plan import SubscriptionPlan


PLANS = [
    {
        "name": "Basic",
        "price": 0,
        "billing_period_days": 30,
        "max_posts": 1,
        "max_images_per_post": 1,
        "max_likes": 10,
        "max_comments": 10,
        "max_image_size_mb": 2,
        "active": True,
    },
    {
        "name": "Premium",
        "price": 499,
        "billing_period_days": 30,
        "max_posts": 2,
        "max_images_per_post": 2,
        "max_likes": 50,
        "max_comments": 50,
        "max_image_size_mb": 5,
        "active": True,
    },
    {
        "name": "Pro",
        "price": 999,
        "billing_period_days": 30,
        "max_posts": -1,
        "max_images_per_post": -1,
        "max_likes": -1,
        "max_comments": -1,
        "max_image_size_mb": -1,
        "active": True,
    },
]


def seed_plans():
    db = SessionLocal()

    try:
        for plan_data in PLANS:
            existing_plan = (
                db.query(SubscriptionPlan)
                .filter(
                    SubscriptionPlan.name == plan_data["name"]
                )
                .first()
            )

            if existing_plan:
                print(
                    f"{plan_data['name']} plan already exists."
                )
                continue

            plan = SubscriptionPlan(**plan_data)

            db.add(plan)

        db.commit()

        print("Subscription plans created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_plans()
