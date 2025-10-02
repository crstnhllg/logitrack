# LogiTrack

A FastAPI-based logistics tracking API to manage orders, vehicles, and users.

## Features

- Create, update, and track orders
- Assign orders to vehicles
- User management with roles (admin, driver)
- JWT-based authentication
- Pydantic validation for request/response models
- SQLAlchemy ORM with SQLite (or other DB)

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy
- Pydantic
- JWT for authentication
- Uvicorn as ASGI server

## Setup

1. Clone the repository:

```bash
git clone https://github.com/crstnhllg/logitrack.git
cd logitrack
````

2. Set and copy env vars:

Modify .env.example to include necessary env vars

`cp .env.example .env`

3. Run docker compose

Run `docker compose build` and `docker compose up -d`

The server will be available on http://localhost:8000

API Docs on http://localhost:8000/docs

## License

MIT License
