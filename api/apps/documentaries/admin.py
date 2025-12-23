from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Availability,
    Documentary,
    Person,
    Platform,
    Region,
    Sport,
    Theme,
    Watchlist,
)


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "icon"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_free", "website"]
    list_filter = ["is_free"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1
    autocomplete_fields = ["platform"]


@admin.register(Documentary)
class DocumentaryAdmin(admin.ModelAdmin):
    list_display = [
        "title", "year", "duration_display", "is_published", "is_featured",
        "sports_display", "poster_preview"
    ]
    list_filter = ["is_published", "is_featured", "year", "sports", "themes"]
    search_fields = ["title", "original_title", "synopsis"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["directors", "sports", "themes", "regions"]
    inlines = [AvailabilityInline]

    fieldsets = [
        (None, {
            "fields": ["title", "original_title", "slug", "year", "duration_minutes"]
        }),
        ("Content", {
            "fields": ["synopsis", "poster", "backdrop", "trailer_url"]
        }),
        ("Relations", {
            "fields": ["directors", "sports", "themes", "regions"]
        }),
        ("External IDs", {
            "fields": ["imdb_id", "imdb_rating", "tmdb_id"],
            "classes": ["collapse"]
        }),
        ("Status", {
            "fields": ["is_published", "is_featured"]
        }),
    ]

    def duration_display(self, obj):
        hours, minutes = divmod(obj.duration_minutes, 60)
        if hours:
            return f"{hours}h {minutes}min"
        return f"{minutes}min"
    duration_display.short_description = "Duration"

    def sports_display(self, obj):
        return ", ".join([s.name for s in obj.sports.all()[:3]])
    sports_display.short_description = "Sports"

    def poster_preview(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" style="max-height: 50px;"/>',
                obj.poster.url
            )
        return "-"
    poster_preview.short_description = "Poster"


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ["documentary", "platform", "is_free", "available_until", "last_checked"]
    list_filter = ["platform", "is_free"]
    search_fields = ["documentary__title"]
    autocomplete_fields = ["documentary", "platform"]


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ["user", "documentary", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["user__email", "documentary__title"]
    autocomplete_fields = ["user", "documentary"]
