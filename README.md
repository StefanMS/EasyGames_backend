# EasyGames

A FastAPI backend for a game bidding platform: users sign up, browse game
collections, and place bids in a `bidding_basket`.

## Stack

- FastAPI + Uvicorn
- SQLAlchemy 2.0 (async) with SQLite (`aiosqlite`)
- Pydantic v2 / pydantic-settings
- Passlib (bcrypt) for password hashing

## Setup

Requires Python 3.12.

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # macOS/Linux

pip install -r requirements-dev.txt
```

Configuration is read from environment variables (or a `.env` file in the
project root). All settings have working defaults for local development, so
a `.env` file is optional:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./easygames_db.db` | SQLAlchemy async connection string |
| `SECRET_KEY` | `dev-secret-key` | Reserved for token signing |
| `ALGORITHM` | `HS256` | Reserved for token signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Reserved for token expiry |

## Running

```bash
uvicorn app.main:app --reload
```

The SQLite database file is created automatically on startup (via
`Base.metadata.create_all`) — it is not committed to the repo.

Interactive API docs are available at `http://127.0.0.1:8000/docs` once the
server is running.

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Tests run against an isolated in-memory SQLite database (see
`tests/conftest.py`) and don't touch the dev database file.

## Known limitations

- `get_current_user` (`app/db/session.py`) is a placeholder that returns a
  fixed user id rather than validating a real auth token — there is no JWT
  issuance/verification yet despite password hashing being in place.
- The `note` module CRUD/routes were implemented to match the existing
  module pattern but have no dedicated tests yet.
