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


class LinkSuggestion(models.Model):
    """User-suggested streaming link for an existing documentary."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    documentary = models.ForeignKey(
        "documentaries.Documentary",
        on_delete=models.CASCADE,
        related_name="link_suggestions"
    )
    platform = models.ForeignKey(
        "documentaries.Platform",
        on_delete=models.CASCADE,
        related_name="link_suggestions"
    )
    url = models.URLField(help_text="Direct link to watch the documentary")
    is_free = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="Additional notes")

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="link_suggestions"
    )

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
        related_name="reviewed_link_suggestions"
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.documentary.title} - {self.platform.name} ({self.status})"


class LinkReport(models.Model):
    """User report for a broken or incorrect streaming link."""

    class Reason(models.TextChoices):
        BROKEN = "broken", "Link is broken"
        GEO_RESTRICTED = "geo_restricted", "Geo-restricted in my country"
        PAYWALL = "paywall", "Now requires payment"
        WRONG_CONTENT = "wrong_content", "Links to wrong content"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        FIXED = "fixed", "Fixed"
        DISMISSED = "dismissed", "Dismissed"

    availability = models.ForeignKey(
        "documentaries.Availability",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports"
    )
    reason = models.CharField(
        max_length=20,
        choices=Reason.choices,
    )
    details = models.TextField(blank=True, help_text="Additional details about the issue")

    # Denormalized documentary info (stored at creation to survive availability deletion)
    documentary_title = models.CharField(max_length=255, blank=True)
    documentary_slug = models.CharField(max_length=255, blank=True)
    platform_name = models.CharField(max_length=100, blank=True)

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="link_reports"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_link_reports"
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        doc_info = self.documentary_title or (self.availability.documentary.title if self.availability and self.availability.documentary else "Unknown")
        return f"Report: {doc_info} - {self.reason} ({self.status})"
