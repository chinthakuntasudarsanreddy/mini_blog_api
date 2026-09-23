from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.services.notifications import create_notification
from app.utils.email import send_email


router = APIRouter(
    tags=["Likes"]
)


@router.post(
    "/posts/{post_id}/like"
)
def like_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("\n========== LIKE DEBUG ==========")

    # -----------------------------------------
    # Find post
    # -----------------------------------------

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    print("POST ID:", post.id)
    print("POST TITLE:", post.title)
    print("POST OWNER ID:", post.author_id)

    # -----------------------------------------
    # Check existing like
    # -----------------------------------------

    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already liked this post"
        )

    # -----------------------------------------
    # Create like
    # -----------------------------------------

    like = Like(
        post_id=post_id,
        user_id=current_user.id
    )

    db.add(like)
    db.commit()
    db.refresh(like)

    print("LIKE ID:", like.id)
    print("LIKE USER:", current_user.username)
    print("LIKE USER EMAIL:", current_user.email)

    # -----------------------------------------
    # Find post owner
    # -----------------------------------------

    post_owner = db.query(User).filter(
        User.id == post.author_id
    ).first()

    if not post_owner:
        print("POST OWNER NOT FOUND")
        print("================================\n")

        return {
            "message": "Post liked successfully",
            "post_id": post_id,
            "user_id": current_user.id
        }

    print("POST OWNER:", post_owner.username)
    print("POST OWNER EMAIL:", post_owner.email)

    # -----------------------------------------
    # Don't notify user about own like
    # -----------------------------------------

    if post_owner.id == current_user.id:
        print("USER LIKED OWN POST")
        print("NO NOTIFICATION CREATED")
        print("NO EMAIL SENT")
        print("================================\n")

        return {
            "message": "Post liked successfully",
            "post_id": post_id,
            "user_id": current_user.id
        }

    # -----------------------------------------
    # Create in-app notification
    # -----------------------------------------

    notification = create_notification(
        db=db,
        user_id=post_owner.id,
        message=f"{current_user.username} liked your post: {post.title}",
        notification_type="like"
    )

    print("IN-APP NOTIFICATION CREATED")
    print("NOTIFICATION ID:", notification.id)
    print("NOTIFICATION TYPE:", notification.notification_type)

    # -----------------------------------------
    # Prepare notification email
    # -----------------------------------------

    subject = "Someone liked your blog post"

    activity_time = like.created_at

    body = (
        f"Hello {post_owner.username},\n\n"

        f"{current_user.username} liked your blog post.\n\n"

        f"Post: {post.title}\n"

        f"User: {current_user.username}\n"

        f"Activity: Liked your post\n"

        f"Time: "
        f"{activity_time.strftime('%Y-%m-%d %I:%M %p')}\n\n"

        f"Thanks,\n"
        f"Mini Blogging System"
    )

    # -----------------------------------------
    # Send email in background
    # -----------------------------------------

    background_tasks.add_task(
        send_email,
        recipient=post_owner.email,
        subject=subject,
        body=body
    )

    print("LIKE EMAIL ADDED TO BACKGROUND TASK")
    print("================================\n")

    return {
        "message": "Post liked successfully",
        "post_id": post_id,
        "user_id": current_user.id,
        "notification_id": notification.id
    }


@router.delete(
    "/posts/{post_id}/like"
)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------------------
    # Find post
    # -----------------------------------------

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # -----------------------------------------
    # Find existing like
    # -----------------------------------------

    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not liked this post"
        )

    # -----------------------------------------
    # Delete like
    # -----------------------------------------

    db.delete(like)
    db.commit()

    return {
        "message": "Post unliked successfully",
        "post_id": post_id,
        "user_id": current_user.id
    }


@router.get(
    "/posts/{post_id}/likes"
)
def get_post_likes(
    post_id: int,
    db: Session = Depends(get_db)
):
    # -----------------------------------------
    # Find post
    # -----------------------------------------

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # -----------------------------------------
    # Count likes
    # -----------------------------------------

    like_count = db.query(Like).filter(
        Like.post_id == post_id
    ).count()

    return {
        "post_id": post_id,
        "likes": like_count
    }