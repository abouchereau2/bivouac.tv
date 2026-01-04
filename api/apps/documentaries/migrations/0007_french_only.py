"""
Migration to convert from bilingual (EN/FR) to French-only.
- Sport, Theme, Region: merge name_en/name_fr -> name (FR preferred, EN fallback)
- Documentary: merge synopsis_en/synopsis_fr -> synopsis (FR preferred, EN fallback)
"""

from django.db import migrations, models


def merge_to_french(apps, schema_editor):
    """Copy name_fr (or name_en as fallback) to name for all taxonomy models."""
    Sport = apps.get_model("documentaries", "Sport")
    Theme = apps.get_model("documentaries", "Theme")
    Region = apps.get_model("documentaries", "Region")
    Documentary = apps.get_model("documentaries", "Documentary")

    for sport in Sport.objects.all():
        sport.name = sport.name_fr or sport.name_en or ""
        sport.save()

    for theme in Theme.objects.all():
        theme.name = theme.name_fr or theme.name_en or ""
        theme.save()

    for region in Region.objects.all():
        region.name = region.name_fr or region.name_en or ""
        region.save()

    for doc in Documentary.objects.all():
        doc.synopsis = doc.synopsis_fr or doc.synopsis_en or ""
        doc.save()


def split_to_bilingual(apps, schema_editor):
    """Reverse: copy name back to name_en and name_fr."""
    Sport = apps.get_model("documentaries", "Sport")
    Theme = apps.get_model("documentaries", "Theme")
    Region = apps.get_model("documentaries", "Region")
    Documentary = apps.get_model("documentaries", "Documentary")

    for sport in Sport.objects.all():
        sport.name_en = sport.name
        sport.name_fr = sport.name
        sport.save()

    for theme in Theme.objects.all():
        theme.name_en = theme.name
        theme.name_fr = theme.name
        theme.save()

    for region in Region.objects.all():
        region.name_en = region.name
        region.name_fr = region.name
        region.save()

    for doc in Documentary.objects.all():
        doc.synopsis_en = doc.synopsis
        doc.synopsis_fr = doc.synopsis
        doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ("documentaries", "0006_add_favorite_model"),
    ]

    operations = [
        # Step 1: Add new unified fields
        migrations.AddField(
            model_name="sport",
            name="name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="theme",
            name="name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="region",
            name="name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="documentary",
            name="synopsis",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        # Step 2: Run data migration to merge FR content (with EN fallback)
        migrations.RunPython(merge_to_french, split_to_bilingual),
        # Step 3: Remove old bilingual fields
        migrations.RemoveField(
            model_name="sport",
            name="name_en",
        ),
        migrations.RemoveField(
            model_name="sport",
            name="name_fr",
        ),
        migrations.RemoveField(
            model_name="theme",
            name="name_en",
        ),
        migrations.RemoveField(
            model_name="theme",
            name="name_fr",
        ),
        migrations.RemoveField(
            model_name="region",
            name="name_en",
        ),
        migrations.RemoveField(
            model_name="region",
            name="name_fr",
        ),
        migrations.RemoveField(
            model_name="documentary",
            name="synopsis_en",
        ),
        migrations.RemoveField(
            model_name="documentary",
            name="synopsis_fr",
        ),
        # Step 4: Update ordering to use unified name
        migrations.AlterModelOptions(
            name="sport",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="theme",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="region",
            options={"ordering": ["name"]},
        ),
    ]
