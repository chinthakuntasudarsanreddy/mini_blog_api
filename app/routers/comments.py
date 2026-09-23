from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.notifications import create_notification
from app.utils.email import send_email


router = APIRouter(
    tags=["Comments"]
)


@router.get(
    "/posts/{post_id}/comments",
    response_model=list[CommentResponse]
)
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).order_by(
        Comment.created_at.asc()
    ).all()

    return comments


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def add_comment(
    post_id: int,
    comment_data: CommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("\n========== COMMENT DEBUG ==========")

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
    # Create comment
    # -----------------------------------------

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        text=comment_data.text
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    print("COMMENT ID:", comment.id)
    print("COMMENT USER:", current_user.username)
    print("COMMENT USER EMAIL:", current_user.email)

    # -----------------------------------------
    # Find post owner
    # -----------------------------------------

    post_owner = db.query(User).filter(
        User.id == post.author_id
    ).first()

    if not post_owner:
        print("POST OWNER NOT FOUND")
        print("=================================\n")

        return comment

    print("POST OWNER:", post_owner.username)
    print("POST OWNER EMAIL:", post_owner.email)

    # -----------------------------------------
    # Don't notify user about own comment
    # -----------------------------------------

    if post_owner.id == current_user.id:
        print(
            "USER COMMENTED ON OWN POST"
        )

        print("NO NOTIFICATION CREATED")
        print("NO EMAIL SENT")
        print("=================================\n")

        return comment

    # -----------------------------------------
    # Create in-app notification
    # -----------------------------------------

    notification = create_notification(
        db=db,
        user_id=post_owner.id,
        message=(
            f"{current_user.username} commented "
            f"on your post: {post.title}"
        ),
        notification_type="comment"
    )

    print("IN-APP NOTIFICATION CREATED")
    print("NOTIFICATION ID:", notification.id)
    print("NOTIFICATION TYPE:", notification.notification_type)

    # -----------------------------------------
    # Prepare email
    # -----------------------------------------

    subject = "New comment on your blog post"

    body = (
        f"Hello {post_owner.username},\n\n"

        f"{current_user.username} commented "
        f"on your blog post.\n\n"

        f"Post: {post.title}\n"

        f"User: {current_user.username}\n"

        f"Activity: Commented on your post\n"

        f"Time: "
        f"{comment.created_at.strftime('%Y-%m-%d %I:%M %p')}\n\n"

        f"Comment:\n"
        f"{comment.text}\n\n"

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

    print("COMMENT EMAIL ADDED TO BACKGROUND TASK")
    print("=================================\n")

    return comment


@router.delete(
    "/comments/{comment_id}"
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------------------
    # Find comment
    # -----------------------------------------

    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # -----------------------------------------
    # Check comment ownership
    # -----------------------------------------

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your own comments"
        )

    # -----------------------------------------
    # Delete comment
    # -----------------------------------------

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }