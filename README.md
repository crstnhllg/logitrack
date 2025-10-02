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

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Set environment variables for database and JWT secrets (example):

```bash
export DATABASE_URL="sqlite:///./logitrack.db"
export SECRET_KEY="your_secret_key"
```

4. Start the server:

```bash
uvicorn app.main:app --reload
```

API docs will be available at: `http://127.0.0.1:8000/docs`

## License

MIT License
