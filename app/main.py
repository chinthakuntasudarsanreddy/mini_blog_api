
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
from app.models import User, Post, Comment, Like

from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router
from app.routers.likes import router as likes_router


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Mini Blogging System",
    description="Blogging API with JWT authentication",
    version="1.0.0"
)


# ============================================================
# MEDIA DIRECTORY
# ============================================================

# Serves uploaded images/files from the media directory.
#
# Example:
# /media/posts/example.jpg
#
# will be available at:
# http://127.0.0.1:8000/media/posts/example.jpg

app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media"
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(likes_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Mini Blogging System API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
