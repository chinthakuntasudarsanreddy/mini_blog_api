
import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostResponse

# Change this import only if your project uses a different auth dependency.
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


# ============================================================
# MEDIA CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MEDIA_DIR = BASE_DIR / "media"
POSTS_MEDIA_DIR = MEDIA_DIR / "posts"

POSTS_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


# Allowed image types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


# ============================================================
# IMAGE HELPERS
# ============================================================

async def save_post_image(image: UploadFile) -> str:
    """
    Save uploaded image inside media/posts/
    and return the relative URL.
    """

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid image type. "
                "Allowed types: JPG, PNG, GIF, WEBP."
            ),
        )

    file_extension = ALLOWED_IMAGE_TYPES[image.content_type]

    filename = f"{uuid.uuid4().hex}{file_extension}"

    file_path = POSTS_MEDIA_DIR / filename

    contents = await image.read()

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size must be 5 MB or less.",
        )

    try:
        with open(file_path, "wb") as file:
            file.write(contents)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save image.",
        ) from exc

    return f"/media/posts/{filename}"


def delete_post_image(image_url: str | None):
    """
    Delete an existing post image from disk.
    """

    if not image_url:
        return

    filename = image_url.split("/")[-1]

    file_path = POSTS_MEDIA_DIR / filename

    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass


def make_image_url(
    request: Request,
    image: str | None,
) -> str | None:
    """
    Convert relative image path into a complete URL.
    """

    if not image:
        return None

    if image.startswith("http://") or image.startswith("https://"):
        return image

    return f"{str(request.base_url).rstrip('/')}{image}"


def post_to_response(
    request: Request,
    post: Post,
):
    """
    Convert SQLAlchemy Post object into API response.
    """

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "image": make_image_url(request, post.image),
        "author_id": post.author_id,
        "created_at": post.created_at,
    }


# ============================================================
# CREATE POST
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new blog post.

    Supports optional image upload.
    """

    if len(title.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must contain at least 3 characters.",
        )

    if len(content.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content must contain at least 10 characters.",
        )

    image_path = None

    if image is not None:
        image_path = await save_post_image(image)

    post = Post(
        title=title.strip(),
        content=content.strip(),
        image=image_path,
        author_id=current_user.id,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post_to_response(request, post)


# ============================================================
# LIST POSTS - PAGINATION + SEARCH
# ============================================================

@router.get("")
def get_posts(
    request: Request,
    page: int = Query(
        1,
        ge=1,
        description="Page number",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of posts per page",
    ),
    search: str | None = Query(
        None,
        description="Search posts by title or content",
    ),
    db: Session = Depends(get_db),
):
    """
    Get posts with pagination and optional search.

    Examples:

    /posts?page=1&limit=10

    /posts?search=python

    /posts?search=python&page=2&limit=5
    """

    query = db.query(Post)

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search and search.strip():
        search_value = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Post.title.ilike(search_value),
                Post.content.ilike(search_value),
            )
        )

    # --------------------------------------------------------
    # TOTAL COUNT
    # --------------------------------------------------------

    total = query.count()

    # --------------------------------------------------------
    # TOTAL PAGES
    # --------------------------------------------------------

    total_pages = (
        (total + limit - 1) // limit
        if total > 0
        else 0
    )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    offset = (page - 1) * limit

    posts = (
        query
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "posts": [
            post_to_response(request, post)
            for post in posts
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


# ============================================================
# MY POSTS
# ============================================================

@router.get("/mine")
def get_my_posts(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get posts created by the logged-in user.
    """

    posts = (
        db.query(Post)
        .filter(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    return [
        post_to_response(request, post)
        for post in posts
    ]


# ============================================================
# GET SINGLE POST
# ============================================================

@router.get("/{post_id}")
def get_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get a single blog post.
    """

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return post_to_response(request, post)


# ============================================================
# UPDATE POST
# ============================================================

@router.put("/{post_id}")
async def update_post(
    post_id: int,
    request: Request,
    title: str | None = Form(None),
    content: str | None = Form(None),
    image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a post.

    Only the post owner can update it.

    Image is optional.
    If a new image is uploaded, the old image is deleted.
    """

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    # --------------------------------------------------------
    # OWNERSHIP CHECK
    # --------------------------------------------------------

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can update only your own posts.",
        )

    # --------------------------------------------------------
    # UPDATE TITLE
    # --------------------------------------------------------

    if title is not None:

        if len(title.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must contain at least 3 characters.",
            )

        post.title = title.strip()

    # --------------------------------------------------------
    # UPDATE CONTENT
    # --------------------------------------------------------

    if content is not None:

        if len(content.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content must contain at least 10 characters.",
            )

        post.content = content.strip()

    # --------------------------------------------------------
    # UPDATE IMAGE
    # --------------------------------------------------------

    if image is not None:

        old_image = post.image

        new_image = await save_post_image(image)

        post.image = new_image

        # Delete old image after new image is successfully saved
        delete_post_image(old_image)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    db.commit()
    db.refresh(post)

    return post_to_response(request, post)


# ============================================================
# DELETE POST
# ============================================================

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a post.

    Only the post owner can delete it.
    """

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    # --------------------------------------------------------
    # OWNERSHIP CHECK
    # --------------------------------------------------------

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your own posts.",
        )

    # --------------------------------------------------------
    # DELETE IMAGE
    # --------------------------------------------------------

    delete_post_image(post.image)

    # --------------------------------------------------------
    # DELETE POST
    # --------------------------------------------------------

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully."
    }
