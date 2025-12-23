from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "documentary", "rating", "created_at", "content_preview"]
    list_filter = ["rating", "created_at"]
    search_fields = ["user__email", "documentary__title", "content"]
    autocomplete_fields = ["user", "documentary"]
    readonly_fields = ["created_at", "updated_at"]

    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return "-"
    content_preview.short_description = "Review"
