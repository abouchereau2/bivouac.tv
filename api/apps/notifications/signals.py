from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.submissions.models import LinkReport, LinkSuggestion, Submission

from .models import Notification


def _get_poster_url(documentary):
    """Get absolute URL for documentary poster."""
    if documentary and documentary.poster:
        return documentary.poster.url
    return ""


@receiver(post_save, sender=Submission)
def create_submission_notification(sender, instance, created, **kwargs):
    """Create notification when a submission is created or update it when reviewed."""
    if created:
        # User submitted a new documentary - create pending notification
        Notification.objects.create(
            user=instance.submitted_by,
            notification_type=Notification.NotificationType.SUBMISSION_PENDING,
            submission=instance,
            status=Notification.Status.PENDING,
            title=f'Submission "{instance.title}" is pending review',
            message="Your documentary suggestion has been received and is awaiting moderation.",
            documentary_title=instance.title,
        )
    elif instance.status in [Submission.Status.APPROVED, Submission.Status.REJECTED]:
        # Admin reviewed - update existing pending notification in place
        doc = instance.created_documentary
        notification = Notification.objects.filter(
            submission=instance,
            notification_type=Notification.NotificationType.SUBMISSION_PENDING,
        ).first()

        if notification:
            if instance.status == Submission.Status.APPROVED:
                notification.notification_type = Notification.NotificationType.SUBMISSION_APPROVED
                notification.title = f'Your submission "{instance.title}" was approved!'
                notification.message = instance.review_notes or "Your documentary suggestion has been added to the database."
                notification.documentary_slug = doc.slug if doc else ""
                notification.documentary_poster = _get_poster_url(doc)
            else:
                notification.notification_type = Notification.NotificationType.SUBMISSION_REJECTED
                notification.title = f'Your submission "{instance.title}" was not accepted'
                notification.message = instance.review_notes or "Thank you for your suggestion."

            notification.status = Notification.Status.RESOLVED
            notification.read = False  # Reset read status to trigger new alert
            notification.read_at = None
            notification.save()


@receiver(post_save, sender=LinkSuggestion)
def create_link_suggestion_notification(sender, instance, created, **kwargs):
    """Create notification when a link suggestion is created or update it when reviewed."""
    doc = instance.documentary
    doc_title = doc.title if doc else "Documentary"

    if created:
        # User submitted a new link suggestion - create pending notification
        Notification.objects.create(
            user=instance.submitted_by,
            notification_type=Notification.NotificationType.LINK_SUGGESTION_PENDING,
            link_suggestion=instance,
            status=Notification.Status.PENDING,
            title=f'Link suggestion for "{doc_title}" is pending review',
            message="Your streaming link suggestion has been received and is awaiting moderation.",
            documentary_title=doc_title,
            documentary_slug=doc.slug if doc else "",
            documentary_poster=_get_poster_url(doc),
        )
    elif instance.status in [LinkSuggestion.Status.APPROVED, LinkSuggestion.Status.REJECTED]:
        # Admin reviewed - update existing pending notification in place
        notification = Notification.objects.filter(
            link_suggestion=instance,
            notification_type=Notification.NotificationType.LINK_SUGGESTION_PENDING,
        ).first()

        if notification:
            if instance.status == LinkSuggestion.Status.APPROVED:
                notification.notification_type = Notification.NotificationType.LINK_SUGGESTION_APPROVED
                notification.title = f'Your link suggestion for "{doc_title}" was approved!'
                notification.message = instance.review_notes or "The streaming link has been added."
            else:
                notification.notification_type = Notification.NotificationType.LINK_SUGGESTION_REJECTED
                notification.title = f'Your link suggestion for "{doc_title}" was not accepted'
                notification.message = instance.review_notes or "Thank you for your suggestion."

            notification.status = Notification.Status.RESOLVED
            notification.read = False  # Reset read status to trigger new alert
            notification.read_at = None
            notification.save()


@receiver(post_save, sender=LinkReport)
def create_link_report_notification(sender, instance, created, **kwargs):
    """Create notification when a link report is created or update it when resolved."""
    # Use denormalized fields from LinkReport (they survive availability deletion)
    doc_title = instance.documentary_title or "the documentary"
    doc_slug = instance.documentary_slug or ""

    # Get poster from documentary if still available
    doc = None
    if instance.availability and instance.availability.documentary:
        doc = instance.availability.documentary
    doc_poster = _get_poster_url(doc)

    if created:
        # User submitted a new link report - create pending notification
        Notification.objects.create(
            user=instance.reported_by,
            notification_type=Notification.NotificationType.LINK_REPORT_PENDING,
            link_report=instance,
            status=Notification.Status.PENDING,
            title=f'Link report for "{doc_title}" is pending review',
            message="Your link report has been received and is awaiting moderation.",
            documentary_title=doc_title,
            documentary_slug=doc_slug,
            documentary_poster=doc_poster,
        )
    elif instance.status in [LinkReport.Status.FIXED, LinkReport.Status.DISMISSED]:
        # Admin reviewed - update existing pending notification in place
        notification = Notification.objects.filter(
            link_report=instance,
            notification_type=Notification.NotificationType.LINK_REPORT_PENDING,
        ).first()

        if notification:
            # Use poster from existing notification if availability was deleted
            if not doc_poster:
                doc_poster = notification.documentary_poster

            if instance.status == LinkReport.Status.FIXED:
                notification.notification_type = Notification.NotificationType.LINK_REPORT_FIXED
                notification.title = f'Your link report for "{doc_title}" was resolved'
                notification.message = instance.resolution_notes or "The broken link has been removed. Thank you for reporting!"
            else:
                notification.notification_type = Notification.NotificationType.LINK_REPORT_DISMISSED
                notification.title = f'Your link report for "{doc_title}" was reviewed'
                notification.message = instance.resolution_notes or "After review, the link appears to be working."

            notification.documentary_poster = doc_poster
            notification.status = Notification.Status.RESOLVED
            notification.read = False  # Reset read status to trigger new alert
            notification.read_at = None
            notification.save()
