"""
Migration to add bilingual names (name_en/name_fr) to Sport, Theme, and Region models.
Copies existing name field to name_en and creates French translations.
"""

from django.db import migrations, models


# French translations for common sports
SPORT_TRANSLATIONS = {
    "climbing": "Escalade",
    "skiing": "Ski",
    "snowboarding": "Snowboard",
    "surfing": "Surf",
    "mountaineering": "Alpinisme",
    "hiking": "Randonnée",
    "trail running": "Trail",
    "kayaking": "Kayak",
    "mountain biking": "VTT",
    "paragliding": "Parapente",
    "base jumping": "Base Jump",
    "freediving": "Apnée",
    "scuba diving": "Plongée",
    "skateboarding": "Skateboard",
    "bmx": "BMX",
    "sailing": "Voile",
    "kitesurfing": "Kitesurf",
    "windsurfing": "Planche à voile",
    "ice climbing": "Cascade de glace",
    "canyoning": "Canyoning",
    "running": "Course à pied",
    "cycling": "Cyclisme",
    "adventure": "Aventure",
    "expedition": "Expédition",
}

# French translations for common themes
THEME_TRANSLATIONS = {
    "expedition": "Expédition",
    "portrait": "Portrait",
    "competition": "Compétition",
    "environment": "Environnement",
    "wildlife": "Faune sauvage",
    "nature": "Nature",
    "adventure": "Aventure",
    "extreme": "Extrême",
    "survival": "Survie",
    "first ascent": "Première ascension",
    "record": "Record",
    "history": "Histoire",
    "culture": "Culture",
    "travel": "Voyage",
    "exploration": "Exploration",
    "conservation": "Conservation",
}

# French translations for common regions
REGION_TRANSLATIONS = {
    "alps": "Alpes",
    "french alps": "Alpes françaises",
    "swiss alps": "Alpes suisses",
    "italian alps": "Alpes italiennes",
    "himalayas": "Himalaya",
    "nepal": "Népal",
    "patagonia": "Patagonie",
    "yosemite": "Yosemite",
    "antarctica": "Antarctique",
    "arctic": "Arctique",
    "greenland": "Groenland",
    "iceland": "Islande",
    "norway": "Norvège",
    "california": "Californie",
    "hawaii": "Hawaï",
    "pacific ocean": "Océan Pacifique",
    "atlantic ocean": "Océan Atlantique",
    "amazon": "Amazonie",
    "africa": "Afrique",
    "morocco": "Maroc",
    "new zealand": "Nouvelle-Zélande",
    "australia": "Australie",
    "japan": "Japon",
    "china": "Chine",
    "india": "Inde",
    "pakistan": "Pakistan",
    "karakorum": "Karakorum",
    "rockies": "Rocheuses",
    "andes": "Andes",
    "pyrenees": "Pyrénées",
    "dolomites": "Dolomites",
    "chamonix": "Chamonix",
    "mont blanc": "Mont Blanc",
    "everest": "Everest",
    "k2": "K2",
    "indonesia": "Indonésie",
    "tahiti": "Tahiti",
    "french polynesia": "Polynésie française",
    "canada": "Canada",
    "alaska": "Alaska",
    "united states": "États-Unis",
    "france": "France",
    "switzerland": "Suisse",
    "austria": "Autriche",
    "spain": "Espagne",
    "portugal": "Portugal",
}


def copy_names_forward(apps, schema_editor):
    """Copy existing name to name_en and set name_fr with translations."""
    Sport = apps.get_model("documentaries", "Sport")
    Theme = apps.get_model("documentaries", "Theme")
    Region = apps.get_model("documentaries", "Region")

    for sport in Sport.objects.all():
        sport.name_en = sport.name
        sport.name_fr = SPORT_TRANSLATIONS.get(sport.name.lower(), sport.name)
        sport.save()

    for theme in Theme.objects.all():
        theme.name_en = theme.name
        theme.name_fr = THEME_TRANSLATIONS.get(theme.name.lower(), theme.name)
        theme.save()

    for region in Region.objects.all():
        region.name_en = region.name
        region.name_fr = REGION_TRANSLATIONS.get(region.name.lower(), region.name)
        region.save()


def copy_names_backward(apps, schema_editor):
    """Copy name_en back to name for reverse migration."""
    Sport = apps.get_model("documentaries", "Sport")
    Theme = apps.get_model("documentaries", "Theme")
    Region = apps.get_model("documentaries", "Region")

    for sport in Sport.objects.all():
        sport.name = sport.name_en
        sport.save()

    for theme in Theme.objects.all():
        theme.name = theme.name_en
        theme.save()

    for region in Region.objects.all():
        region.name = region.name_en
        region.save()


class Migration(migrations.Migration):

    dependencies = [
        ("documentaries", "0003_add_synopsis_i18n"),
    ]

    operations = [
        # Step 1: Add name_en and name_fr fields with defaults
        migrations.AddField(
            model_name="sport",
            name="name_en",
            field=models.CharField(default="", max_length=100, verbose_name="Name (English)"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="sport",
            name="name_fr",
            field=models.CharField(default="", max_length=100, verbose_name="Name (French)"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="theme",
            name="name_en",
            field=models.CharField(default="", max_length=100, verbose_name="Name (English)"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="theme",
            name="name_fr",
            field=models.CharField(default="", max_length=100, verbose_name="Name (French)"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="region",
            name="name_en",
            field=models.CharField(default="", max_length=100, verbose_name="Name (English)"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="region",
            name="name_fr",
            field=models.CharField(default="", max_length=100, verbose_name="Name (French)"),
            preserve_default=False,
        ),
        # Step 2: Run data migration to copy names
        migrations.RunPython(copy_names_forward, copy_names_backward),
        # Step 3: Remove old name fields
        migrations.RemoveField(
            model_name="sport",
            name="name",
        ),
        migrations.RemoveField(
            model_name="theme",
            name="name",
        ),
        migrations.RemoveField(
            model_name="region",
            name="name",
        ),
        # Step 4: Update ordering
        migrations.AlterModelOptions(
            name="region",
            options={"ordering": ["name_en"]},
        ),
        migrations.AlterModelOptions(
            name="sport",
            options={"ordering": ["name_en"]},
        ),
        migrations.AlterModelOptions(
            name="theme",
            options={"ordering": ["name_en"]},
        ),
    ]
