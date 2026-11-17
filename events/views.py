from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    """Public page: what's happening at CoLab. Events arrive in Slice 1."""
    return render(request, "events/home.html", {"events": []})


def healthz(request):
    """For the host's health check: is the app up and can it reach the database?"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "error", "database": "unreachable"}, status=503)
    return JsonResponse({"status": "ok"})
