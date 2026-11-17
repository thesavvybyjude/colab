"""Error pages and admin branding."""

import pytest
from django.template.loader import render_to_string
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_unknown_page_shows_colab_404_with_link_home(client, settings):
    settings.DEBUG = False  # the debug 404 page hides the real template
    response = client.get("/events/99999/")
    page = response.content.decode()
    assert response.status_code == 404
    assert "Page not found" in page
    assert f'href="{reverse("home")}"' in page


def test_500_page_renders_without_request_context():
    page = render_to_string("500.html")
    assert "Something went wrong" in page
    assert f'href="{reverse("home")}"' in page


def test_admin_shows_colab_header_and_programme_section(client, django_user_model):
    user = django_user_model.objects.create_user(username="ada", password="x", role="admin")
    client.force_login(user)
    page = client.get(reverse("admin:index")).content.decode()
    assert "CoLab admin" in page
    assert "Manage CoLab Jos" in page
    assert "Programme" in page
