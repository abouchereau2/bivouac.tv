"""
Enrich documentaries with web-scraped data (for films not found on TMDB).

This command searches YouTube to find trailers and metadata for documentaries.
YouTube is the most reliable source for niche/indie documentaries.

Usage:
    python manage.py enrich_web
    python manage.py enrich_web --limit 10
    python manage.py enrich_web --dry-run
"""

import json
import re
import time
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.documentaries.models import Documentary


class WebScraper:
    """Web scraper for documentary metadata from YouTube."""

    def __init__(self, stdout=None):
        self.stdout = stdout
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
        )
        self._last_request = 0

    def _rate_limit(self, delay: float = 2.0):
        """Respect rate limits between requests."""
        elapsed = time.time() - self._last_request
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request = time.time()

    def log(self, message: str):
        """Log a message if stdout is available."""
        if self.stdout:
            self.stdout.write(message)

    def search_youtube(self, title: str, year: int | None = None) -> dict | None:
        """
        Search YouTube for a documentary.
        Returns dict with: video_id, title, description, thumbnail_url
        """
        self._rate_limit()

        # Build search query - add "documentaire" for French docs
        query = f"{title} documentaire"
        if year:
            query += f" {year}"

        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"

        try:
            response = self.client.get(search_url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            self.log(f"    YouTube search error: {e}")
            return None

        # Extract video IDs from YouTube's HTML (they embed JSON data)
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)

        if not video_ids:
            return None

        # Get unique video IDs (first few results)
        seen = set()
        unique_ids = []
        for vid in video_ids:
            if vid not in seen:
                seen.add(vid)
                unique_ids.append(vid)
                if len(unique_ids) >= 5:
                    break

        # Check each video to find the best match
        for video_id in unique_ids:
            video_data = self._fetch_youtube_video(video_id, title)
            if video_data:
                return video_data

        return None

    def _fetch_youtube_video(self, video_id: str, expected_title: str) -> dict | None:
        """Fetch metadata from a YouTube video page."""
        self._rate_limit(delay=1.0)

        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            response = self.client.get(url)
            response.raise_for_status()
        except httpx.HTTPError:
            return None

        soup = BeautifulSoup(response.text, "lxml")

        # Extract metadata from meta tags
        title_elem = soup.select_one('meta[name="title"]')
        title = title_elem.get("content") if title_elem else None

        if not title:
            return None

        # Check if title matches (fuzzy)
        if not self._titles_match(title, expected_title):
            return None

        result = {
            "video_id": video_id,
            "video_url": url,
            "title": title,
            "description": None,
            "thumbnail_url": None,
        }

        # Get FULL description from ytInitialPlayerResponse JSON
        # (meta description is truncated to 160 chars)
        match = re.search(r"ytInitialPlayerResponse\s*=\s*({.+?});", response.text)
        if match:
            try:
                player_data = json.loads(match.group(1))
                full_desc = player_data.get("videoDetails", {}).get("shortDescription", "")
                if full_desc:
                    result["description"] = full_desc.strip()
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback to meta description if JSON parsing failed
        if not result["description"]:
            desc_elem = soup.select_one('meta[name="description"]')
            if desc_elem:
                result["description"] = desc_elem.get("content", "").strip()

        # Get high-quality thumbnail
        # YouTube thumbnails: maxresdefault.jpg (1280x720), hqdefault.jpg (480x360)
        result["thumbnail_url"] = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

        return result

    def _titles_match(self, title1: str, title2: str) -> bool:
        """Check if two titles match (fuzzy comparison)."""
        def normalize(t: str) -> str:
            t = t.lower()
            # Remove punctuation and extra spaces
            t = re.sub(r"[^\w\s]", "", t)
            t = re.sub(r"\s+", " ", t).strip()
            return t

        n1 = normalize(title1)
        n2 = normalize(title2)

        # Exact match
        if n1 == n2:
            return True

        # One contains the other
        if n1 in n2 or n2 in n1:
            return True

        # Check word overlap (at least 50% of words match)
        words1 = set(n1.split())
        words2 = set(n2.split())
        if words1 and words2:
            overlap = len(words1 & words2)
            min_len = min(len(words1), len(words2))
            if min_len > 0 and overlap >= min_len * 0.5:
                return True

        return False

    def search_vimeo(self, title: str, year: int | None = None) -> dict | None:
        """
        Search Vimeo for a documentary.
        Returns dict with: video_url, title, description, thumbnail_url
        """
        self._rate_limit()

        query = f"{title} documentaire"
        if year:
            query += f" {year}"

        search_url = f"https://vimeo.com/search?q={quote_plus(query)}"

        try:
            response = self.client.get(search_url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            self.log(f"    Vimeo search error: {e}")
            return None

        # Extract Vimeo video IDs from search results
        video_ids = re.findall(r'"/(\d{8,12})"', response.text)

        if not video_ids:
            return None

        # Get unique video IDs
        seen = set()
        unique_ids = []
        for vid in video_ids:
            if vid not in seen:
                seen.add(vid)
                unique_ids.append(vid)
                if len(unique_ids) >= 3:
                    break

        # Check each video
        for video_id in unique_ids:
            video_data = self._fetch_vimeo_video(video_id, title)
            if video_data:
                return video_data

        return None

    def _fetch_vimeo_video(self, video_id: str, expected_title: str) -> dict | None:
        """Fetch metadata from a Vimeo video page."""
        self._rate_limit(delay=1.0)

        url = f"https://vimeo.com/{video_id}"

        try:
            response = self.client.get(url)
            response.raise_for_status()
        except httpx.HTTPError:
            return None

        soup = BeautifulSoup(response.text, "lxml")

        # Get title from og:title
        title_elem = soup.select_one('meta[property="og:title"]')
        title = title_elem.get("content") if title_elem else None

        if not title:
            return None

        # Check if title matches
        if not self._titles_match(title, expected_title):
            return None

        result = {
            "video_id": video_id,
            "video_url": url,
            "title": title,
            "description": None,
            "thumbnail_url": None,
        }

        # Get description
        desc_elem = soup.select_one('meta[property="og:description"]')
        if desc_elem:
            result["description"] = desc_elem.get("content", "").strip()

        # Get thumbnail
        thumb_elem = soup.select_one('meta[property="og:image"]')
        if thumb_elem:
            result["thumbnail_url"] = thumb_elem.get("content")

        return result

    def download_image(self, url: str) -> bytes | None:
        """Download an image from URL."""
        if not url:
            return None

        self._rate_limit(delay=0.5)

        try:
            response = self.client.get(url)

            # YouTube may return 404 for maxresdefault, try hqdefault
            if response.status_code == 404 and "ytimg.com" in url and "maxresdefault" in url:
                fallback_url = url.replace("maxresdefault", "hqdefault")
                response = self.client.get(fallback_url)

            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "image" in content_type:
                return response.content

        except httpx.HTTPError:
            pass

        return None

    def close(self):
        """Close the HTTP client."""
        self.client.close()


class Command(BaseCommand):
    help = "Enrich documentaries with web-scraped data (YouTube, Vimeo)"

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
            "--unpublished-only",
            action="store_true",
            default=True,
            help="Only process unpublished documentaries (default: True)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-enrich documentaries that already have data",
        )
        parser.add_argument(
            "--skip-youtube",
            action="store_true",
            help="Skip YouTube search",
        )
        parser.add_argument(
            "--skip-vimeo",
            action="store_true",
            help="Skip Vimeo search",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        unpublished_only = options["unpublished_only"]
        force = options["force"]
        skip_youtube = options["skip_youtube"]
        skip_vimeo = options["skip_vimeo"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        # Get documentaries to enrich
        queryset = Documentary.objects.all()

        if unpublished_only:
            queryset = queryset.filter(is_published=False)

        if not force:
            # Only docs without poster (main gap we're filling)
            queryset = queryset.filter(poster="")

        queryset = queryset.order_by("-year", "title")

        if limit:
            queryset = queryset[:limit]

        docs = list(queryset)
        total = len(docs)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No documentaries need web enrichment!"))
            return

        self.stdout.write(f"Processing {total} documentaries...\n")

        scraper = WebScraper(stdout=self.stdout)

        stats = {
            "enriched": 0,
            "poster_added": 0,
            "synopsis_added": 0,
            "trailer_added": 0,
            "not_found": 0,
            "errors": 0,
        }

        try:
            for i, doc in enumerate(docs, 1):
                self.stdout.write(f"\n[{i}/{total}] {doc.title} ({doc.year})")

                try:
                    enriched = False
                    video_data = None

                    # Step 1: Try YouTube
                    if not skip_youtube and not enriched:
                        self.stdout.write("  Searching YouTube...")
                        video_data = scraper.search_youtube(doc.title, doc.year)

                        if video_data:
                            self.stdout.write(
                                self.style.SUCCESS(f"    Found: {video_data['title'][:50]}")
                            )
                            if not dry_run:
                                enriched = self._apply_video_data(
                                    doc, video_data, scraper, stats, source="youtube"
                                )
                            else:
                                self._show_dry_run_info(video_data)
                                enriched = True
                        else:
                            self.stdout.write(self.style.WARNING("    Not found on YouTube"))

                    # Step 2: Try Vimeo as fallback
                    if not skip_vimeo and not enriched:
                        self.stdout.write("  Searching Vimeo...")
                        video_data = scraper.search_vimeo(doc.title, doc.year)

                        if video_data:
                            self.stdout.write(
                                self.style.SUCCESS(f"    Found: {video_data['title'][:50]}")
                            )
                            if not dry_run:
                                enriched = self._apply_video_data(
                                    doc, video_data, scraper, stats, source="vimeo"
                                )
                            else:
                                self._show_dry_run_info(video_data)
                                enriched = True
                        else:
                            self.stdout.write(self.style.WARNING("    Not found on Vimeo"))

                    if enriched:
                        stats["enriched"] += 1
                    else:
                        stats["not_found"] += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error: {e}"))
                    stats["errors"] += 1

        finally:
            scraper.close()

        # Summary
        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("Web enrichment complete:"))
        self.stdout.write(f"  - Enriched: {stats['enriched']}")
        self.stdout.write(f"  - Posters added: {stats['poster_added']}")
        self.stdout.write(f"  - Synopses added: {stats['synopsis_added']}")
        self.stdout.write(f"  - Trailers added: {stats['trailer_added']}")
        self.stdout.write(f"  - Not found: {stats['not_found']}")
        self.stdout.write(f"  - Errors: {stats['errors']}")

    def _show_dry_run_info(self, video_data: dict):
        """Show what would be updated in dry run mode."""
        if video_data.get("thumbnail_url"):
            self.stdout.write(f"    Would download poster from: {video_data['thumbnail_url'][:60]}...")
        if video_data.get("description"):
            self.stdout.write(f"    Would add synopsis: {video_data['description'][:60]}...")
        if video_data.get("video_url"):
            self.stdout.write(f"    Would set trailer: {video_data['video_url']}")

    def _apply_video_data(
        self, doc: Documentary, video_data: dict, scraper: WebScraper, stats: dict, source: str
    ) -> bool:
        """Apply video data to a documentary."""
        changed = False

        with transaction.atomic():
            # Download and save thumbnail as poster
            if video_data.get("thumbnail_url") and not doc.poster:
                image_data = scraper.download_image(video_data["thumbnail_url"])
                if image_data:
                    filename = f"{doc.slug}-poster.jpg"
                    doc.poster.save(filename, ContentFile(image_data), save=False)
                    stats["poster_added"] += 1
                    changed = True
                    self.stdout.write(self.style.SUCCESS(f"    ✓ Poster saved from {source}"))

            # Update synopsis if we have a better one
            if video_data.get("description"):
                desc = video_data["description"]
                # Only update if current synopsis is placeholder or shorter
                is_placeholder = doc.synopsis.startswith("Winner of")
                if is_placeholder or (len(desc) > len(doc.synopsis) and len(desc) > 50):
                    doc.synopsis = desc
                    stats["synopsis_added"] += 1
                    changed = True
                    self.stdout.write(self.style.SUCCESS("    ✓ Synopsis updated"))

            # Set trailer URL
            if video_data.get("video_url") and not doc.trailer_url:
                doc.trailer_url = video_data["video_url"]
                stats["trailer_added"] += 1
                changed = True
                self.stdout.write(self.style.SUCCESS(f"    ✓ Trailer set: {video_data['video_url']}"))

            if changed:
                doc.save()

        return changed
