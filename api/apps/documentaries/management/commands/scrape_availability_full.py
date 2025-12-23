"""
Scrape streaming availability using multiple sources:
- TMDB watch providers API
- JustWatch (unofficial API)
- YouTube search (for free documentaries)

Usage:
    python manage.py scrape_availability_full
    python manage.py scrape_availability_full --dry-run
    python manage.py scrape_availability_full --source justwatch
    python manage.py scrape_availability_full --source youtube
"""

import re
import time
from difflib import SequenceMatcher

import httpx
from django.core.management.base import BaseCommand

from apps.documentaries.models import Availability, Documentary, Platform


# JustWatch package ID to our platform slug mapping
JUSTWATCH_PLATFORM_MAP = {
    "nfx": "netflix",
    "netflix": "netflix",
    "amp": "amazon-prime-video",
    "prv": "amazon-prime-video",
    "amazon": "amazon-prime-video",
    "dnp": "disney",
    "disney": "disney",
    "atp": "apple-tv",
    "apple": "apple-tv",
    "itu": "apple-tv",
    "arte": "arte",
    "mbi": "mubi",
    "mubi": "mubi",
    "pmp": "paramount",
    "paramount": "paramount",
    "cts": "curiosity-stream",
    "curiosity": "curiosity-stream",
    "yot": "youtube",
    "youtube": "youtube",
    "vim": "vimeo",
    "vimeo": "vimeo",
    "plex": "plex",
    "redbulltv": "red-bull-tv",
}

# Monetization types that indicate free content
FREE_MONETIZATION_TYPES = {"FREE", "ADS", "FLATRATE"}  # FLATRATE = subscription


def similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class Command(BaseCommand):
    help = "Scrape streaming availability from multiple sources"

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
            "--source",
            type=str,
            choices=["all", "justwatch", "youtube", "vimeo"],
            default="all",
            help="Which source to use (default: all)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-check documentaries that already have availabilities",
        )
        parser.add_argument(
            "--min-similarity",
            type=float,
            default=0.7,
            help="Minimum title similarity to accept a match (0-1, default: 0.7)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        source = options["source"]
        force = options["force"]
        min_similarity = options["min_similarity"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        # Load platforms
        platforms = {p.slug: p for p in Platform.objects.all()}
        self.stdout.write(f"Loaded {len(platforms)} platforms\n")

        # Get documentaries
        queryset = Documentary.objects.all()

        if not force:
            docs_with_avail = Availability.objects.values_list("documentary_id", flat=True)
            queryset = queryset.exclude(id__in=docs_with_avail)

        if limit:
            queryset = queryset[:limit]

        docs = list(queryset)
        total = len(docs)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No documentaries to check!"))
            return

        self.stdout.write(f"Processing {total} documentaries...\n")

        stats = {"found": 0, "added": 0, "skipped": 0}

        for i, doc in enumerate(docs, 1):
            self.stdout.write(f"\n[{i}/{total}] {doc.title} ({doc.year})")

            offers_found = []

            # JustWatch
            if source in ["all", "justwatch"]:
                jw_offers = self._search_justwatch(doc, min_similarity)
                offers_found.extend(jw_offers)

            # YouTube direct search
            if source in ["all", "youtube"]:
                yt_offers = self._search_youtube(doc, min_similarity)
                offers_found.extend(yt_offers)

            # Vimeo search
            if source in ["all", "vimeo"]:
                vimeo_offers = self._search_vimeo(doc, min_similarity)
                offers_found.extend(vimeo_offers)

            if not offers_found:
                self.stdout.write(self.style.WARNING("  No offers found"))
                continue

            stats["found"] += 1

            # Deduplicate by platform
            seen_platforms = set()
            for offer in offers_found:
                platform_slug = offer["platform"]
                if platform_slug in seen_platforms:
                    continue
                seen_platforms.add(platform_slug)

                platform = platforms.get(platform_slug)
                if not platform:
                    continue

                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ {platform.name}: {offer['url'][:60]}... ({offer['type']})"
                ))

                if not dry_run:
                    Availability.objects.update_or_create(
                        documentary=doc,
                        platform=platform,
                        defaults={
                            "url": offer["url"],
                            "is_free": offer["is_free"],
                            "country_codes": ["FR"],
                        }
                    )
                    stats["added"] += 1

            # Rate limiting
            time.sleep(0.5)

        # Summary
        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS("Scraping complete:"))
        self.stdout.write(f"  - Docs with offers: {stats['found']}")
        if not dry_run:
            self.stdout.write(f"  - Availabilities added: {stats['added']}")

    def _search_justwatch(self, doc: Documentary, min_similarity: float) -> list[dict]:
        """Search JustWatch for streaming availability."""
        try:
            from simplejustwatchapi.justwatch import details, search
        except ImportError:
            self.stdout.write(self.style.WARNING(
                "  JustWatch API not installed. Run: uv add simple-justwatch-python-api"
            ))
            return []

        offers = []

        try:
            # Search with title and year
            search_query = f"{doc.title}"
            results = search(search_query, "FR", "fr", count=5)

            if not results:
                return []

            # Find best match by title similarity and year
            best_match = None
            best_score = 0

            for result in results:
                title_sim = similarity(doc.title, result.title)
                year_match = 1.0 if result.release_year == doc.year else 0.8

                score = title_sim * year_match

                if score > best_score and title_sim >= min_similarity:
                    best_score = score
                    best_match = result

            if not best_match:
                return []

            # Get full details
            detail = details(best_match.entry_id, "FR", "fr")

            for offer in detail.offers:
                # Map JustWatch package to our platform
                tech_name = offer.package.technical_name.lower()
                platform_slug = None

                for jw_key, slug in JUSTWATCH_PLATFORM_MAP.items():
                    if jw_key in tech_name:
                        platform_slug = slug
                        break

                if not platform_slug:
                    continue

                is_free = offer.monetization_type in FREE_MONETIZATION_TYPES

                offers.append({
                    "platform": platform_slug,
                    "url": offer.url,
                    "is_free": is_free,
                    "type": offer.monetization_type,
                    "source": "justwatch",
                })

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  JustWatch error: {e}"))

        return offers

    def _search_youtube(self, doc: Documentary, min_similarity: float = 0.6) -> list[dict]:
        """Search YouTube for free full documentaries."""
        offers = []

        try:
            # Search with documentary-specific terms
            queries = [
                f'"{doc.title}" documentaire complet',
                f'"{doc.title}" {doc.year} film complet',
                f'"{doc.title}" documentary',
            ]

            client = httpx.Client(
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "fr-FR,fr;q=0.9",
                },
            )

            for query in queries:
                encoded_query = query.replace(" ", "+").replace('"', "%22")

                response = client.get(
                    f"https://www.youtube.com/results?search_query={encoded_query}"
                )

                if response.status_code != 200:
                    continue

                # Extract video IDs and titles from JSON data in page
                # YouTube embeds initial data as JSON (use DOTALL for multiline)
                json_match = re.search(
                    r'var ytInitialData = ({.*?});</script>',
                    response.text,
                    re.DOTALL
                )
                if json_match:
                    import json
                    try:
                        data = json.loads(json_match.group(1))
                        videos = self._extract_youtube_videos(data)

                        for video in videos[:3]:  # Check top 3 results
                            title_sim = similarity(doc.title, video["title"])

                            # Check if it looks like a full documentary (> 20 min usually)
                            duration_ok = self._is_full_length(video.get("duration", ""))

                            if title_sim >= min_similarity and duration_ok:
                                offers.append({
                                    "platform": "youtube",
                                    "url": f"https://www.youtube.com/watch?v={video['id']}",
                                    "is_free": True,
                                    "type": "FREE",
                                    "source": "youtube_search",
                                    "title_found": video["title"],
                                })
                                client.close()
                                return offers
                    except json.JSONDecodeError:
                        pass

                # No fallback - only accept verified matches with title check
                if offers:
                    break

            client.close()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  YouTube error: {e}"))

        return offers

    def _extract_youtube_videos(self, data: dict) -> list[dict]:
        """Extract video info from YouTube initial data JSON."""
        videos = []
        try:
            contents = (
                data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
            )

            for section in contents:
                items = section.get("itemSectionRenderer", {}).get("contents", [])
                for item in items:
                    video = item.get("videoRenderer", {})
                    if video:
                        video_id = video.get("videoId")
                        title = video.get("title", {}).get("runs", [{}])[0].get("text", "")
                        duration = video.get("lengthText", {}).get("simpleText", "")

                        if video_id and title:
                            videos.append({
                                "id": video_id,
                                "title": title,
                                "duration": duration,
                            })
        except (KeyError, IndexError):
            pass
        return videos

    def _is_full_length(self, duration_str: str) -> bool:
        """Check if duration suggests a full documentary (> 20 minutes)."""
        if not duration_str:
            return True  # Assume ok if unknown

        # Parse "1:23:45" or "45:23" format
        parts = duration_str.split(":")
        try:
            if len(parts) >= 2:
                if len(parts) == 3:  # Hours:min:sec
                    return True  # Anything over an hour is good
                else:  # Min:sec
                    minutes = int(parts[0])
                    return minutes >= 20
        except ValueError:
            pass
        return True

    def _search_vimeo(self, doc: Documentary, min_similarity: float = 0.6) -> list[dict]:
        """Search Vimeo for documentaries."""
        offers = []

        try:
            query = f"{doc.title} {doc.year}"
            encoded_query = query.replace(" ", "+")

            response = httpx.get(
                f"https://vimeo.com/search?q={encoded_query}",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "fr-FR,fr;q=0.9",
                },
                timeout=10,
                follow_redirects=True,
            )

            if response.status_code != 200:
                return []

            # Extract video links from search results
            video_matches = re.findall(
                r'href="/(\d{6,12})"[^>]*>([^<]+)</a>',
                response.text
            )

            for video_id, title in video_matches[:5]:
                title_clean = title.strip()
                title_sim = similarity(doc.title, title_clean)

                if title_sim >= min_similarity:
                    offers.append({
                        "platform": "vimeo",
                        "url": f"https://vimeo.com/{video_id}",
                        "is_free": True,  # Most Vimeo content is free to watch
                        "type": "FREE",
                        "source": "vimeo_search",
                        "title_found": title_clean,
                    })
                    break

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Vimeo error: {e}"))

        return offers
