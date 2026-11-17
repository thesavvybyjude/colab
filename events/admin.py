from django.contrib import admin
from django.db import IntegrityError

from .models import Event, Space


class ColabAdminOnly:
    """Only CoLab admins (role admin or superuser) may see or change these records."""

    def _allowed(self, request):
        return request.user.is_active and request.user.is_colab_admin

    def has_module_permission(self, request):
        return self._allowed(request)

    def has_view_permission(self, request, obj=None):
        return self._allowed(request)

    def has_add_permission(self, request):
        return self._allowed(request)

    def has_change_permission(self, request, obj=None):
        return self._allowed(request)

    def has_delete_permission(self, request, obj=None):
        return self._allowed(request)


@admin.register(Space)
class SpaceAdmin(ColabAdminOnly, admin.ModelAdmin):
    list_display = ("name", "capacity")


@admin.register(Event)
class EventAdmin(ColabAdminOnly, admin.ModelAdmin):
    list_display = ("title", "space", "start", "end", "status")
    list_filter = ("status", "space")
    search_fields = ("title", "host_name")
    list_select_related = ("space",)

    def changeform_view(self, request, *args, **kwargs):
        try:
            return super().changeform_view(request, *args, **kwargs)
        except IntegrityError:
            # Another admin saved a clashing event between our form check and our save. The failed
            # save was rolled back; running the form again now finds that event and names it.
            return super().changeform_view(request, *args, **kwargs)
