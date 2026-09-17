
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.subscription_plan import Subscription


LIMIT_MESSAGE = (
    "You've reached your plan limit. "
    "Kindly upgrade your plan to continue."
)


def get_active_subscription(
    db: Session,
    user_id: int
):
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.expires_at > datetime.utcnow(),
        )
        .order_by(
            Subscription.started_at.desc()
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=403,
            detail="You do not have an active subscription."
        )

    return subscription


def check_post_limit(
    db: Session,
    user_id: int
):
    subscription = get_active_subscription(
        db,
        user_id
    )

    max_posts = subscription.plan.max_posts

    # -1 means unlimited
    if max_posts == -1:
        return subscription

    from app.models.post import Post

    post_count = (
        db.query(Post)
        .filter(
            Post.author_id == user_id
        )
        .count()
    )

    if post_count >= max_posts:
        raise HTTPException(
            status_code=403,
            detail=LIMIT_MESSAGE
        )

    return subscription


def check_like_limit(
    db: Session,
    user_id: int
):
    subscription = get_active_subscription(
        db,
        user_id
    )

    max_likes = subscription.plan.max_likes

    # -1 means unlimited
    if max_likes == -1:
        return subscription

    from app.models.like import Like

    like_count = (
        db.query(Like)
        .filter(
            Like.user_id == user_id
        )
        .count()
    )

    if like_count >= max_likes:
        raise HTTPException(
            status_code=403,
            detail=LIMIT_MESSAGE
        )

    return subscription


def check_comment_limit(
    db: Session,
    user_id: int
):
    subscription = get_active_subscription(
        db,
        user_id
    )

    max_comments = subscription.plan.max_comments

    # -1 means unlimited
    if max_comments == -1:
        return subscription

    from app.models.comment import Comment

    comment_count = (
        db.query(Comment)
        .filter(
            Comment.user_id == user_id
        )
        .count()
    )

    if comment_count >= max_comments:
        raise HTTPException(
            status_code=403,
            detail=LIMIT_MESSAGE
        )

    return subscription


def check_image_limit(
    db: Session,
    user_id: int,
    image_count: int
):
    subscription = get_active_subscription(
        db,
        user_id
    )

    max_images = subscription.plan.max_images_per_post

    # -1 means unlimited
    if max_images == -1:
        return subscription

    if image_count >= max_images:
        raise HTTPException(
            status_code=403,
            detail=LIMIT_MESSAGE
        )

    return subscription