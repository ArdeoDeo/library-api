from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Book
from app.schemas import BookCreate, BookResponse, BookStatusUpdate


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(book: BookCreate, db: Session = Depends(get_db)) -> Book:
    existing_book = db.get(Book, book.serial_number)

    if existing_book is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book with this serial number already exists",
        )

    db_book = Book(
        serial_number=book.serial_number,
        title=book.title,
        author=book.author,
    )

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book


@app.get("/books", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)) -> list[Book]:
    return list(db.scalars(select(Book)))


@app.patch("/books/{serial_number}", response_model=BookResponse)
def update_book_status(
    serial_number: Annotated[int, Path(ge=100000, le=999999)],
    update: BookStatusUpdate,
    db: Session = Depends(get_db),
) -> Book:
    book = db.get(Book, serial_number)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    if update.is_borrowed:
        if update.borrower_card_number is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Borrower card number is required",
            )

        book.is_borrowed = True
        book.borrower_card_number = update.borrower_card_number
        book.borrowed_at = datetime.now(timezone.utc)
    else:
        book.is_borrowed = False
        book.borrower_card_number = None
        book.borrowed_at = None

    db.commit()
    db.refresh(book)

    return book


@app.delete(
    "/books/{serial_number}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_book(
    serial_number: Annotated[int, Path(ge=100000, le=999999)],
    db: Session = Depends(get_db),
) -> Response:
    book = db.get(Book, serial_number)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    db.delete(book)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
