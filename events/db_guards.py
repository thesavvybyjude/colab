"""SQLite version of the "no overlapping approved events in a space" rule.

SQLite has no exclusion constraint, so triggers enforce it. Django rebuilds SQLite tables on many
schema changes, which silently drops triggers, so these are (re)created after every migrate run.
PostgreSQL uses the exclusion constraint in migration 0002 instead.
"""

CLASH = """
    SELECT RAISE(ABORT, 'event_no_overlap_in_space') WHERE EXISTS (
        SELECT 1 FROM events_event e
        WHERE e.space_id = NEW.space_id AND e.status = 'approved' AND e.id IS NOT NEW.id
          AND julianday(e."start") < julianday(NEW."end") AND julianday(e."end") > julianday(NEW."start")
    );
"""
TRIGGERS = [
    f"""CREATE TRIGGER IF NOT EXISTS event_no_overlap_insert BEFORE INSERT ON events_event
        WHEN NEW.status = 'approved' BEGIN {CLASH} END""",
    f"""CREATE TRIGGER IF NOT EXISTS event_no_overlap_update BEFORE UPDATE ON events_event
        WHEN NEW.status = 'approved' BEGIN {CLASH} END""",
]


def ensure_sqlite_overlap_guard(connection):
    if connection.vendor != "sqlite" or "events_event" not in connection.introspection.table_names():
        return
    with connection.cursor() as cursor:
        for sql in TRIGGERS:
            cursor.execute(sql)


def on_post_migrate(using, **kwargs):
    from django.db import connections

    ensure_sqlite_overlap_guard(connections[using])
