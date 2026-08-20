import os
from collections.abc import Generator

# The database URL must be configured before importing the application.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database import SessionLocal
from app.main import app
from app.models import Book


@pytest.fixture(autouse=True)
def clean_database() -> Generator[None, None, None]:
    with SessionLocal() as db:
        db.execute(delete(Book))
        db.commit()

    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_create_book(client: TestClient) -> None:
    response = client.post(
        "/books",
        json={
            "serial_number": 100001,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["serial_number"] == 100001
    assert data["title"] == "1984"
    assert data["author"] == "George Orwell"
    assert data["is_borrowed"] is False
    assert data["borrower_card_number"] is None
    assert data["borrowed_at"] is None


def test_create_duplicate_book(client: TestClient) -> None:
    book = {
        "serial_number": 100001,
        "title": "1984",
        "author": "George Orwell",
    }

    client.post("/books", json=book)
    response = client.post("/books", json=book)

    assert response.status_code == 409


@pytest.mark.parametrize("serial_number", [99999, 1000000])
def test_create_book_requires_six_digit_serial_number(
    client: TestClient,
    serial_number: int,
) -> None:
    response = client.post(
        "/books",
        json={
            "serial_number": serial_number,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["title", "author"])
def test_create_book_rejects_blank_text(
    client: TestClient,
    field: str,
) -> None:
    book = {
        "serial_number": 100001,
        "title": "1984",
        "author": "George Orwell",
    }
    book[field] = "   "

    response = client.post("/books", json=book)

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["title", "author"])
def test_create_book_rejects_text_longer_than_255_characters(
    client: TestClient,
    field: str,
) -> None:
    book = {
        "serial_number": 100001,
        "title": "1984",
        "author": "George Orwell",
    }
    book[field] = "a" * 256

    response = client.post("/books", json=book)

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["title", "author"])
def test_create_book_accepts_255_character_text(
    client: TestClient,
    field: str,
) -> None:
    book = {
        "serial_number": 100001,
        "title": "1984",
        "author": "George Orwell",
    }
    book[field] = "a" * 255

    response = client.post("/books", json=book)

    assert response.status_code == 201
    assert response.json()[field] == book[field]


def test_get_books(client: TestClient) -> None:
    client.post(
        "/books",
        json={
            "serial_number": 100001,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    client.post(
        "/books",
        json={
            "serial_number": 100002,
            "title": "Animal Farm",
            "author": "George Orwell",
        },
    )

    response = client.get("/books")

    assert response.status_code == 200
    books_by_serial_number = {
        book["serial_number"]: book for book in response.json()
    }
    assert set(books_by_serial_number) == {100001, 100002}
    assert books_by_serial_number[100001]["title"] == "1984"
    assert books_by_serial_number[100002]["title"] == "Animal Farm"


def test_borrow_book(client: TestClient) -> None:
    client.post(
        "/books",
        json={
            "serial_number": 100001,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    response = client.patch(
        "/books/100001",
        json={
            "is_borrowed": True,
            "borrower_card_number": "000001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_borrowed"] is True
    assert data["borrower_card_number"] == "000001"
    assert data["borrowed_at"] is not None


def test_borrow_book_requires_card_number(client: TestClient) -> None:
    client.post(
        "/books",
        json={
            "serial_number": 100001,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    response = client.patch(
        "/books/100001",
        json={"is_borrowed": True},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Borrower card number is required"}


@pytest.mark.parametrize(
    "card_number",
    ["12345", "1234567", "abcdef", "١٢٣٤٥٦"],
)
def test_borrow_book_rejects_invalid_card_number(
    client: TestClient,
    card_number: str,
) -> None:
    client.post(
        "/books",
        json={
            "serial_number": 100001,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    response = client.patch(
        "/books/100001",
        json={
            "is_borrowed": True,
            "borrower_card_number": card_number,
        },
    )

    assert response.status_code == 422


def test_return_book(client: TestClient) -> None:
    client.post(
        "/books",
        json={
            "serial_number": 100001,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    client.patch(
        "/books/100001",
        json={
            "is_borrowed": True,
            "borrower_card_number": "000001",
        },
    )

    response = client.patch(
        "/books/100001",
        json={
            "is_borrowed": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_borrowed"] is False
    assert data["borrower_card_number"] is None
    assert data["borrowed_at"] is None


def test_delete_book(client: TestClient) -> None:
    client.post(
        "/books",
        json={
            "serial_number": 100001,
            "title": "1984",
            "author": "George Orwell",
        },
    )

    response = client.delete("/books/100001")

    assert response.status_code == 204

    response = client.get("/books")

    assert response.status_code == 200
    assert response.json() == []


def test_update_missing_book_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        "/books/100001",
        json={"is_borrowed": False},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_delete_missing_book_returns_not_found(client: TestClient) -> None:
    response = client.delete("/books/100001")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}
