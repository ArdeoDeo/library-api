# library-api
Simple REST API for managing library books, built with FastAPI, PostgreSQL and Docker.

# Assumptions and open questions
- serial_number is a 'liczba' so it cannot have leading zeros but borrower_card_number is 'numer' so it can have leading zeros?
- what if book is already borrowed and you are setting as borrowed again?
