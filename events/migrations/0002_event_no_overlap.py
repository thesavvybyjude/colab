"""Database guard: no two approved events may overlap in the same space.

PostgreSQL: an exclusion constraint, created here. SQLite: triggers, created by a post_migrate
handler in events/db_guards.py so they come back after Django rebuilds the table.
"""

from django.db import migrations

PG_FORWARD = [
    "CREATE EXTENSION IF NOT EXISTS btree_gist",
    """ALTER TABLE events_event ADD CONSTRAINT event_no_overlap_in_space
       EXCLUDE USING gist (space_id WITH =, tstzrange("start", "end") WITH &&)
       WHERE (status = 'approved')""",
]
PG_REVERSE = ["ALTER TABLE events_event DROP CONSTRAINT event_no_overlap_in_space"]
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
            run({"postgresql": PG_FORWARD, "sqlite": []}),
            run({"postgresql": PG_REVERSE, "sqlite": SQLITE_REVERSE}),
        ),
    ]
