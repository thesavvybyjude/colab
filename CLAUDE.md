# CoLab Jos events system

Events and publicity system for CoLab's Jos branch. Staff publish events, the public sees and registers, staff check people in, each event gets a ready-to-post graphic.

- What to build: `specs/001-events-core/spec.md` (user stories, acceptance scenarios, FR-001 to FR-028)
- How and in what order: `specs/001-events-core/plan.md` (slices 0 to 5)
- Progress: the Status table in `README.md`

## Commands

```bash
. .venv/bin/activate                    # uv venv -p 3.12 .venv && uv pip install -r requirements-dev.txt if missing
export DJANGO_DEBUG=true                # settings don't read .env; manage.py needs this locally
python manage.py runserver              # SQLite, no Docker needed
pytest                                  # tests (DJANGO_DEBUG=true is set by pytest config)
ruff check . && ruff format --check .   # lint
python manage.py makemigrations --check --dry-run
```

Docker (PostgreSQL): `docker compose up --build`, stop with `docker compose down`.

## How to work here

- Build one slice at a time, in plan order. A slice is done when every acceptance scenario of its user story has a passing test, lint is clean, and the README Status table is updated.
- Write the test for an acceptance scenario before the code for it. Name tests after the scenario.
- Enforce the hard rules in the database, not only in forms: no overlapping approved events in a space, never more registrations than capacity, one registration per phone per event.
- Keep it small: server-rendered Django templates, no JavaScript framework, no new dependencies without saying why.
- Neutral styling only. CoLab's branding comes later.
- Times are Africa/Lagos. Phone is the main contact field.
- Out of scope for v1 (do not build): social media posting, payments, waitlists, QR check-in, reminders, recurring events, courses.

## Machine limits

This laptop has 14 GB RAM and runs other containers. Prefer SQLite and `runserver` while developing. Don't leave Docker containers, test browsers or dev servers running when a task is done. Never set containers to restart on boot.

## Git

Commit at the end of each working step with a clear message. Ask before pushing.
