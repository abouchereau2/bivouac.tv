"""
Auto-tag documentaries with sports, themes, and regions using Claude AI.

This command analyzes documentary synopses with Claude to generate accurate tags.
Much more effective than TMDB keywords for niche adventure documentaries.

Usage:
    python manage.py autotag_ai
    python manage.py autotag_ai --limit 10
    python manage.py autotag_ai --dry-run

Requires ANTHROPIC_API_KEY environment variable.
"""

import json
import os

import anthropic
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.documentaries.models import Documentary, Region, Sport, Theme


SYSTEM_PROMPT = """You categorize adventure documentaries. Output ONLY valid JSON, nothing else.

Sports: Climbing, Mountaineering, Skiing, Snowboarding, Surfing, Kayaking, Trail Running, Cycling, Sailing, Diving, Paragliding, Base Jumping, Expedition, Polar Exploration, Caving, Wildlife, Trekking, Swimming, Rowing, Skateboarding

Themes: Adventure, Portrait, Environment, Conservation, First Ascent, Expedition, Competition, Survival, Culture, History, Science, Mountain, Ocean, Desert, Polar, Forest

Regions: Alps, Himalayas, Andes, Rockies, Patagonia, Nepal, New Zealand, Iceland, Norway, Canada, USA, France, Switzerland, Antarctica, Arctic, Amazon, Sahara, Morocco, Tanzania, Kenya, Madagascar, Indonesia, Philippines, Japan, China, Tibet, Pacific Islands, Caribbean, Mediterranean, Scandinavia, Greenland, Alaska, Mongolia, Central Asia, Middle East, Australia, South Africa, India

Output format (JSON only, no other text):
{"sports":["..."],"themes":["..."],"regions":["..."],"reasoning":"..."}"""


class Command(BaseCommand):
    help = "Auto-tag documentaries using Claude AI analysis of synopses"

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
        parser.add_argument(
            "--unpublished-only",
            action="store_true",
            help="Only process unpublished documentaries",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        force = options["force"]
        unpublished_only = options["unpublished_only"]

        # Check for API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self.stderr.write(
                self.style.ERROR(
                    "ANTHROPIC_API_KEY environment variable not set.\n"
                    "Set it with: export ANTHROPIC_API_KEY=your_key"
                )
            )
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        # Get documentaries to tag
        queryset = Documentary.objects.exclude(synopsis="").exclude(
            synopsis__startswith="Winner of"
        )

        if unpublished_only:
            queryset = queryset.filter(is_published=False)

        if not force:
            # Only docs without any sports, themes, or regions
            queryset = queryset.filter(
                sports__isnull=True, themes__isnull=True, regions__isnull=True
            )

        queryset = queryset.distinct().order_by("-year", "title")

        if limit:
            queryset = queryset[:limit]

        docs = list(queryset)
        total = len(docs)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No documentaries need AI tagging!"))
            return

        self.stdout.write(f"Processing {total} documentaries with Claude AI...\n")

        # Load taxonomies for validation
        valid_sports = set(Sport.objects.values_list("name", flat=True))
        valid_themes = set(Theme.objects.values_list("name", flat=True))
        valid_regions = set(Region.objects.values_list("name", flat=True))

        sports_map = {s.name: s for s in Sport.objects.all()}
        themes_map = {t.name: t for t in Theme.objects.all()}
        regions_map = {r.name: r for r in Region.objects.all()}

        # Initialize Claude client
        client = anthropic.Anthropic(api_key=api_key)

        stats = {
            "tagged": 0,
            "sports_added": 0,
            "themes_added": 0,
            "regions_added": 0,
            "errors": 0,
        }

        for i, doc in enumerate(docs, 1):
            self.stdout.write(f"\n[{i}/{total}] {doc.title} ({doc.year})")

            try:
                # Build prompt for Claude
                user_prompt = f"""Documentary: {doc.title} ({doc.year})

Synopsis: {doc.synopsis}

Directors: {', '.join(d.name for d in doc.directors.all()) or 'Unknown'}

Analyze this documentary and provide appropriate tags."""

                # Call Claude API
                response = client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=500,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )

                # Parse response
                response_text = response.content[0].text

                # Extract JSON from response (handle markdown code blocks and partial JSON)
                json_str = response_text
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]

                # Try to find JSON object in the text
                json_str = json_str.strip()
                if not json_str.startswith("{"):
                    # Find first { in the text
                    start = json_str.find("{")
                    if start != -1:
                        json_str = json_str[start:]

                # Ensure JSON is complete (fix truncated responses)
                if json_str.count("{") > json_str.count("}"):
                    json_str = json_str + "}" * (json_str.count("{") - json_str.count("}"))
                if json_str.count("[") > json_str.count("]"):
                    json_str = json_str + "]" * (json_str.count("[") - json_str.count("]"))

                try:
                    tags = json.loads(json_str.strip())
                except json.JSONDecodeError:
                    self.stdout.write(
                        self.style.WARNING(f"  Failed to parse JSON: {response_text[:100]}")
                    )
                    stats["errors"] += 1
                    continue

                # Validate and collect tags
                matched_sports = []
                matched_themes = []
                matched_regions = []

                for sport_name in tags.get("sports", []):
                    if sport_name in valid_sports:
                        matched_sports.append(sports_map[sport_name])

                for theme_name in tags.get("themes", []):
                    if theme_name in valid_themes:
                        matched_themes.append(themes_map[theme_name])

                for region_name in tags.get("regions", []):
                    if region_name in valid_regions:
                        matched_regions.append(regions_map[region_name])

                # Display results
                self.stdout.write(
                    f"  Sports: {[s.name for s in matched_sports] or 'none'}"
                )
                self.stdout.write(
                    f"  Themes: {[t.name for t in matched_themes] or 'none'}"
                )
                self.stdout.write(
                    f"  Regions: {[r.name for r in matched_regions] or 'none'}"
                )
                if tags.get("reasoning"):
                    self.stdout.write(f"  Reason: {tags['reasoning'][:80]}...")

                if not dry_run:
                    with transaction.atomic():
                        if matched_sports:
                            doc.sports.add(*matched_sports)
                            stats["sports_added"] += len(matched_sports)
                        if matched_themes:
                            doc.themes.add(*matched_themes)
                            stats["themes_added"] += len(matched_themes)
                        if matched_regions:
                            doc.regions.add(*matched_regions)
                            stats["regions_added"] += len(matched_regions)

                    self.stdout.write(self.style.SUCCESS("  ✓ Tags saved"))

                stats["tagged"] += 1

            except anthropic.APIError as e:
                self.stdout.write(self.style.ERROR(f"  API Error: {e}"))
                stats["errors"] += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))
                stats["errors"] += 1

        # Summary
        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("AI tagging complete:"))
        self.stdout.write(f"  - Documentaries tagged: {stats['tagged']}")
        self.stdout.write(f"  - Sports added: {stats['sports_added']}")
        self.stdout.write(f"  - Themes added: {stats['themes_added']}")
        self.stdout.write(f"  - Regions added: {stats['regions_added']}")
        self.stdout.write(f"  - Errors: {stats['errors']}")
