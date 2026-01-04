from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Sport(models.Model):
    """Sport/activity category (climbing, surf, ski, etc.)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Lucide icon name")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Theme(models.Model):
    """Documentary theme (wildlife, expedition, portrait, etc.)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Region(models.Model):
    """Geographic region (Alps, Patagonia, Nepal, etc.)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Person(models.Model):
    """Director, athlete, or other person related to documentaries."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    photo = models.ImageField(upload_to="people/", blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "people"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Platform(models.Model):
    """Streaming platform (Netflix, Arte, YouTube, etc.)."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="platforms/", blank=True)
    website = models.URLField(blank=True)
    is_free = models.BooleanField(default=False, help_text="Is this a free platform?")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Documentary(models.Model):
    """Core documentary model."""

    # Basic info
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True, max_length=280)

    # Dates and duration
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(600)]
    )

    # Content
    synopsis = models.TextField(blank=True)
    poster = models.ImageField(upload_to="posters/", blank=True)
    backdrop = models.ImageField(upload_to="backdrops/", blank=True)
    trailer_url = models.URLField(blank=True)

    # Relations
    directors = models.ManyToManyField(Person, related_name="directed", blank=True)
    sports = models.ManyToManyField(Sport, related_name="documentaries", blank=True)
    themes = models.ManyToManyField(Theme, related_name="documentaries", blank=True)
    regions = models.ManyToManyField(Region, related_name="documentaries", blank=True)

    # External IDs
    imdb_id = models.CharField(max_length=20, blank=True)
    imdb_rating = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    tmdb_id = models.CharField(max_length=20, blank=True)

    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "title"]
        verbose_name_plural = "documentaries"

    def __str__(self):
        return f"{self.title} ({self.year})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{self.year}"
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        """Calculate average user rating."""
        from apps.reviews.models import Review
        avg = Review.objects.filter(documentary=self).aggregate(
            avg=models.Avg("rating")
        )["avg"]
        return round(avg, 1) if avg else None

    @property
    def review_count(self):
        """Count number of reviews."""
        from apps.reviews.models import Review
        return Review.objects.filter(documentary=self).count()


class Availability(models.Model):
    """Tracks where a documentary is available to watch."""

    documentary = models.ForeignKey(
        Documentary, on_delete=models.CASCADE, related_name="availabilities"
    )
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="availabilities"
    )
    url = models.URLField()
    is_free = models.BooleanField(default=False)
    available_from = models.DateField(null=True, blank=True)
    available_until = models.DateField(null=True, blank=True)
    country_codes = models.JSONField(
        default=list,
        blank=True,
        help_text="List of country codes where available, e.g. ['FR', 'BE', 'CH']"
    )
    last_checked = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "availabilities"
        unique_together = ["documentary", "platform"]

    def __str__(self):
        return f"{self.documentary.title} on {self.platform.name}"


class Watchlist(models.Model):
    """User's watchlist - documentaries they want to watch."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist"
    )
    documentary = models.ForeignKey(
        Documentary, on_delete=models.CASCADE, related_name="in_watchlists"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "documentary"]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.email} - {self.documentary.title}"


class Watched(models.Model):
    """User's watched list - documentaries they have already seen."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watched"
    )
    documentary = models.ForeignKey(
        Documentary, on_delete=models.CASCADE, related_name="watched_by"
    )
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "documentary"]
        ordering = ["-watched_at"]

    def __str__(self):
        return f"{self.user.email} watched {self.documentary.title}"


class Favorite(models.Model):
    """User's favorite documentaries - their personal best picks."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    documentary = models.ForeignKey(
        Documentary, on_delete=models.CASCADE, related_name="favorited_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "documentary"]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.email} favorited {self.documentary.title}"
