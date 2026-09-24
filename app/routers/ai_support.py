from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.ai_support import AISupportChat
from app.models.user import User
from app.schemas.ai_support import (
    AISupportRequest,
    AISupportResponse,
)
from app.services.ai_support import generate_ai_response


router = APIRouter(
    prefix="/api/ai-support",
    tags=["AI Support"],
)


# ============================================================
# SEND MESSAGE TO AI SUPPORT
# ============================================================

@router.post(
    "/",
    response_model=AISupportResponse,
)
def ai_support(
    request: AISupportRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # VALIDATE MESSAGE
    # --------------------------------------------------------

    question = request.message.strip()

    if not question:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # --------------------------------------------------------
    # GENERATE AI RESPONSE
    # --------------------------------------------------------

    ai_response = generate_ai_response(
        question
    )

    # --------------------------------------------------------
    # SAVE CHAT HISTORY
    # --------------------------------------------------------

    chat = AISupportChat(
        user_id=current_user.id,
        question=question,
        ai_response=ai_response,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return chat


# ============================================================
# GET MY AI SUPPORT HISTORY
# ============================================================

@router.get(
    "/history",
    response_model=list[AISupportResponse],
)
def get_ai_support_history(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    chats = (
        db.query(AISupportChat)
        .filter(
            AISupportChat.user_id
            == current_user.id
        )
        .order_by(
            AISupportChat.created_at.asc()
        )
        .all()
    )

    return chats