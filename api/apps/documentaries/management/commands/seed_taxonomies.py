"""
Seed initial taxonomy data (sports, themes, regions, platforms).

Usage:
    python manage.py seed_taxonomies
    python manage.py seed_taxonomies --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.documentaries.models import Platform, Region, Sport, Theme


# Sports/Activities with Lucide icon names
SPORTS = [
    {"name": "Climbing", "icon": "mountain"},
    {"name": "Mountaineering", "icon": "mountain-snow"},
    {"name": "Skiing", "icon": "snowflake"},
    {"name": "Snowboarding", "icon": "snowflake"},
    {"name": "Surfing", "icon": "waves"},
    {"name": "Kayaking", "icon": "ship"},
    {"name": "Trail Running", "icon": "footprints"},
    {"name": "Cycling", "icon": "bike"},
    {"name": "Sailing", "icon": "sailboat"},
    {"name": "Diving", "icon": "fish"},
    {"name": "Paragliding", "icon": "wind"},
    {"name": "Base Jumping", "icon": "plane"},
    {"name": "Expedition", "icon": "compass"},
    {"name": "Polar Exploration", "icon": "thermometer-snowflake"},
    {"name": "Caving", "icon": "lamp"},
    {"name": "Wildlife", "icon": "bird"},
    {"name": "Trekking", "icon": "footprints"},
    {"name": "Swimming", "icon": "waves"},
    {"name": "Rowing", "icon": "anchor"},
    {"name": "Skateboarding", "icon": "circle-dot"},
]

# Documentary themes
THEMES = [
    {"name": "Adventure"},
    {"name": "Portrait"},
    {"name": "Environment"},
    {"name": "Conservation"},
    {"name": "First Ascent"},
    {"name": "Expedition"},
    {"name": "Competition"},
    {"name": "Survival"},
    {"name": "Culture"},
    {"name": "History"},
    {"name": "Science"},
    {"name": "Festival Winner"},
    {"name": "Audience Favorite"},
    {"name": "Mountain"},
    {"name": "Ocean"},
    {"name": "Desert"},
    {"name": "Polar"},
    {"name": "Forest"},
]

# Geographic regions
REGIONS = [
    # Mountain ranges
    {"name": "Alps"},
    {"name": "Himalayas"},
    {"name": "Andes"},
    {"name": "Rockies"},
    {"name": "Karakoram"},
    {"name": "Dolomites"},
    {"name": "Pyrenees"},
    {"name": "Patagonia"},
    {"name": "Alaska Range"},
    # Countries/Areas known for adventure
    {"name": "Nepal"},
    {"name": "New Zealand"},
    {"name": "Iceland"},
    {"name": "Norway"},
    {"name": "Canada"},
    {"name": "USA"},
    {"name": "France"},
    {"name": "Switzerland"},
    {"name": "Italy"},
    {"name": "Spain"},
    {"name": "Morocco"},
    {"name": "South Africa"},
    {"name": "Australia"},
    {"name": "Japan"},
    {"name": "Mongolia"},
    {"name": "Greenland"},
    {"name": "Antarctica"},
    {"name": "Arctic"},
    # Water/Ocean regions
    {"name": "Pacific Ocean"},
    {"name": "Atlantic Ocean"},
    {"name": "Mediterranean"},
    {"name": "Caribbean"},
    {"name": "Indonesia"},
    {"name": "Hawaii"},
    {"name": "Tahiti"},
    {"name": "Maldives"},
    # Special areas
    {"name": "Amazon"},
    {"name": "Sahara"},
    {"name": "Yosemite"},
    {"name": "Torres del Paine"},
]

# Streaming platforms
PLATFORMS = [
    {"name": "Netflix", "website": "https://netflix.com", "is_free": False},
    {"name": "Amazon Prime Video", "website": "https://primevideo.com", "is_free": False},
    {"name": "Disney+", "website": "https://disneyplus.com", "is_free": False},
    {"name": "Arte", "website": "https://arte.tv", "is_free": True},
    {"name": "YouTube", "website": "https://youtube.com", "is_free": True},
    {"name": "Vimeo", "website": "https://vimeo.com", "is_free": False},
    {"name": "Red Bull TV", "website": "https://redbull.com/tv", "is_free": True},
    {"name": "Curiosity Stream", "website": "https://curiositystream.com", "is_free": False},
    {"name": "Apple TV+", "website": "https://tv.apple.com", "is_free": False},
    {"name": "Ushuaïa TV", "website": "https://ushuaiatv.fr", "is_free": False},
    {"name": "Outside TV", "website": "https://watch.outsideonline.com", "is_free": False},
    {"name": "Paramount+", "website": "https://paramountplus.com", "is_free": False},
    {"name": "Mubi", "website": "https://mubi.com", "is_free": False},
    {"name": "Tubi", "website": "https://tubitv.com", "is_free": True},
    {"name": "Plex", "website": "https://plex.tv", "is_free": True},
]


class Command(BaseCommand):
    help = "Seed initial taxonomy data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        stats = {
            "sports": {"created": 0, "skipped": 0},
            "themes": {"created": 0, "skipped": 0},
            "regions": {"created": 0, "skipped": 0},
            "platforms": {"created": 0, "skipped": 0},
        }

        with transaction.atomic():
            # Sports
            self.stdout.write("Seeding sports...")
            for data in SPORTS:
                exists = Sport.objects.filter(name=data["name"]).exists()
                if exists:
                    stats["sports"]["skipped"] += 1
                    continue

                if not dry_run:
                    Sport.objects.create(
                        name=data["name"],
                        icon=data.get("icon", ""),
                    )
                stats["sports"]["created"] += 1

            # Themes
            self.stdout.write("Seeding themes...")
            for data in THEMES:
                exists = Theme.objects.filter(name=data["name"]).exists()
                if exists:
                    stats["themes"]["skipped"] += 1
                    continue

                if not dry_run:
                    Theme.objects.create(name=data["name"])
                stats["themes"]["created"] += 1

            # Regions
            self.stdout.write("Seeding regions...")
            for data in REGIONS:
                exists = Region.objects.filter(name=data["name"]).exists()
                if exists:
                    stats["regions"]["skipped"] += 1
                    continue

                if not dry_run:
                    Region.objects.create(name=data["name"])
                stats["regions"]["created"] += 1

            # Platforms
            self.stdout.write("Seeding platforms...")
            for data in PLATFORMS:
                exists = Platform.objects.filter(name=data["name"]).exists()
                if exists:
                    stats["platforms"]["skipped"] += 1
                    continue

                if not dry_run:
                    Platform.objects.create(
                        name=data["name"],
                        website=data.get("website", ""),
                        is_free=data.get("is_free", False),
                    )
                stats["platforms"]["created"] += 1

            if dry_run:
                transaction.set_rollback(True)

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seeding complete:"))

        for category, counts in stats.items():
            self.stdout.write(
                f"  {category.capitalize()}: "
                f"{counts['created']} created, "
                f"{counts['skipped']} skipped"
            )
