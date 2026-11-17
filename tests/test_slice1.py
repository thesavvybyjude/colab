"""User Story 1: staff publish an event and the public sees it."""

from datetime import timedelta
from unittest import mock

import pytest
from django.db import IntegrityError, connection, transaction
from django.urls import reverse
from django.utils import timezone

from events.db_guards import ensure_sqlite_overlap_guard
from events.models import Event, Space

pytestmark = pytest.mark.django_db


@pytest.fixture
def space():
    return Space.objects.create(name="Main hall")


@pytest.fixture
def admin_client(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="ada", password="a-long-test-password", role="admin"
    )
    client.force_login(user)
    return client


def at(days, hour, minute=0):
    """A Lagos-time datetime `days` from today at hour:minute."""
    day = timezone.localtime() + timedelta(days=days)
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def make_event(space, start, end, status=Event.Status.APPROVED, title="Design Jam"):
    return Event.objects.create(
        title=title,
        description="Bring a laptop.",
        space=space,
        start=start,
        end=end,
        host_name="Lily",
        status=status,
    )


def admin_form(space, start, end, title="Design Jam", status="approved"):
    """POST data for the Django admin event form (split date/time widgets, en-GB dates)."""
    return {
        "title": title,
        "description": "Bring a laptop.",
        "space": space.pk,
        "start_0": start.strftime("%d/%m/%Y"),
        "start_1": start.strftime("%H:%M"),
        "end_0": end.strftime("%d/%m/%Y"),
        "end_1": end.strftime("%H:%M"),
        "host_name": "Lily",
        "status": status,
    }


# Scenario 1
def test_admin_publishes_event_and_it_appears_on_public_page(admin_client, client, space):
    response = admin_client.post(
        reverse("admin:events_event_add"), admin_form(space, at(3, 10), at(3, 12), title="Robotics Meetup")
    )
    assert response.status_code == 302, response.content.decode()[:2000]

    admin_client.logout()
    page = client.get(reverse("home")).content.decode()
    assert "Robotics Meetup" in page
    assert "Main hall" in page
    assert "10:00" in page

    event = Event.objects.get(title="Robotics Meetup")
    detail = client.get(reverse("event_detail", args=[event.pk]))
    assert detail.status_code == 200
    assert "Bring a laptop." in detail.content.decode()


# Scenario 2
def test_admin_changes_time_and_public_page_shows_new_time(admin_client, client, space):
    event = make_event(space, at(3, 10), at(3, 12))
    response = admin_client.post(
        reverse("admin:events_event_change", args=[event.pk]), admin_form(space, at(3, 14, 30), at(3, 16))
    )
    assert response.status_code == 302, response.content.decode()[:2000]

    admin_client.logout()
    page = client.get(reverse("event_detail", args=[event.pk])).content.decode()
    assert "14:30" in page
    assert "10:00" not in page


# Scenario 3
def test_overlapping_event_in_same_space_is_refused_and_names_clash(admin_client, space):
    make_event(space, at(3, 10), at(3, 12), title="Design Jam")
    response = admin_client.post(
        reverse("admin:events_event_add"), admin_form(space, at(3, 11), at(3, 13), title="Pitch Night")
    )
    assert response.status_code == 200
    assert "Design Jam" in response.content.decode()
    assert not Event.objects.filter(title="Pitch Night").exists()


def test_simultaneous_clashing_save_shows_clash_message_not_crash(admin_client, space):
    """Two admins pass the form check at once; the database refuses one and the form says why."""
    make_event(space, at(3, 10), at(3, 12), title="Design Jam")
    real_find_clash = Event.find_clash
    calls = []

    def first_check_misses(self):
        calls.append(1)
        return None if len(calls) == 1 else real_find_clash(self)

    with mock.patch.object(Event, "find_clash", first_check_misses):
        response = admin_client.post(
            reverse("admin:events_event_add"), admin_form(space, at(3, 11), at(3, 13), title="Pitch Night")
        )
    assert response.status_code == 200
    assert "Design Jam" in response.content.decode()
    assert not Event.objects.filter(title="Pitch Night").exists()


def test_database_refuses_overlapping_approved_events(space):
    make_event(space, at(3, 10), at(3, 12))
    with pytest.raises(IntegrityError), transaction.atomic():
        make_event(space, at(3, 11), at(3, 13), title="Pitch Night")


def test_database_refuses_moving_an_approved_event_onto_another(space):
    make_event(space, at(3, 10), at(3, 12))
    other = make_event(space, at(3, 14), at(3, 16), title="Pitch Night")
    other.start, other.end = at(3, 11), at(3, 13)
    with pytest.raises(IntegrityError), transaction.atomic():
        other.save()


def test_overlap_allowed_in_other_space_back_to_back_or_as_draft(space):
    other_space = Space.objects.create(name="Studio")
    make_event(space, at(3, 10), at(3, 12))
    make_event(other_space, at(3, 10), at(3, 12), title="Other room")
    make_event(space, at(3, 12), at(3, 14), title="Right after")
    make_event(space, at(3, 11), at(3, 13), title="Just a draft", status=Event.Status.DRAFT)
    assert Event.objects.count() == 4


# Scenario 4
def test_event_whose_end_has_passed_is_not_in_upcoming_list(client, space):
    make_event(space, at(-2, 10), at(-2, 12), title="Last Week Thing")
    make_event(space, at(3, 10), at(3, 12), title="Future Thing")
    page = client.get(reverse("home")).content.decode()
    assert "Last Week Thing" not in page
    assert "Future Thing" in page


def test_upcoming_list_is_soonest_first_and_hides_unapproved(client, space):
    make_event(space, at(5, 10), at(5, 12), title="Later One")
    make_event(space, at(2, 10), at(2, 12), title="Sooner One")
    make_event(space, at(3, 10), at(3, 12), title="Secret Draft", status=Event.Status.DRAFT)
    page = client.get(reverse("home")).content.decode()
    assert page.index("Sooner One") < page.index("Later One")
    assert "Secret Draft" not in page


def test_unapproved_event_has_no_public_page(client, space):
    draft = make_event(space, at(3, 10), at(3, 12), status=Event.Status.DRAFT)
    assert client.get(reverse("event_detail", args=[draft.pk])).status_code == 404


# Scenario 5
def test_visitor_not_signed_in_is_sent_to_sign_in_from_admin_screens(client, space):
    event = make_event(space, at(3, 10), at(3, 12), title="Hidden From Visitors")
    for url in (
        reverse("admin:events_event_changelist"),
        reverse("admin:events_event_add"),
        reverse("admin:events_event_change", args=[event.pk]),
        reverse("admin:events_space_changelist"),
    ):
        response = client.get(url)
        assert response.status_code == 302, url
        assert "/admin/login/" in response["Location"]
        assert "Hidden From Visitors" not in response.content.decode()


def test_host_role_cannot_open_event_admin(client, django_user_model, space):
    host = django_user_model.objects.create_user(username="lily", password="x", role="host")
    # Bypass save() so the staff flag is on: only the role check in ColabAdminOnly stands in the way.
    django_user_model.objects.filter(pk=host.pk).update(is_staff=True)
    client.force_login(host)
    for url in (
        reverse("admin:events_event_changelist"),
        reverse("admin:events_event_add"),
        reverse("admin:events_space_changelist"),
    ):
        assert client.get(url).status_code == 403, url


def test_admin_role_gets_admin_access_and_loses_it_when_made_host(client, django_user_model):
    user = django_user_model.objects.create_user(username="ada", password="x", role="admin")
    assert user.is_staff
    client.force_login(user)
    assert client.get(reverse("admin:events_event_changelist")).status_code == 200

    user.role = "host"
    user.save()
    user.refresh_from_db()
    assert not user.is_staff
    assert client.get(reverse("admin:events_event_changelist")).status_code == 302


def test_demoting_with_update_fields_role_removes_admin_access(client, django_user_model):
    user = django_user_model.objects.create_user(username="ada", password="x", role="admin")
    client.force_login(user)
    user.role = "host"
    user.save(update_fields=["role"])
    user.refresh_from_db()
    assert not user.is_staff
    assert client.get(reverse("admin:events_event_changelist")).status_code == 302


@pytest.mark.skipif(connection.vendor != "sqlite", reason="SQLite trigger guard only")
def test_sqlite_overlap_guard_heals_after_triggers_are_dropped(space):
    with connection.cursor() as cursor:
        cursor.execute("DROP TRIGGER event_no_overlap_insert")
        cursor.execute("DROP TRIGGER event_no_overlap_update")
    ensure_sqlite_overlap_guard(connection)
    make_event(space, at(3, 10), at(3, 12))
    with pytest.raises(IntegrityError), transaction.atomic():
        make_event(space, at(3, 11), at(3, 13), title="Pitch Night")
