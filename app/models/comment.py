from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(
        Integer,
        ForeignKey("posts.id"),
        nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship(
        "Post",
        back_populates="comments"
    )

    user = relationship(
        "User",
        back_populates="comments"
    )