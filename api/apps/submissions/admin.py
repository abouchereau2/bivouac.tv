from django.contrib import admin
from django.utils import timezone

from .models import Submission


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
