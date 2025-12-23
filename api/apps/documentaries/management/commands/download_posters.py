"""
Download posters and backdrops for documentaries that have TMDB IDs.

Usage:
    python manage.py download_posters
    python manage.py download_posters --limit 10
"""

import httpx
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.documentaries.models import Documentary


TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/"


class Command(BaseCommand):
    help = "Download posters for documentaries with TMDB IDs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of documentaries to process",
        )

    def handle(self, *args, **options):
        limit = options["limit"]

        api_key = getattr(settings, "TMDB_API_KEY", None)
        if not api_key:
            self.stderr.write(self.style.ERROR("TMDB_API_KEY not found in settings."))
            return

        # Get docs with TMDB ID but no poster
        queryset = Documentary.objects.exclude(tmdb_id="").filter(poster="")

        if limit:
            queryset = queryset[:limit]

        docs = list(queryset)
        total = len(docs)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("All documentaries already have posters!"))
            return

        self.stdout.write(f"Downloading posters for {total} documentaries...\n")

        client = httpx.Client(timeout=30.0)
        downloaded = 0
        errors = 0

        try:
            for i, doc in enumerate(docs, 1):
                self.stdout.write(f"[{i}/{total}] {doc.title}...")

                try:
                    # Get movie details from TMDB
                    response = client.get(
                        f"{TMDB_BASE_URL}/movie/{doc.tmdb_id}",
                        params={"api_key": api_key}
                    )
                    response.raise_for_status()
                    data = response.json()

                    poster_path = data.get("poster_path")
                    backdrop_path = data.get("backdrop_path")

                    if poster_path:
                        img_response = client.get(f"{TMDB_IMAGE_BASE}w500{poster_path}")
                        img_response.raise_for_status()
                        filename = f"{doc.slug}-poster.jpg"
                        doc.poster.save(filename, ContentFile(img_response.content), save=False)

                    if backdrop_path:
                        img_response = client.get(f"{TMDB_IMAGE_BASE}w1280{backdrop_path}")
                        img_response.raise_for_status()
                        filename = f"{doc.slug}-backdrop.jpg"
                        doc.backdrop.save(filename, ContentFile(img_response.content), save=False)

                    doc.save()
                    downloaded += 1
                    self.stdout.write(self.style.SUCCESS(" OK"))

                except httpx.HTTPError as e:
                    self.stdout.write(self.style.ERROR(f" ERROR: {e}"))
                    errors += 1

        finally:
            client.close()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Downloaded: {downloaded}"))
        if errors:
            self.stdout.write(self.style.ERROR(f"Errors: {errors}"))
