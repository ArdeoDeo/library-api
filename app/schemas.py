from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    serial_number: int = Field(ge=100000, le=999999)
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)


class BookStatusUpdate(BaseModel):
    is_borrowed: bool
    borrower_card_number: str | None = Field(
        default=None,
        pattern=r"^\d{6}$",
    )


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    serial_number: int
    title: str
    author: str
    is_borrowed: bool
    borrower_card_number: str | None
    borrowed_at: datetime | None
