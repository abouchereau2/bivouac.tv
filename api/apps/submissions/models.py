from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Submission(models.Model):
    """User-submitted documentary suggestion."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    # Submitted by
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    # Documentary info
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    url = models.URLField(help_text="Link to trailer or streaming platform")
    notes = models.TextField(blank=True, help_text="Additional information about the documentary")

    # Moderation
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_submissions"
    )
    review_notes = models.TextField(blank=True, help_text="Notes from the reviewer")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Link to created documentary (if approved)
    created_documentary = models.OneToOneField(
        "documentaries.Documentary",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="from_submission"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.year}) - {self.status}"
