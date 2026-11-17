# CoLab

Events and publicity system for CoLab Jos: staff publish events, the public sees and registers for them, staff check people in, and each event gets a ready-to-post graphic.

What it should do is in [`specs/001-events-core/spec.md`](specs/001-events-core/spec.md). How and in what order it's being built is in [`specs/001-events-core/plan.md`](specs/001-events-core/plan.md).

## Status

| Slice | What works | State |
|---|---|---|
| 0 Foundation | Public home page, staff sign-in, admin, health check, Docker, CI | Done |
| 1 Staff publish, public sees | | Next |
| 2 Pitch and approve | | |
| 3 Registration | | |
| 4 Check-in | | |
| 5 Publicity | | |

## Run it locally

Without Docker (uses SQLite):

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # then set DJANGO_SECRET_KEY
export $(grep -v '^#' .env | xargs)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

With Docker (uses PostgreSQL, capped at 512 MB per container):

```bash
cp .env.example .env            # then set DJANGO_SECRET_KEY
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

Stop it with `docker compose down`. It doesn't start by itself at boot.

Open http://localhost:8000. Staff sign in at `/login/`; the admin is at `/admin/`.

## Checks

```bash
ruff check . && ruff format --check .
pytest
```

CI runs the same checks against PostgreSQL on every push, then builds the Docker image.

## Stack

Python 3.12, Django 5.2, PostgreSQL 16, server-rendered templates, Gunicorn, WhiteNoise, Docker, GitHub Actions.
