
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

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.post import Post, PostImage
from app.models.user import User
from app.services.subscription_limits import check_post_limit


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

POSTS_MEDIA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


# ============================================================
# SAVE IMAGE
# ============================================================

async def save_post_image(
    image: UploadFile,
) -> str:

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid image type. "
                "Allowed types: JPG, PNG, GIF, WEBP."
            ),
        )

    extension = ALLOWED_IMAGE_TYPES[
        image.content_type
    ]

    filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

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

    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save image.",
        ) from exc

    return f"/media/posts/{filename}"


# ============================================================
# DELETE IMAGE
# ============================================================

def delete_post_image(
    image_url: str | None,
):
    if not image_url:
        return

    filename = image_url.split("/")[-1]

    file_path = POSTS_MEDIA_DIR / filename

    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass


# ============================================================
# IMAGE URL
# ============================================================

def make_image_url(
    request: Request,
    image: str | None,
):
    if not image:
        return None

    if (
        image.startswith("http://")
        or image.startswith("https://")
    ):
        return image

    return (
        f"{str(request.base_url).rstrip('/')}"
        f"{image}"
    )


# ============================================================
# POST RESPONSE
# ============================================================

def post_to_response(
    request: Request,
    post: Post,
):
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,

        # Old image field kept for compatibility
        "image": make_image_url(
            request,
            post.image,
        ),

        # New multiple-image support
        "images": [
            make_image_url(
                request,
                image.image_url,
            )
            for image in post.images
        ],

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
    images: list[UploadFile] | None = File(None),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # CHECK POST SUBSCRIPTION LIMIT
    # --------------------------------------------------------

    subscription = check_post_limit(
        db=db,
        user_id=current_user.id,
    )

    # --------------------------------------------------------
    # VALIDATE TITLE
    # --------------------------------------------------------

    if len(title.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Title must contain at least "
                "3 characters."
            ),
        )

    # --------------------------------------------------------
    # VALIDATE CONTENT
    # --------------------------------------------------------

    if len(content.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Content must contain at least "
                "10 characters."
            ),
        )

    # --------------------------------------------------------
    # IMAGE LIST
    # --------------------------------------------------------

    images = images or []

    # --------------------------------------------------------
    # CHECK IMAGE LIMIT
    # --------------------------------------------------------

    max_images = (
        subscription.plan.max_images_per_post
    )

    # -1 = unlimited
    if (
        max_images != -1
        and len(images) > max_images
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You've reached your plan limit. "
                "Kindly upgrade your plan to continue."
            ),
        )

    # --------------------------------------------------------
    # CREATE POST
    # --------------------------------------------------------

    post = Post(
        title=title.strip(),
        content=content.strip(),
        author_id=current_user.id,
    )

    db.add(post)
    db.flush()

    saved_images = []

    try:

        # ----------------------------------------------------
        # SAVE IMAGES
        # ----------------------------------------------------

        for uploaded_image in images:

            image_path = await save_post_image(
                uploaded_image
            )

            post_image = PostImage(
                post_id=post.id,
                image_url=image_path,
            )

            db.add(post_image)

            saved_images.append(
                image_path
            )

        db.commit()
        db.refresh(post)

    except HTTPException:
        db.rollback()

        for image_path in saved_images:
            delete_post_image(image_path)

        raise

    except Exception:
        db.rollback()

        for image_path in saved_images:
            delete_post_image(image_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create post.",
        )

    return post_to_response(
        request,
        post,
    )


# ============================================================
# GET POSTS
# PAGINATION + SEARCH
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
        description="Posts per page",
    ),
    search: str | None = Query(
        None,
        description="Search by title or content",
    ),
    db: Session = Depends(get_db),
):

    query = db.query(Post)

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search and search.strip():

        search_value = (
            f"%{search.strip()}%"
        )

        query = query.filter(
            or_(
                Post.title.ilike(
                    search_value
                ),
                Post.content.ilike(
                    search_value
                ),
            )
        )

    # --------------------------------------------------------
    # TOTAL
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

    offset = (
        (page - 1) * limit
    )

    posts = (
        query
        .order_by(
            Post.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "posts": [
            post_to_response(
                request,
                post,
            )
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
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    posts = (
        db.query(Post)
        .filter(
            Post.author_id
            == current_user.id
        )
        .order_by(
            Post.created_at.desc()
        )
        .all()
    )

    return [
        post_to_response(
            request,
            post,
        )
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

    post = (
        db.query(Post)
        .filter(
            Post.id == post_id
        )
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return post_to_response(
        request,
        post,
    )


# ============================================================
# UPDATE POST
# ============================================================

@router.put("/{post_id}")
async def update_post(
    post_id: int,
    request: Request,
    title: str | None = Form(None),
    content: str | None = Form(None),
    images: list[UploadFile] | None = File(None),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    post = (
        db.query(Post)
        .filter(
            Post.id == post_id
        )
        .first()
    )

    # --------------------------------------------------------
    # POST NOT FOUND
    # --------------------------------------------------------

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    # --------------------------------------------------------
    # OWNER CHECK
    # --------------------------------------------------------

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can update only "
                "your own posts."
            ),
        )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if title is not None:

        if len(title.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Title must contain at least "
                    "3 characters."
                ),
            )

        post.title = title.strip()

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    if content is not None:

        if len(content.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Content must contain at least "
                    "10 characters."
                ),
            )

        post.content = content.strip()

    # --------------------------------------------------------
    # UPDATE IMAGES
    # --------------------------------------------------------

    images = images or []

    if images:

        subscription = (
            check_post_limit(
                db=db,
                user_id=current_user.id,
            )
        )

        max_images = (
            subscription.plan
            .max_images_per_post
        )

        if (
            max_images != -1
            and len(images) > max_images
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You've reached your plan limit. "
                    "Kindly upgrade your plan to continue."
                ),
            )

        old_images = list(
            post.images
        )

        saved_images = []

        try:

            for uploaded_image in images:

                image_path = (
                    await save_post_image(
                        uploaded_image
                    )
                )

                new_post_image = PostImage(
                    post_id=post.id,
                    image_url=image_path,
                )

                db.add(new_post_image)

                saved_images.append(
                    image_path
                )

            # Delete old image records
            for old_image in old_images:

                delete_post_image(
                    old_image.image_url
                )

                db.delete(old_image)

            db.commit()
            db.refresh(post)

        except HTTPException:
            db.rollback()

            for image_path in saved_images:
                delete_post_image(
                    image_path
                )

            raise

        except Exception:
            db.rollback()

            for image_path in saved_images:
                delete_post_image(
                    image_path
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not update images.",
            )

    else:
        db.commit()
        db.refresh(post)

    return post_to_response(
        request,
        post,
    )


# ============================================================
# DELETE POST
# ============================================================

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    post = (
        db.query(Post)
        .filter(
            Post.id == post_id
        )
        .first()
    )

    # --------------------------------------------------------
    # POST NOT FOUND
    # --------------------------------------------------------

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    # --------------------------------------------------------
    # OWNER CHECK
    # --------------------------------------------------------

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can delete only "
                "your own posts."
            ),
        )

    # --------------------------------------------------------
    # DELETE OLD SINGLE IMAGE
    # --------------------------------------------------------

    delete_post_image(
        post.image
    )

    # --------------------------------------------------------
    # DELETE MULTIPLE IMAGES
    # --------------------------------------------------------

    for post_image in post.images:

        delete_post_image(
            post_image.image_url
        )

    # --------------------------------------------------------
    # DELETE POST
    # --------------------------------------------------------

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully."
    }
