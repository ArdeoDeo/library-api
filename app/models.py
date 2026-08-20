from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    serial_number: Mapped[str] = mapped_column(String(6), primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)

    is_borrowed: Mapped[bool] = mapped_column(default=False)
    borrower_card_number: Mapped[str | None] = mapped_column(String(6), nullable=True)
    borrowed_at: Mapped[datetime | None] = mapped_column(nullable=True)
