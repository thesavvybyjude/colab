from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Event


def home(request):
    """Public page: approved events that haven't ended yet, soonest first."""
    events = Event.objects.filter(status=Event.Status.APPROVED, end__gt=timezone.now()).select_related(
        "space"
    )
    return render(request, "events/home.html", {"events": events})


def event_detail(request, pk):
    """Shareable public page for one approved event."""
    event = get_object_or_404(Event.objects.select_related("space"), pk=pk, status=Event.Status.APPROVED)
    return render(request, "events/detail.html", {"event": event})


def healthz(request):
    """For the host's health check: is the app up and can it reach the database?"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "error", "database": "unreachable"}, status=503)
    return JsonResponse({"status": "ok"})
