from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import User, Post, Comment, Like

from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router
from app.routers.likes import router as likes_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Mini Blogging System",
    description="Blogging API with JWT authentication",
    version="1.0.0"
)


# Routers
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(likes_router)


@app.get("/")
def root():
    return {
        "message": "Mini Blogging System API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }