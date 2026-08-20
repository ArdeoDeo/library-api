import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.models import Book
from app.main import app
from app.database import SessionLocal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete


@pytest.fixture(autouse=True)
def clean_database():
    with SessionLocal() as db:
        db.execute(delete(Book))
        db.commit()

    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_create_book(client: TestClient):
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


def test_create_duplicate_book(client: TestClient):
    book = {
        "serial_number": 100001,
        "title": "1984",
        "author": "George Orwell",
    }

    client.post("/books", json=book)
    response = client.post("/books", json=book)

    assert response.status_code == 409


def test_get_books(client: TestClient):
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
    assert len(response.json()) == 2


def test_borrow_book(client: TestClient):
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


def test_return_book(client: TestClient):
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


def test_delete_book(client: TestClient):
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
