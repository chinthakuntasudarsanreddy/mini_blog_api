from pydantic import BaseModel
from typing import List


class PostAnalytics(BaseModel):
    post_id: int
    title: str
    likes: int
    comments: int
    views: int = 0


class DashboardResponse(BaseModel):
    user_id: int

    total_posts: int
    total_comments: int
    total_likes_received: int
    total_views: int

    posts: List[PostAnalytics]