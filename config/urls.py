from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from events import views as event_views

urlpatterns = [
    path("", event_views.home, name="home"),
    path("healthz", event_views.healthz, name="healthz"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]
