"""Database guard: no two approved events may overlap in the same space.

PostgreSQL uses an exclusion constraint. SQLite has none, so it uses triggers.
shortcut: Django rebuilds SQLite tables on some later ALTERs, which drops these triggers; the
test_database_refuses_* tests catch that, and a later migration must recreate them if it happens.
"""

from django.db import migrations

PG_FORWARD = [
    "CREATE EXTENSION IF NOT EXISTS btree_gist",
    """ALTER TABLE events_event ADD CONSTRAINT event_no_overlap_in_space
       EXCLUDE USING gist (space_id WITH =, tstzrange("start", "end") WITH &&)
       WHERE (status = 'approved')""",
]
PG_REVERSE = ["ALTER TABLE events_event DROP CONSTRAINT event_no_overlap_in_space"]

SQLITE_CLASH = """
    SELECT RAISE(ABORT, 'event_no_overlap_in_space') WHERE EXISTS (
        SELECT 1 FROM events_event e
        WHERE e.space_id = NEW.space_id AND e.status = 'approved' AND e.id IS NOT NEW.id
          AND julianday(e."start") < julianday(NEW."end") AND julianday(e."end") > julianday(NEW."start")
    );
"""
SQLITE_FORWARD = [
    f"""CREATE TRIGGER event_no_overlap_insert BEFORE INSERT ON events_event
        WHEN NEW.status = 'approved' BEGIN {SQLITE_CLASH} END""",
    f"""CREATE TRIGGER event_no_overlap_update BEFORE UPDATE ON events_event
        WHEN NEW.status = 'approved' BEGIN {SQLITE_CLASH} END""",
]
SQLITE_REVERSE = [
    "DROP TRIGGER IF EXISTS event_no_overlap_insert",
    "DROP TRIGGER IF EXISTS event_no_overlap_update",
]


def run(statements):
    def apply(apps, schema_editor):
        vendor = schema_editor.connection.vendor
        if vendor not in statements:
            raise RuntimeError(f"No event overlap guard for database '{vendor}'.")
        for sql in statements[vendor]:
            schema_editor.execute(sql)

    return apply


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            run({"postgresql": PG_FORWARD, "sqlite": SQLITE_FORWARD}),
            run({"postgresql": PG_REVERSE, "sqlite": SQLITE_REVERSE}),
        ),
    ]
