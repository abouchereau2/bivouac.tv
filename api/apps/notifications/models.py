from django.conf import settings
from django.db import models


class Notification(models.Model):
    """User notification for submission status updates and other events."""

    class NotificationType(models.TextChoices):
        # Pending (user submitted something)
        SUBMISSION_PENDING = "submission_pending", "Submission Pending"
        LINK_SUGGESTION_PENDING = "link_suggestion_pending", "Link Suggestion Pending"
        LINK_REPORT_PENDING = "link_report_pending", "Link Report Pending"
        # Resolved (admin reviewed)
        SUBMISSION_APPROVED = "submission_approved", "Submission Approved"
        SUBMISSION_REJECTED = "submission_rejected", "Submission Rejected"
        LINK_SUGGESTION_APPROVED = "link_suggestion_approved", "Link Suggestion Approved"
        LINK_SUGGESTION_REJECTED = "link_suggestion_rejected", "Link Suggestion Rejected"
        LINK_REPORT_FIXED = "link_report_fixed", "Link Report Fixed"
        LINK_REPORT_DISMISSED = "link_report_dismissed", "Link Report Dismissed"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        RESOLVED = "resolved", "Resolved"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )

    # Related object info (for linking to the relevant item)
    submission = models.ForeignKey(
        "submissions.Submission",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications"
    )
    link_suggestion = models.ForeignKey(
        "submissions.LinkSuggestion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications"
    )
    link_report = models.ForeignKey(
        "submissions.LinkReport",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications"
    )

    # Additional context
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    # Denormalized documentary info (stored at creation time to survive deletions)
    documentary_title = models.CharField(max_length=255, blank=True)
    documentary_slug = models.CharField(max_length=255, blank=True)
    documentary_poster = models.URLField(blank=True)

    # Status (pending review vs resolved)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Read status
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.notification_type} - {'read' if self.read else 'unread'}"
