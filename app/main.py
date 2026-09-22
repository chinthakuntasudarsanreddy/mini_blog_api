from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from app.core.database import Base, engine
from app.models import User, Post, Comment, Like

from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router
from app.routers.likes import router as likes_router
from app.routers.subscriptions import router as subscription_router
from app.routers.dashboard import router as dashboard_router

from app.models.subscription_plan import (
    SubscriptionPlan,
    Subscription,
    Invoice,
)


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
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8081",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    name="media",
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(subscription_router)
app.include_router(dashboard_router)


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


# ============================================================
# CUSTOM OPENAPI
# ============================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Mini Blogging System",
        version="1.0.0",
        description="Blogging API with JWT authentication",
        routes=app.routes,
    )

    # Use OpenAPI 3.0 for better Swagger file-upload rendering
    openapi_schema["openapi"] = "3.0.3"

    # --------------------------------------------------------
    # POST /posts
    # --------------------------------------------------------

    create_schema = openapi_schema.get(
        "components",
        {}
    ).get(
        "schemas",
        {}
    ).get(
        "Body_create_post_posts_post"
    )

    if create_schema:
        properties = create_schema.get("properties", {})

        if "images" in properties:
            properties["images"] = {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "binary",
                },
                "title": "Images",
            }

    # --------------------------------------------------------
    # PUT /posts/{post_id}
    # --------------------------------------------------------

    update_schema = openapi_schema.get(
        "components",
        {}
    ).get(
        "schemas",
        {}
    ).get(
        "Body_update_post_posts__post_id__put"
    )

    if update_schema:
        properties = update_schema.get("properties", {})

        if "images" in properties:
            properties["images"] = {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "binary",
                },
                "title": "Images",
            }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi