# Library API

A small REST API for registering library books and tracking whether they are borrowed.

## Run with Docker

Docker with Docker Compose is the only requirement:

```bash
docker compose up --build
```

The API is available at <http://localhost:8000> and its interactive OpenAPI documentation at <http://localhost:8000/docs>. PostgreSQL data is retained in the `postgres_data` Docker volume. Stop the application with `docker compose down`; add `-v` to also remove the stored data.

## Run tests

Local tests require Python 3.12 and [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked
uv run pytest
```

Tests use an isolated SQLite database instead of the Docker PostgreSQL instance.

## Technology stack

- Python 3.12, FastAPI, Pydantic and Uvicorn
- SQLAlchemy 2 with psycopg 3 and PostgreSQL 18
- pytest, SQLite, uv, Docker and Docker Compose

## API

| Method | Path | Function |
| --- | --- | --- |
| `POST` | `/books` | Create a book (`serial_number`, `title`, `author`). |
| `GET` | `/books` | List all books, including borrowing status. |
| `PATCH` | `/books/{serial_number}` | Borrow or return a book using `is_borrowed` and, when borrowing, `borrower_card_number`. |
| `DELETE` | `/books/{serial_number}` | Delete a book. |

A serial number is a six-digit integer. Titles and author names must contain between 1 and 255 characters. A borrower card number is a six-digit string so leading zeros are preserved. Borrowing sets `borrowed_at` to the current UTC time; returning clears the card number and timestamp.

## Assumptions

- `PATCH` represents the requested current state. Borrowing an already borrowed book is therefore allowed and replaces its card number and timestamp; returning an available book is also harmless.
- A borrower card number supplied while returning a book is ignored and borrowing metadata is cleared.
- Books may be deleted regardless of borrowing status because the specification does not define a restriction.
- Titles and author names are limited to 255 characters to keep request validation and database storage bounded.
- Tables are created automatically on startup, which keeps this small assignment runnable without a migration system.
