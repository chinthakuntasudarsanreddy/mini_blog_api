from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db

from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like

from app.schemas.dashboard import DashboardResponse, PostAnalytics


router = APIRouter(
    prefix="/user",
    tags=["User Dashboard"]
)


@router.get(
    "/dashboard",
    response_model=DashboardResponse
)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all posts created by the logged-in user
    user_posts = (
        db.query(Post)
        .filter(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    total_posts = len(user_posts)

    # Total comments made by the logged-in user
    total_comments = (
        db.query(Comment)
        .filter(Comment.user_id == current_user.id)
        .count()
    )

    total_likes_received = 0
    total_views = 0

    post_analytics = []

    for post in user_posts:

        # Likes received on this user's post
        likes_count = (
            db.query(Like)
            .filter(Like.post_id == post.id)
            .count()
        )

        # Comments received on this user's post
        comments_count = (
            db.query(Comment)
            .filter(Comment.post_id == post.id)
            .count()
        )

        # View tracking is not implemented yet
        views_count = 0

        total_likes_received += likes_count
        total_views += views_count

        post_analytics.append(
            PostAnalytics(
                post_id=post.id,
                title=post.title,
                likes=likes_count,
                comments=comments_count,
                views=views_count
            )
        )

    return DashboardResponse(
        user_id=current_user.id,
        total_posts=total_posts,
        total_comments=total_comments,
        total_likes_received=total_likes_received,
        total_views=total_views,
        posts=post_analytics
    )