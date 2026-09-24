
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine

from app.models import (
    User,
    Post,
    Comment,
    Like,
)

from app.models.subscription_plan import (
    SubscriptionPlan,
    Subscription,
    Invoice,
)

from app.models.notification import Notification
from app.models import AISupportChat

from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router
from app.routers.likes import router as likes_router
from app.routers.subscriptions import router as subscription_router
from app.routers.dashboard import router as dashboard_router
from app.routers.notifications import router as notifications_router
from app.routers.ai_support import router as ai_support_router

# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Mini Blogging System",
    description="Blogging API with JWT authentication",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
          "http://127.0.0.1:5173",
        "http://localhost:5173",
        
        "http://127.0.0.1:8081",
        "http://localhost:8081",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# STATIC MEDIA
# ============================================================

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

app.include_router(notifications_router)

app.include_router(ai_support_router)
# ============================================================
# SWAGGER AUTHORIZATION
# ============================================================

def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():

        for operation in path.values():

            if isinstance(operation, dict):

                operation["security"] = [
                    {
                        "BearerAuth": []
                    }
                ]

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi
