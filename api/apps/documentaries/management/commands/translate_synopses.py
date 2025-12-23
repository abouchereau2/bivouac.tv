"""
Management command to translate documentary synopses using Claude API.

Usage:
    python manage.py translate_synopses
    python manage.py translate_synopses --batch-size=10
    python manage.py translate_synopses --dry-run
"""

import time
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.documentaries.models import Documentary


class Command(BaseCommand):
    help = "Translate documentary synopses from English to French (or vice versa) using Claude API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10,
            help="Number of documentaries to translate in one run (default: 10)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be translated without making changes",
        )
        parser.add_argument(
            "--direction",
            type=str,
            default="en_to_fr",
            choices=["en_to_fr", "fr_to_en"],
            help="Translation direction (default: en_to_fr)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.0,
            help="Delay between API calls in seconds (default: 1.0)",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]
        direction = options["direction"]
        delay = options["delay"]

        # Check for API key
        api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
        if not api_key:
            api_key = __import__("os").environ.get("ANTHROPIC_API_KEY")

        if not api_key and not dry_run:
            self.stderr.write(
                self.style.ERROR(
                    "ANTHROPIC_API_KEY not found. Set it in settings or environment."
                )
            )
            return

        # Get documentaries that need translation
        if direction == "en_to_fr":
            # Has English, missing French
            docs = Documentary.objects.filter(
                synopsis_en__gt="",
                synopsis_fr="",
            ).order_by("id")[:batch_size]
            source_field = "synopsis_en"
            target_field = "synopsis_fr"
            source_lang = "English"
            target_lang = "French"
        else:
            # Has French, missing English
            docs = Documentary.objects.filter(
                synopsis_fr__gt="",
                synopsis_en="",
            ).order_by("id")[:batch_size]
            source_field = "synopsis_fr"
            target_field = "synopsis_en"
            source_lang = "French"
            target_lang = "English"

        if not docs:
            self.stdout.write(
                self.style.SUCCESS(f"No documentaries need {source_lang} → {target_lang} translation!")
            )
            return

        self.stdout.write(
            f"Found {len(docs)} documentaries to translate ({source_lang} → {target_lang})"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
            for doc in docs:
                source = getattr(doc, source_field)
                self.stdout.write(f"\n📄 {doc.title} ({doc.year})")
                self.stdout.write(f"   Source: {source[:100]}...")
            return

        # Initialize Anthropic client
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            self.stderr.write(
                self.style.ERROR("anthropic package not installed. Run: pip install anthropic")
            )
            return

        translated = 0
        errors = 0

        for doc in docs:
            source_text = getattr(doc, source_field)
            if not source_text or len(source_text.strip()) < 20:
                self.stdout.write(
                    self.style.WARNING(f"⏭️  Skipping {doc.title} - synopsis too short")
                )
                continue

            self.stdout.write(f"🔄 Translating: {doc.title} ({doc.year})...")

            try:
                # Call Claude API for translation
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""Translate the following documentary synopsis from {source_lang} to {target_lang}.
Keep the same tone and style. Only output the translation, nothing else.

Synopsis:
{source_text}""",
                        }
                    ],
                )

                translated_text = message.content[0].text.strip()

                # Save translation
                setattr(doc, target_field, translated_text)
                doc.save(update_fields=[target_field])

                translated += 1
                self.stdout.write(
                    self.style.SUCCESS(f"   ✓ Translated ({len(translated_text)} chars)")
                )

                # Rate limiting
                time.sleep(delay)

            except Exception as e:
                errors += 1
                self.stderr.write(
                    self.style.ERROR(f"   ✗ Error: {str(e)}")
                )
                continue

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Translation complete: {translated} translated, {errors} errors")
        )

        # Show remaining count
        if direction == "en_to_fr":
            remaining = Documentary.objects.filter(synopsis_en__gt="", synopsis_fr="").count()
        else:
            remaining = Documentary.objects.filter(synopsis_fr__gt="", synopsis_en="").count()

        if remaining > 0:
            self.stdout.write(f"Remaining to translate: {remaining}")
