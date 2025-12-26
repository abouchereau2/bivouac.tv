from django.contrib import admin
from django.utils import timezone

from .models import LinkReport, LinkSuggestion, Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["title", "year", "submitted_by", "status", "created_at", "reviewed_by"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "submitted_by__email"]
    readonly_fields = ["submitted_by", "created_at", "updated_at", "reviewed_at"]
    autocomplete_fields = ["reviewed_by", "created_documentary"]

    fieldsets = [
        ("Submission", {
            "fields": ["submitted_by", "title", "year", "url", "notes", "created_at"]
        }),
        ("Review", {
            "fields": ["status", "reviewed_by", "review_notes", "reviewed_at"]
        }),
        ("Result", {
            "fields": ["created_documentary"],
            "classes": ["collapse"]
        }),
    ]

    actions = ["approve_submissions", "reject_submissions"]

    def approve_submissions(self, request, queryset):
        count = queryset.filter(status=Submission.Status.PENDING).update(
            status=Submission.Status.APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f"{count} submission(s) approved.")
    approve_submissions.short_description = "Approve selected submissions"

    def reject_submissions(self, request, queryset):
        count = queryset.filter(status=Submission.Status.PENDING).update(
            status=Submission.Status.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f"{count} submission(s) rejected.")
    reject_submissions.short_description = "Reject selected submissions"


@admin.register(LinkSuggestion)
class LinkSuggestionAdmin(admin.ModelAdmin):
    list_display = ["documentary", "platform", "submitted_by", "status", "created_at"]
    list_filter = ["status", "platform", "created_at"]
    search_fields = ["documentary__title", "submitted_by__email", "url"]
    readonly_fields = ["submitted_by", "created_at", "updated_at", "reviewed_at"]
    autocomplete_fields = ["documentary", "platform", "reviewed_by"]

    fieldsets = [
        ("Suggestion", {
            "fields": ["submitted_by", "documentary", "platform", "url", "is_free", "notes", "created_at"]
        }),
        ("Review", {
            "fields": ["status", "reviewed_by", "review_notes", "reviewed_at"]
        }),
    ]

    actions = ["approve_suggestions", "reject_suggestions"]

    def approve_suggestions(self, request, queryset):
        from apps.documentaries.models import Availability

        approved_count = 0
        for suggestion in queryset.filter(status=LinkSuggestion.Status.PENDING):
            Availability.objects.update_or_create(
                documentary=suggestion.documentary,
                platform=suggestion.platform,
                defaults={
                    "url": suggestion.url,
                    "is_free": suggestion.is_free,
                }
            )
            suggestion.status = LinkSuggestion.Status.APPROVED
            suggestion.reviewed_by = request.user
            suggestion.reviewed_at = timezone.now()
            suggestion.save()
            approved_count += 1

        self.message_user(request, f"{approved_count} suggestion(s) approved and availability created.")
    approve_suggestions.short_description = "Approve selected suggestions"

    def reject_suggestions(self, request, queryset):
        count = queryset.filter(status=LinkSuggestion.Status.PENDING).update(
            status=LinkSuggestion.Status.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f"{count} suggestion(s) rejected.")
    reject_suggestions.short_description = "Reject selected suggestions"


@admin.register(LinkReport)
class LinkReportAdmin(admin.ModelAdmin):
    list_display = ["get_documentary_display", "platform_name", "reason", "reported_by", "status", "created_at"]
    list_filter = ["status", "reason", "created_at"]
    search_fields = ["documentary_title", "reported_by__email", "details"]
    readonly_fields = ["reported_by", "documentary_title", "documentary_slug", "platform_name", "created_at", "resolved_at"]
    autocomplete_fields = ["availability", "resolved_by"]

    fieldsets = [
        ("Report", {
            "fields": ["reported_by", "documentary_title", "platform_name", "availability", "reason", "details", "created_at"]
        }),
        ("Resolution", {
            "fields": ["status", "resolved_by", "resolution_notes", "resolved_at"]
        }),
    ]

    actions = ["mark_as_fixed", "dismiss_reports"]

    @admin.display(description="Documentary")
    def get_documentary_display(self, obj):
        return obj.documentary_title or "-"

    def mark_as_fixed(self, request, queryset):
        count = queryset.filter(status=LinkReport.Status.PENDING).update(
            status=LinkReport.Status.FIXED,
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f"{count} report(s) marked as fixed.")
    mark_as_fixed.short_description = "Mark selected as fixed"

    def dismiss_reports(self, request, queryset):
        count = queryset.filter(status=LinkReport.Status.PENDING).update(
            status=LinkReport.Status.DISMISSED,
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f"{count} report(s) dismissed.")
    dismiss_reports.short_description = "Dismiss selected reports"
