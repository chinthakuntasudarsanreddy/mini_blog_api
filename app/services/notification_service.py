from datetime import datetime

from app.services.email_service import send_email


def send_post_activity_notification(
    recipient_email: str,
    recipient_name: str,
    post_title: str,
    actor_name: str,
    activity_type: str,
    activity_time: datetime
):
    if activity_type.lower() == "like":
        activity_text = "Liked your post"
    elif activity_type.lower() == "comment":
        activity_text = "Commented on your post"
    else:
        activity_text = activity_type

    formatted_time = activity_time.strftime(
        "%Y-%m-%d %I:%M %p"
    )

    subject = f"Someone {activity_type.lower()}d your post"

    body = f"""
Hello {recipient_name},

Someone interacted with your blog post.

Post: {post_title}
User: {actor_name}
Activity: {activity_text}
Time: {formatted_time}

Thank you,
Blog Management System
""".strip()

    send_email(
        recipient_email=recipient_email,
        subject=subject,
        body=body
    )