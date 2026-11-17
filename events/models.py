from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Space(models.Model):
    """A bookable room or area at the hub."""

    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        CHANGES_REQUESTED = "changes_requested", "Changes requested"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=200)
    description = models.TextField()
    space = models.ForeignKey(Space, on_delete=models.PROTECT, related_name="events")
    start = models.DateTimeField()
    end = models.DateTimeField()
    host_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["start"]
        # The no-overlap rule for approved events lives in migration 0002 (database-specific SQL).
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end__gt=models.F("start")),
                name="event_end_after_start",
                violation_error_message="End must be after start.",
            )
        ]

    def __str__(self):
        return self.title

    @property
    def when(self):
        start, end = timezone.localtime(self.start), timezone.localtime(self.end)
        if start.date() == end.date():
            return f"{start:%a %d %b %Y, %H:%M}–{end:%H:%M}"
        return f"{start:%a %d %b %Y, %H:%M} – {end:%a %d %b %Y, %H:%M}"

    @property
    def has_ended(self):
        return self.end <= timezone.now()

    def find_clash(self):
        """The first approved event in the same space whose time overlaps this one, if any."""
        return (
            Event.objects.filter(
                space_id=self.space_id, status=self.Status.APPROVED, start__lt=self.end, end__gt=self.start
            )
            .exclude(pk=self.pk)
            .first()
        )

    def clean(self):
        if self.status != self.Status.APPROVED or not (self.space_id and self.start and self.end):
            return
        if self.end > self.start and (clash := self.find_clash()):
            raise ValidationError(f"Clashes with “{clash.title}” in {clash.space} ({clash.when}).")
