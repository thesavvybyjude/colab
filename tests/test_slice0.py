import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_home_is_public_and_says_what_it_is(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert "What's happening at CoLab" in response.content.decode()


def test_home_shows_empty_state_when_no_events(client):
    response = client.get(reverse("home"))
    assert "No upcoming events yet" in response.content.decode()


def test_healthz_reports_ok_with_database(client):
    response = client.get(reverse("healthz"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_admin_requires_sign_in(client):
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


def test_staff_can_sign_in(client, django_user_model):
    django_user_model.objects.create_user(username="ada", password="a-long-test-password", role="admin")
    response = client.post(reverse("login"), {"username": "ada", "password": "a-long-test-password"})
    assert response.status_code == 302
    assert response["Location"] == reverse("home")


def test_new_users_default_to_host_role(django_user_model):
    user = django_user_model.objects.create_user(username="lily", password="x")
    assert user.role == "host"
    assert not user.is_colab_admin
