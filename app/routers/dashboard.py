
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
    # ============================================================
    # GET ALL POSTS CREATED BY THE LOGGED-IN USER
    # ============================================================

    user_posts = (
        db.query(Post)
        .filter(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    total_posts = len(user_posts)

    # ============================================================
    # DASHBOARD TOTALS
    # ============================================================

    # Total comments RECEIVED on the user's posts
    total_comments = 0

    # Total likes RECEIVED on the user's posts
    total_likes_received = 0

    # View tracking will be implemented later
    total_views = 0

    post_analytics = []

    # ============================================================
    # ANALYTICS FOR EACH POST
    # ============================================================

    for post in user_posts:

        # --------------------------------------------------------
        # LIKES RECEIVED ON THIS POST
        # --------------------------------------------------------

        likes_count = (
            db.query(Like)
            .filter(Like.post_id == post.id)
            .count()
        )

        # --------------------------------------------------------
        # COMMENTS RECEIVED ON THIS POST
        # --------------------------------------------------------

        comments_count = (
            db.query(Comment)
            .filter(Comment.post_id == post.id)
            .count()
        )

        # --------------------------------------------------------
        # VIEWS
        # --------------------------------------------------------

        # View tracking is not implemented yet
        views_count = 0

        # --------------------------------------------------------
        # ADD TO TOTALS
        # --------------------------------------------------------

        total_comments += comments_count
        total_likes_received += likes_count
        total_views += views_count

        # --------------------------------------------------------
        # ADD POST ANALYTICS
        # --------------------------------------------------------

        post_analytics.append(
            PostAnalytics(
                post_id=post.id,
                title=post.title,
                likes=likes_count,
                comments=comments_count,
                views=views_count
            )
        )

    # ============================================================
    # RETURN DASHBOARD
    # ============================================================

    return DashboardResponse(
        user_id=current_user.id,
        total_posts=total_posts,
        total_comments=total_comments,
        total_likes_received=total_likes_received,
        total_views=total_views,
        posts=post_analytics
    )
