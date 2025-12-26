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
    """Create notification when a submission is created or reviewed."""
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
        # Admin reviewed - update existing pending notification to resolved
        Notification.objects.filter(
            submission=instance,
            notification_type=Notification.NotificationType.SUBMISSION_PENDING,
            status=Notification.Status.PENDING,
        ).update(status=Notification.Status.RESOLVED)

        # Create new notification for the result
        doc = instance.created_documentary
        if instance.status == Submission.Status.APPROVED:
            Notification.objects.create(
                user=instance.submitted_by,
                notification_type=Notification.NotificationType.SUBMISSION_APPROVED,
                submission=instance,
                status=Notification.Status.RESOLVED,
                title=f'Your submission "{instance.title}" was approved!',
                message=instance.review_notes or "Your documentary suggestion has been added to the database.",
                documentary_title=instance.title,
                documentary_slug=doc.slug if doc else "",
                documentary_poster=_get_poster_url(doc),
            )
        else:
            Notification.objects.create(
                user=instance.submitted_by,
                notification_type=Notification.NotificationType.SUBMISSION_REJECTED,
                submission=instance,
                status=Notification.Status.RESOLVED,
                title=f'Your submission "{instance.title}" was not accepted',
                message=instance.review_notes or "Thank you for your suggestion.",
                documentary_title=instance.title,
            )


@receiver(post_save, sender=LinkSuggestion)
def create_link_suggestion_notification(sender, instance, created, **kwargs):
    """Create notification when a link suggestion is created or reviewed."""
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
        # Admin reviewed - update existing pending notification to resolved
        Notification.objects.filter(
            link_suggestion=instance,
            notification_type=Notification.NotificationType.LINK_SUGGESTION_PENDING,
            status=Notification.Status.PENDING,
        ).update(status=Notification.Status.RESOLVED)

        # Create new notification for the result
        if instance.status == LinkSuggestion.Status.APPROVED:
            Notification.objects.create(
                user=instance.submitted_by,
                notification_type=Notification.NotificationType.LINK_SUGGESTION_APPROVED,
                link_suggestion=instance,
                status=Notification.Status.RESOLVED,
                title=f'Your link suggestion for "{doc_title}" was approved!',
                message=instance.review_notes or "The streaming link has been added.",
                documentary_title=doc_title,
                documentary_slug=doc.slug if doc else "",
                documentary_poster=_get_poster_url(doc),
            )
        else:
            Notification.objects.create(
                user=instance.submitted_by,
                notification_type=Notification.NotificationType.LINK_SUGGESTION_REJECTED,
                link_suggestion=instance,
                status=Notification.Status.RESOLVED,
                title=f'Your link suggestion for "{doc_title}" was not accepted',
                message=instance.review_notes or "Thank you for your suggestion.",
                documentary_title=doc_title,
                documentary_slug=doc.slug if doc else "",
                documentary_poster=_get_poster_url(doc),
            )


@receiver(post_save, sender=LinkReport)
def create_link_report_notification(sender, instance, created, **kwargs):
    """Create notification when a link report is created or resolved."""
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
        # Admin reviewed - update existing pending notification to resolved
        Notification.objects.filter(
            link_report=instance,
            notification_type=Notification.NotificationType.LINK_REPORT_PENDING,
            status=Notification.Status.PENDING,
        ).update(status=Notification.Status.RESOLVED)

        # Get poster from pending notification if availability was deleted
        if not doc_poster:
            pending_notif = Notification.objects.filter(
                link_report=instance,
                notification_type=Notification.NotificationType.LINK_REPORT_PENDING,
            ).first()
            if pending_notif:
                doc_poster = pending_notif.documentary_poster

        # Create new notification for the result
        if instance.status == LinkReport.Status.FIXED:
            Notification.objects.create(
                user=instance.reported_by,
                notification_type=Notification.NotificationType.LINK_REPORT_FIXED,
                link_report=instance,
                status=Notification.Status.RESOLVED,
                title=f'Your link report for "{doc_title}" was resolved',
                message=instance.resolution_notes or "The broken link has been removed. Thank you for reporting!",
                documentary_title=doc_title,
                documentary_slug=doc_slug,
                documentary_poster=doc_poster,
            )
        else:
            Notification.objects.create(
                user=instance.reported_by,
                notification_type=Notification.NotificationType.LINK_REPORT_DISMISSED,
                link_report=instance,
                status=Notification.Status.RESOLVED,
                title=f'Your link report for "{doc_title}" was reviewed',
                message=instance.resolution_notes or "After review, the link appears to be working.",
                documentary_title=doc_title,
                documentary_slug=doc_slug,
                documentary_poster=doc_poster,
            )
