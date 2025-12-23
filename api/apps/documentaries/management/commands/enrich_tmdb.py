"""
Enrich documentaries with TMDB data (posters, synopses, metadata).

Usage:
    python manage.py enrich_tmdb
    python manage.py enrich_tmdb --limit 10
    python manage.py enrich_tmdb --dry-run
    python manage.py enrich_tmdb --force  # Re-enrich docs that already have TMDB data
"""

import time
from urllib.parse import urljoin

import httpx
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.documentaries.models import Documentary


TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/"


class TMDBClient:
    """Simple TMDB API client."""

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
                sleep_time = 10 - elapsed
                time.sleep(sleep_time)
            self._request_count = 0
            self._last_request_time = time.time()

    def search_movie(self, title: str, year: int | None = None) -> dict | None:
        """Search for a movie/documentary on TMDB."""
        self._rate_limit()

        params = {
            "api_key": self.api_key,
            "query": title,
            "include_adult": False,
        }
        if year:
            params["year"] = year
            # Also search primary_release_year for better results
            params["primary_release_year"] = year

        response = self.client.get(f"{TMDB_BASE_URL}/search/movie", params=params)
        response.raise_for_status()

        results = response.json().get("results", [])

        if not results and year:
            # Try without year constraint
            del params["year"]
            del params["primary_release_year"]
            response = self.client.get(f"{TMDB_BASE_URL}/search/movie", params=params)
            response.raise_for_status()
            results = response.json().get("results", [])

        return results[0] if results else None

    def get_movie_details(self, movie_id: int) -> dict:
        """Get full movie details including credits and watch providers."""
        self._rate_limit()

        params = {
            "api_key": self.api_key,
            "append_to_response": "credits,watch/providers,videos",
        }

        response = self.client.get(f"{TMDB_BASE_URL}/movie/{movie_id}", params=params)
        response.raise_for_status()

        return response.json()

    def download_image(self, path: str, size: str = "w500") -> bytes | None:
        """Download an image from TMDB."""
        if not path:
            return None

        url = f"{TMDB_IMAGE_BASE}{size}{path}"

        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError:
            return None

    def close(self):
        self.client.close()


class Command(BaseCommand):
    help = "Enrich documentaries with TMDB data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be enriched without making changes",
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
            help="Re-enrich documentaries that already have TMDB data",
        )
        parser.add_argument(
            "--download-images",
            action="store_true",
            help="Download and save poster/backdrop images locally",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        force = options["force"]
        download_images = options["download_images"]

        # Check for API key
        api_key = getattr(settings, "TMDB_API_KEY", None)
        if not api_key:
            self.stderr.write(self.style.ERROR(
                "TMDB_API_KEY not found in settings. "
                "Add TMDB_API_KEY to your .env file."
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        # Get documentaries to enrich
        queryset = Documentary.objects.all()

        if not force:
            # Only get docs without TMDB data
            queryset = queryset.filter(tmdb_id="")

        if limit:
            queryset = queryset[:limit]

        docs = list(queryset)
        total = len(docs)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No documentaries need enrichment!"))
            return

        self.stdout.write(f"Processing {total} documentaries...\n")

        client = TMDBClient(api_key)

        enriched_count = 0
        not_found_count = 0
        error_count = 0

        try:
            for i, doc in enumerate(docs, 1):
                self.stdout.write(f"[{i}/{total}] {doc.title} ({doc.year})...")

                try:
                    result = client.search_movie(doc.title, doc.year)

                    if not result:
                        self.stdout.write(self.style.WARNING(" NOT FOUND on TMDB"))
                        not_found_count += 1
                        continue

                    # Get full details
                    details = client.get_movie_details(result["id"])

                    if dry_run:
                        self.stdout.write(self.style.SUCCESS(
                            f" FOUND: {details.get('title')} "
                            f"(TMDB ID: {result['id']}, "
                            f"Runtime: {details.get('runtime')}min)"
                        ))
                        enriched_count += 1
                        continue

                    # Update documentary
                    with transaction.atomic():
                        doc.tmdb_id = str(result["id"])

                        # Update synopsis if we have a better one
                        if details.get("overview") and len(details["overview"]) > len(doc.synopsis):
                            doc.synopsis = details["overview"]

                        # Update runtime
                        if details.get("runtime"):
                            doc.duration_minutes = details["runtime"]

                        # Get IMDB ID
                        if details.get("imdb_id"):
                            doc.imdb_id = details["imdb_id"]

                        # Get vote average as a proxy for quality
                        if details.get("vote_average"):
                            doc.imdb_rating = details["vote_average"]

                        # Get trailer from videos
                        videos = details.get("videos", {}).get("results", [])
                        for video in videos:
                            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                                doc.trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                                break

                        # Download images if requested
                        if download_images:
                            if result.get("poster_path"):
                                image_data = client.download_image(result["poster_path"], "w500")
                                if image_data:
                                    filename = f"{doc.slug}-poster.jpg"
                                    doc.poster.save(filename, ContentFile(image_data), save=False)

                            if result.get("backdrop_path"):
                                image_data = client.download_image(result["backdrop_path"], "w1280")
                                if image_data:
                                    filename = f"{doc.slug}-backdrop.jpg"
                                    doc.backdrop.save(filename, ContentFile(image_data), save=False)

                        doc.save()
                        enriched_count += 1

                        self.stdout.write(self.style.SUCCESS(
                            f" ENRICHED (TMDB: {result['id']})"
                        ))

                except httpx.HTTPError as e:
                    self.stdout.write(self.style.ERROR(f" HTTP ERROR: {e}"))
                    error_count += 1

        finally:
            client.close()

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Enrichment complete:"))
        self.stdout.write(f"  - Enriched: {enriched_count}")
        self.stdout.write(f"  - Not found: {not_found_count}")
        self.stdout.write(f"  - Errors: {error_count}")

        if not_found_count > 0:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(
                f"Tip: {not_found_count} documentaries weren't found on TMDB. "
                "These are likely niche festival films. You may need to add "
                "metadata manually via the admin interface."
            ))
