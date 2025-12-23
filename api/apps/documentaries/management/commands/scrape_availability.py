"""
Scrape streaming availability for documentaries using TMDB watch providers API.

Usage:
    python manage.py scrape_availability
    python manage.py scrape_availability --limit 10
    python manage.py scrape_availability --dry-run
    python manage.py scrape_availability --country FR  # Default is FR
"""

import time

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.documentaries.models import Availability, Documentary, Platform


TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Mapping TMDB provider IDs to our platform slugs
# Get provider IDs from: https://api.themoviedb.org/3/watch/providers/movie?api_key=XXX&watch_region=FR
TMDB_PROVIDER_MAP = {
    # Subscription services
    8: "netflix",
    1796: "netflix",  # Netflix with Ads
    119: "amazon-prime-video",  # Amazon Prime Video
    10: "amazon-prime-video",   # Amazon Video (rental/purchase)
    2100: "amazon-prime-video", # Amazon Prime with Ads
    337: "disney",
    234: "arte",
    190: "curiosity-stream",
    531: "paramount",
    2303: "paramount",  # Paramount Plus Premium
    11: "mubi",
    201: "mubi",  # MUBI Amazon Channel
    350: "apple-tv",
    2: "apple-tv",
    # Free platforms
    192: "youtube",
    188: "youtube",  # YouTube Premium
    538: "plex",
    2077: "plex",  # Plex Channel
    # Note: Red Bull TV, Ushuaia TV, Outside TV, Tubi, Vimeo not in TMDB FR
}


class Command(BaseCommand):
    help = "Scrape streaming availability from TMDB watch providers"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be added without making changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of documentaries to process",
        )
        parser.add_argument(
            "--country",
            type=str,
            default="FR",
            help="Country code for watch providers (default: FR)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-check documentaries that already have availabilities",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        country = options["country"].upper()
        force = options["force"]

        api_key = getattr(settings, "TMDB_API_KEY", None)
        if not api_key:
            self.stderr.write(self.style.ERROR(
                "TMDB_API_KEY not found in settings. Add TMDB_API_KEY to your .env file."
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        # Load our platforms
        platforms = {p.slug: p for p in Platform.objects.all()}
        self.stdout.write(f"Loaded {len(platforms)} platforms\n")

        # Get documentaries with TMDB ID
        queryset = Documentary.objects.exclude(tmdb_id="")

        if not force:
            # Exclude docs that already have availabilities
            docs_with_avail = Availability.objects.values_list("documentary_id", flat=True)
            queryset = queryset.exclude(id__in=docs_with_avail)

        if limit:
            queryset = queryset[:limit]

        docs = list(queryset)
        total = len(docs)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No documentaries to check!"))
            return

        self.stdout.write(f"Checking {total} documentaries for {country} availability...\n")

        client = httpx.Client(timeout=30.0)
        request_count = 0

        found_count = 0
        not_found_count = 0
        added_count = 0

        try:
            for i, doc in enumerate(docs, 1):
                # Rate limiting (40 req / 10 sec)
                request_count += 1
                if request_count >= 35:
                    time.sleep(10)
                    request_count = 0

                self.stdout.write(f"[{i}/{total}] {doc.title}...")

                try:
                    response = client.get(
                        f"{TMDB_BASE_URL}/movie/{doc.tmdb_id}/watch/providers",
                        params={"api_key": api_key}
                    )
                    response.raise_for_status()
                    data = response.json()

                    results = data.get("results", {})
                    country_data = results.get(country, {})

                    if not country_data:
                        self.stdout.write(self.style.WARNING(f" No {country} providers"))
                        not_found_count += 1
                        continue

                    found_count += 1
                    providers_added = []

                    # Check flatrate (subscription), free, and ads categories
                    for category in ["flatrate", "free", "ads"]:
                        providers = country_data.get(category, [])
                        for provider in providers:
                            provider_id = provider.get("provider_id")
                            slug = TMDB_PROVIDER_MAP.get(provider_id)
                            if not slug:
                                continue

                            platform = platforms.get(slug)
                            if not platform:
                                continue

                            # Build watch URL (TMDB provides a link)
                            watch_link = country_data.get("link", "")

                            if dry_run:
                                providers_added.append(f"{platform.name} ({category})")
                            else:
                                # Create or update availability
                                avail, created = Availability.objects.update_or_create(
                                    documentary=doc,
                                    platform=platform,
                                    defaults={
                                        "url": watch_link,
                                        "is_free": category in ["free", "ads"],
                                        "country_codes": [country],
                                    }
                                )
                                if created:
                                    added_count += 1
                                    providers_added.append(platform.name)

                    if providers_added:
                        self.stdout.write(self.style.SUCCESS(
                            f" Found: {', '.join(providers_added)}"
                        ))
                    else:
                        self.stdout.write(self.style.WARNING(" No mapped providers"))

                except httpx.HTTPError as e:
                    self.stdout.write(self.style.ERROR(f" HTTP ERROR: {e}"))

        finally:
            client.close()

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Scraping complete:"))
        self.stdout.write(f"  - Docs with providers in {country}: {found_count}")
        self.stdout.write(f"  - Docs without providers: {not_found_count}")
        if not dry_run:
            self.stdout.write(f"  - Availabilities added: {added_count}")

        # Show unmapped providers hint
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE(
            "Tip: To see all available TMDB providers for a region, visit:\n"
            f"https://api.themoviedb.org/3/watch/providers/movie?api_key=YOUR_KEY&watch_region={country}"
        ))
