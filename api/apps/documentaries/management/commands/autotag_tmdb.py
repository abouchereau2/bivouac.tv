"""
Auto-tag documentaries with sports and themes based on TMDB keywords.

This command fetches keywords from TMDB and maps them to our taxonomy.

Usage:
    python manage.py autotag_tmdb
    python manage.py autotag_tmdb --dry-run
    python manage.py autotag_tmdb --limit 10
"""

import time

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.documentaries.models import Documentary, Sport, Theme


TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Map TMDB keywords to our Sports
# Keys are lowercase TMDB keywords, values are our Sport names
KEYWORD_TO_SPORT = {
    # Climbing
    "rock climbing": "Climbing",
    "climbing": "Climbing",
    "free climbing": "Climbing",
    "bouldering": "Climbing",
    "alpinism": "Mountaineering",
    "mountaineering": "Mountaineering",
    "mountain climbing": "Mountaineering",
    "everest": "Mountaineering",
    "mount everest": "Mountaineering",
    "k2": "Mountaineering",
    "himalaya": "Mountaineering",
    # Snow sports
    "skiing": "Skiing",
    "ski": "Skiing",
    "backcountry skiing": "Skiing",
    "freeride": "Skiing",
    "snowboarding": "Snowboarding",
    "snowboard": "Snowboarding",
    # Water sports
    "surfing": "Surfing",
    "surf": "Surfing",
    "big wave surfing": "Surfing",
    "kayak": "Kayaking",
    "kayaking": "Kayaking",
    "whitewater": "Kayaking",
    "canoeing": "Kayaking",
    "sailing": "Sailing",
    "yacht": "Sailing",
    "scuba diving": "Diving",
    "diving": "Diving",
    "freediving": "Diving",
    "underwater": "Diving",
    # Air sports
    "paragliding": "Paragliding",
    "base jumping": "Base Jumping",
    "skydiving": "Base Jumping",
    "wingsuit": "Base Jumping",
    # Running & Cycling
    "trail running": "Trail Running",
    "ultramarathon": "Trail Running",
    "marathon": "Trail Running",
    "cycling": "Cycling",
    "mountain biking": "Cycling",
    "bicycle": "Cycling",
    # Other adventure
    "expedition": "Expedition",
    "exploration": "Expedition",
    "adventure": "Expedition",
    "polar expedition": "Polar Exploration",
    "arctic": "Polar Exploration",
    "antarctic": "Polar Exploration",
    "antarctica": "Polar Exploration",
    "cave": "Caving",
    "caving": "Caving",
    "spelunking": "Caving",
    "trekking": "Trekking",
    "hiking": "Trekking",
    "backpacking": "Trekking",
    "swimming": "Swimming",
    "open water": "Swimming",
    "rowing": "Rowing",
    "skateboard": "Skateboarding",
    "skateboarding": "Skateboarding",
    # Wildlife
    "wildlife": "Wildlife",
    "nature": "Wildlife",
    "animal": "Wildlife",
    "bird": "Wildlife",
    "shark": "Wildlife",
    "whale": "Wildlife",
    "bear": "Wildlife",
    "lion": "Wildlife",
    "elephant": "Wildlife",
}

# Map TMDB keywords to our Themes
KEYWORD_TO_THEME = {
    # Core themes
    "adventure": "Adventure",
    "portrait": "Portrait",
    "biography": "Portrait",
    "biographical": "Portrait",
    "environment": "Environment",
    "environmental": "Environment",
    "climate change": "Environment",
    "global warming": "Environment",
    "conservation": "Conservation",
    "endangered species": "Conservation",
    "wildlife conservation": "Conservation",
    "first ascent": "First Ascent",
    "expedition": "Expedition",
    "competition": "Competition",
    "championship": "Competition",
    "olympics": "Competition",
    "world cup": "Competition",
    "survival": "Survival",
    "rescue": "Survival",
    "disaster": "Survival",
    "culture": "Culture",
    "indigenous": "Culture",
    "tradition": "Culture",
    "history": "History",
    "historical": "History",
    "science": "Science",
    "scientific": "Science",
    "research": "Science",
    # Environment themes
    "mountain": "Mountain",
    "mountains": "Mountain",
    "alps": "Mountain",
    "himalayas": "Mountain",
    "ocean": "Ocean",
    "sea": "Ocean",
    "marine": "Ocean",
    "desert": "Desert",
    "sahara": "Desert",
    "polar": "Polar",
    "arctic": "Polar",
    "antarctic": "Polar",
    "forest": "Forest",
    "jungle": "Forest",
    "rainforest": "Forest",
    "amazon": "Forest",
}

# Map TMDB genres to themes (as fallback)
GENRE_TO_THEME = {
    "adventure": "Adventure",
    "history": "History",
    "documentary": None,  # Too generic
}


class TMDBKeywordClient:
    """TMDB client for fetching keywords."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)
        self._request_count = 0
        self._last_request_time = 0

    def _rate_limit(self):
        """Simple rate limiting - max 40 requests per 10 seconds."""
        self._request_count += 1
        if self._request_count >= 35:
            elapsed = time.time() - self._last_request_time
            if elapsed < 10:
                time.sleep(10 - elapsed)
            self._request_count = 0
            self._last_request_time = time.time()

    def get_keywords(self, tmdb_id: str) -> list[str]:
        """Get keywords for a movie."""
        self._rate_limit()

        try:
            response = self.client.get(
                f"{TMDB_BASE_URL}/movie/{tmdb_id}/keywords",
                params={"api_key": self.api_key},
            )
            response.raise_for_status()
            keywords = response.json().get("keywords", [])
            return [kw["name"].lower() for kw in keywords]
        except httpx.HTTPError:
            return []

    def get_genres(self, tmdb_id: str) -> list[str]:
        """Get genres for a movie."""
        self._rate_limit()

        try:
            response = self.client.get(
                f"{TMDB_BASE_URL}/movie/{tmdb_id}",
                params={"api_key": self.api_key},
            )
            response.raise_for_status()
            genres = response.json().get("genres", [])
            return [g["name"].lower() for g in genres]
        except httpx.HTTPError:
            return []

    def close(self):
        self.client.close()


class Command(BaseCommand):
    help = "Auto-tag documentaries with sports/themes from TMDB keywords"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be tagged without making changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of documentaries to process",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-tag documentaries that already have tags",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        force = options["force"]

        api_key = getattr(settings, "TMDB_API_KEY", None)
        if not api_key:
            self.stderr.write(
                self.style.ERROR("TMDB_API_KEY not found in settings.")
            )
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        # Get documentaries with TMDB IDs
        queryset = Documentary.objects.exclude(tmdb_id="")

        if not force:
            # Only docs without any sports or themes
            queryset = queryset.filter(sports__isnull=True, themes__isnull=True)

        queryset = queryset.distinct()

        if limit:
            queryset = queryset[:limit]

        docs = list(queryset)
        total = len(docs)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No documentaries need tagging!"))
            return

        self.stdout.write(f"Processing {total} documentaries...\n")

        # Load all sports and themes for mapping
        sports_map = {s.name: s for s in Sport.objects.all()}
        themes_map = {t.name: t for t in Theme.objects.all()}

        client = TMDBKeywordClient(api_key)
        tagged_count = 0
        skipped_count = 0

        try:
            for i, doc in enumerate(docs, 1):
                self.stdout.write(f"[{i}/{total}] {doc.title}...")

                keywords = client.get_keywords(doc.tmdb_id)
                genres = client.get_genres(doc.tmdb_id)

                matched_sports = set()
                matched_themes = set()

                # Match keywords to sports
                for kw in keywords:
                    if kw in KEYWORD_TO_SPORT:
                        sport_name = KEYWORD_TO_SPORT[kw]
                        if sport_name in sports_map:
                            matched_sports.add(sports_map[sport_name])

                # Match keywords to themes
                for kw in keywords:
                    if kw in KEYWORD_TO_THEME:
                        theme_name = KEYWORD_TO_THEME[kw]
                        if theme_name in themes_map:
                            matched_themes.add(themes_map[theme_name])

                # Fallback: match genres to themes
                for genre in genres:
                    if genre in GENRE_TO_THEME and GENRE_TO_THEME[genre]:
                        theme_name = GENRE_TO_THEME[genre]
                        if theme_name in themes_map:
                            matched_themes.add(themes_map[theme_name])

                if not matched_sports and not matched_themes:
                    self.stdout.write(self.style.WARNING(" no matches"))
                    skipped_count += 1
                    continue

                sport_names = [s.name for s in matched_sports]
                theme_names = [t.name for t in matched_themes]

                if dry_run:
                    self.stdout.write(self.style.SUCCESS(
                        f" Sports: {sport_names or 'none'}, Themes: {theme_names or 'none'}"
                    ))
                else:
                    with transaction.atomic():
                        if matched_sports:
                            doc.sports.add(*matched_sports)
                        if matched_themes:
                            doc.themes.add(*matched_themes)

                    self.stdout.write(self.style.SUCCESS(
                        f" +{len(matched_sports)} sports, +{len(matched_themes)} themes"
                    ))

                tagged_count += 1

        finally:
            client.close()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Auto-tagging complete:"))
        self.stdout.write(f"  - Tagged: {tagged_count}")
        self.stdout.write(f"  - No matches: {skipped_count}")
