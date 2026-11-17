from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A person with a CoLab account. The public never needs one."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        HOST = "host", "Host"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.HOST)
    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_colab_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def save(self, *args, **kwargs):
        # Admin-site access follows the role both ways: making someone a host removes it.
        self.is_staff = self.is_colab_admin
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "role" in update_fields:
            kwargs["update_fields"] = {*update_fields, "is_staff"}
        super().save(*args, **kwargs)
