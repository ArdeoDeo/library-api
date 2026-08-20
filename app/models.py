from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    serial_number: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)

    is_borrowed: Mapped[bool] = mapped_column(default=False)
    borrower_card_number: Mapped[str | None] = mapped_column(
        String(6),
        nullable=True,
    )
    borrowed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
