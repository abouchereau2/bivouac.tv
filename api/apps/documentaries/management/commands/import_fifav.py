"""
Import FIFAV festival data into the database.

Usage:
    python manage.py import_fifav
    python manage.py import_fifav --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.documentaries.models import Documentary, Person, Theme


# FIFAV Palmares Data (2004-2025)
FIFAV_DOCUMENTARIES = [
    # 2025 - 22ème Édition
    {"title": "Save our souls", "director": "Jean-Baptiste Bonnet", "year": 2025, "award": "Grand Prix du Festival"},
    {"title": "Guts, a female expedition through Africa", "director": "Patrizia Bruno", "year": 2025, "award": "Prix de l'Aventure"},
    {"title": "Mercantour sous nos pieds", "director": "Loïc Preghenella", "year": 2025, "award": "Prix Coup de Cœur"},
    {"title": "La route", "director": "Marianne Chaud", "year": 2025, "award": "Prix Environnement"},
    {"title": "Champions of the Golden Valley", "director": "Ben Sturgulewski", "year": 2025, "award": "Prix Montagne"},
    {"title": "Side to side", "director": "Jérôme Dalle Mulle", "year": 2025, "award": "Grand Prix du Public"},
    {"title": "Le sabot montagnard", "director": "Ashley Parsons & Quentin Boehm", "year": 2025, "award": "Prix de l'Aventurière"},
    {"title": "2000 jours au Paradis", "director": "Véronique, Anne & Erik Lapid", "year": 2025, "award": "Prix Ushuaïa TV"},
    {"title": "Le chant des forêts", "director": "Vincent Munier", "year": 2025, "award": "Prix Meilleure BO"},
    # 2024 - 21ème Édition
    {"title": "Un pasteur", "director": "Louis Hanquet", "year": 2024, "award": "Grand Prix du Festival"},
    {"title": "Les jours sauvages", "director": "Yohan Guignard", "year": 2024, "award": "Prix de l'Aventure"},
    {"title": "À perte de vue", "director": "Carla & Pierre Petit", "year": 2024, "award": "Prix Coup de Cœur"},
    {"title": "Nagalaqa, au nord des terres", "director": "Sébastien Roubinet & Franck Lepagnol", "year": 2024, "award": "Prix Environnement"},
    {"title": "Le cavalier sans tête", "director": "Andy Collet", "year": 2024, "award": "Prix Montagne"},
    {"title": "Beyond Prognosis", "director": "Alexandre Silva & Morgan Le Faucheur", "year": 2024, "award": "Grand Prix du Public"},
    {"title": "We the surfers", "director": "Arthur Bourbon", "year": 2024, "award": "Prix Ushuaïa TV"},
    {"title": "Sunny Boy", "director": "Morgan Le Faucheur", "year": 2024, "award": "Prix Collégiens"},
    # 2023 - 20ème Édition
    {"title": "Mongolie, la vallée des ours", "director": "Hamid Sardar", "year": 2023, "award": "Grand Prix du Festival"},
    {"title": "On a marché sous la terre", "director": "Alexandre Lopez", "year": 2023, "award": "Prix de l'Aventure"},
    {"title": "Still Alive", "director": "Santino Martirano", "year": 2023, "award": "Prix Coup de Cœur"},
    {"title": "L'affût aux loups", "director": "Tanguy Dumortier & Olivier Larrey", "year": 2023, "award": "Prix Environnement"},
    {"title": "Edge of reason", "director": "Jérémie Chenal & Benjamin Védrines", "year": 2023, "award": "Prix Montagne"},
    {"title": "Baluchon, 4 mètres autour du monde", "director": "Romain Latournerie & Mathieu Alonso", "year": 2023, "award": "Grand Prix du Public"},
    {"title": "Isaline, poussière d'étoiles", "director": "Alexandre Lachavanne", "year": 2023, "award": "Prix Ushuaïa TV"},
    {"title": "Première", "director": "Mathieu Koiko", "year": 2023, "award": "Prix Collégiens"},
    # 2022 - 19ème Édition
    {"title": "L'aventure", "director": "Marianne Chaud", "year": 2022, "award": "Grand Prix du Festival"},
    {"title": "Wild Waters", "director": "David Arnaud", "year": 2022, "award": "Prix de l'Aventure"},
    {"title": "Havana Libre", "director": "Corey McLean", "year": 2022, "award": "Prix Coup de Cœur"},
    {"title": "Naïs au pays des loups", "director": "Rémy Masséglia", "year": 2022, "award": "Prix Environnement"},
    {"title": "De l'ombre à la lumière", "director": "Davina & Sébastien Montaz-Rosset", "year": 2022, "award": "Prix Montagne"},
    {"title": "ORA", "director": "Michel Garcia", "year": 2022, "award": "Grand Prix du Public"},
    {"title": "Exposure", "director": "Holly Morris", "year": 2022, "award": "Prix de l'Aventurière"},
    {"title": "Lumdo Kolola", "director": "Nicolas Alliot", "year": 2022, "award": "Prix Ushuaïa TV"},
    # 2021 - 18ème Édition
    {"title": "Le mur de l'ombre", "director": "Eliza Kubarska", "year": 2021, "award": "Grand Prix du Festival"},
    {"title": "La panthère des neiges", "director": "Vincent Munier & Marie Amiguet", "year": 2021, "award": "Prix de l'Aventure"},
    {"title": "Requin'roll", "director": "Armel Ruy", "year": 2021, "award": "Prix Coup de Cœur"},
    {"title": "Quatre mois sur ma Biosphère", "director": "Laurent Sardi", "year": 2021, "award": "Prix Environnement"},
    {"title": "Climbing blind", "director": "Alastair Lee", "year": 2021, "award": "Prix Montagne"},
    {"title": "Sur les voix des Amériques", "director": "Julien Defourny", "year": 2021, "award": "Prix Ushuaïa TV"},
    {"title": "Dans les pas de Lou", "director": "Lou Nodet", "year": 2021, "award": "Prix de l'Aventurière"},
    # 2019 - 16ème Édition
    {"title": "Le cavalier mongol", "director": "Hamid Sardar", "year": 2019, "award": "Grand Prix du Festival"},
    {"title": "Les vélos de la colère", "director": "Charlie Tunbull & Cameron Ford", "year": 2019, "award": "Prix de l'Aventure"},
    {"title": "Water get no ennemy", "director": "Damien Castera & Arthur Bourbon", "year": 2019, "award": "Prix Coup de Cœur"},
    {"title": "Ours, simplement sauvage", "director": "Vincent Munier & Laurent Joffrion", "year": 2019, "award": "Prix Environnement"},
    {"title": "This mountain life", "director": "Grant Baldwin", "year": 2019, "award": "Prix Montagne"},
    {"title": "Du Pôule Nord au Pôule Sud", "director": "Guirec Soudée", "year": 2019, "award": "Prix Ushuaïa TV"},
    {"title": "Mada trek, la grande aventure", "director": "Sonia & Alexandre Poussin & Nicolas Thoma", "year": 2019, "award": "Prix Collégiens"},
    {"title": "Vincent Munier, éternel émerveillé", "director": "Benoît Aymon & Pierre-Antoine Hiroz", "year": 2019, "award": "Prix du Public Quai"},
    # 2018 - 15ème Édition
    {"title": "Dug out", "director": "Benjamin Sadd", "year": 2018, "award": "Grand Prix du Festival"},
    {"title": "The Dawn Wall", "director": "Josh Lowell & Peter Mortimer", "year": 2018, "award": "Prix de l'Aventure"},
    {"title": "Maman, c'est encore loin le désert", "director": "Aurélia Tazi & Charlène Gravel", "year": 2018, "award": "Prix Coup de Cœur"},
    {"title": "700 requins dans la nuit", "director": "Luc Marescot", "year": 2018, "award": "Prix Environnement"},
    {"title": "The last honey hunter", "director": "Ben Knight & Renan Ozturk", "year": 2018, "award": "Prix Montagne"},
    {"title": "Marcel, au sommet de son art", "director": "Nicolas Falquet", "year": 2018, "award": "Prix Ushuaïa TV"},
    {"title": "Les voies de la liberté", "director": "Mélusine Mallender & Christian Clot", "year": 2018, "award": "Prix de l'Aventurière"},
    {"title": "Himalaya, la marche au-dessus", "director": "Eliott Schonfeld", "year": 2018, "award": "Grand Prix du Public"},
    # 2017 - 14ème Édition
    {"title": "Antarctica, sur les traces de l'empereur", "director": "Jérôme Bouvier", "year": 2017, "award": "Grand Prix du Festival"},
    {"title": "Freeride aux Kouriles", "director": "Bertrand Delapierre", "year": 2017, "award": "Prix de l'Aventure"},
    {"title": "Au-delà de la lumière, le défi Baïkal", "director": "Olivier Weber", "year": 2017, "award": "Prix Coup de Cœur"},
    {"title": "Le paradis perdu", "director": "R. Gladu", "year": 2017, "award": "Prix Environnement"},
    {"title": "Groenland : les murmures de la glace", "director": "Evrard Wendenbaum", "year": 2017, "award": "Prix de l'Aventurière"},
    {"title": "Tom", "director": "Angel Esteban", "year": 2017, "award": "Prix Montagne"},
    {"title": "Surf the line", "director": "J. Frey", "year": 2017, "award": "Prix Collégiens"},
    {"title": "Le doigt de Dieu", "director": "Yannick Estienne", "year": 2017, "award": "Prix du Public Quai"},
    # 2016 - 13ème Édition
    {"title": "Les voyageurs sans trace", "director": "Iara Lee McCluskey", "year": 2016, "award": "Grand Prix du Festival"},
    {"title": "De l'eau sous la montagne", "director": "Jérôme Espla", "year": 2016, "award": "Prix de l'Aventure"},
    {"title": "Unbranded", "director": "Phillip Baribeau", "year": 2016, "award": "Prix Coup de Cœur"},
    {"title": "Les œuvres du Pamir", "director": "Morgan Monchaud, Baptiste Mathé & Vera", "year": 2016, "award": "Prix Environnement"},
    {"title": "L'appel de la banquise", "director": "M. Magidson", "year": 2016, "award": "Prix Collégiens"},
    {"title": "The Weekend Sailor", "director": "B. Arsuaga", "year": 2016, "award": "Grand Prix du Public"},
    {"title": "Papouasie, expédition au cœur d'un monde perdu", "director": "C. Tournadre", "year": 2016, "award": "Prix du Public Quai"},
    # 2015 - 12ème Édition
    {"title": "Le mystère Mérou", "director": "Gil Kebaïli", "year": 2015, "award": "Grand Prix du Festival"},
    {"title": "Bear Island", "director": "Inge Wegge", "year": 2015, "award": "Prix de l'Aventure"},
    {"title": "On ne marche qu'une fois sur la lune", "director": "C. Raylat", "year": 2015, "award": "Prix Coup de Cœur"},
    {"title": "And then we swam", "director": "Ben Finney & R. Ellender", "year": 2015, "award": "Prix Coup de Cœur"},
    {"title": "Sous les glaces du Groenland", "director": "Jean-Gabriel Leynaud", "year": 2015, "award": "Prix Environnement"},
    # 2014 - 11ème Édition
    {"title": "Solidream", "director": "Baptiste Mathé, Morgan Monchaud & S. Vera", "year": 2014, "award": "Grand Prix du Festival"},
    {"title": "China Jam", "director": "Evrard Wendenbaum", "year": 2014, "award": "Prix de l'Aventure"},
    {"title": "Gold of Bengal", "director": "Laurent Flahault", "year": 2014, "award": "Prix Coup de Cœur"},
    # 2013 - 10ème Édition
    {"title": "Sur le fil de Darwin, la dernière terre inconnue", "director": "Jean-François Didelot & Jeanne Delasnerie", "year": 2013, "award": "Grand Prix du Festival"},
    {"title": "Terminus Boréal", "director": "Bruno Peyronnet", "year": 2013, "award": "Prix de l'Aventure"},
    {"title": "Abyssinie, l'appel du loup", "director": "Laurent Joffrion", "year": 2013, "award": "Prix Coup de Cœur"},
    {"title": "Sur le grand Océan Blanc", "director": "Véronique Ovaldé & Hugues de Rosières", "year": 2013, "award": "Prix Collégiens"},
    # 2012 - 9ème Édition
    {"title": "7000 mètres au-dessus de la guerre", "director": "Louis Meunier", "year": 2012, "award": "Grand Prix du Festival"},
    {"title": "La voie Bonatti", "director": "Bruno Peyronnet", "year": 2012, "award": "Prix de l'Aventure"},
    {"title": "Nager au-delà des frontières", "director": "Robert Isébi & Charlène Gravel", "year": 2012, "award": "Grand Prix du Public"},
    {"title": "Una Boya Feliz", "director": "Jordi Munz Sola & Eloi Thomas", "year": 2012, "award": "Prix Coup de Cœur"},
    # 2011 - 8ème Édition
    {"title": "I believe I can fly", "director": "Sébastien Montaz-Rosset", "year": 2011, "award": "Grand Prix du Festival"},
    {"title": "Autour du monde sur un voilier de 6,50 mètres", "director": "Franck Aubert", "year": 2011, "award": "Prix de l'Aventure"},
    {"title": "Vertical Sailing Greenland", "director": "Sean Villanueva", "year": 2011, "award": "Grand Prix du Public"},
    {"title": "Jolokia, l'odyssée des bras cassés", "director": "Chloé Henry Biabaud", "year": 2011, "award": "Prix Collégiens"},
    # 2010 - 7ème Édition
    {"title": "On a marché sous le pôle", "director": "Thierry Robert", "year": 2010, "award": "Grand Prix du Festival"},
    {"title": "Enterrés volontaires de l'Antarctique", "director": "Djamel Tahi", "year": 2010, "award": "Prix de l'Aventure"},
    {"title": "L'extraordinaire tournée du Facteur Maignan", "director": "Patrick Soulabaille", "year": 2010, "award": "Grand Prix du Public"},
    {"title": "Un Mont Blanc pour y croire", "director": "Johan Perrier", "year": 2010, "award": "Prix Coup de Cœur"},
    {"title": "Le Grand Détour", "director": "Delphine Million & Damien Artéro", "year": 2010, "award": "Prix Collégiens"},
    # 2009 - 6ème Édition
    {"title": "Paris Jérusalem", "director": "Mathilde & Edouard Cortès & Frédéric Réau", "year": 2009, "award": "Grand Prix du Festival"},
    {"title": "Broad Peak", "director": "Sébastien Touta & Sébastien Colomb-Gros", "year": 2009, "award": "Prix de l'Aventure"},
    {"title": "Au-delà des Cimes", "director": "Rémy Tézier", "year": 2009, "award": "Grand Prix du Public"},
    {"title": "Sous les étoiles du pôle", "director": "Hugues de la Rosière", "year": 2009, "award": "Prix Collégiens"},
    # 2008 - 5ème Édition
    {"title": "Bérhault", "director": "Gilles Chappaz", "year": 2008, "award": "Grand Prix du Jury"},
    {"title": "Babouche dans les glaces du passage du nord-ouest", "director": "Sébastien Roubinet", "year": 2008, "award": "Prix de l'Aventure"},
    {"title": "Asiemut", "director": "Mélanie Carrier & Olivier Higgins", "year": 2008, "award": "Grand Prix du Public"},
    {"title": "Four Eight Thousands – l'Expédition Himalayenne de Mike Horn", "director": "David Ribeiro", "year": 2008, "award": "Prix Coup de Cœur"},
    {"title": "Les Ailes du Condor", "director": "Marco Visalberghi", "year": 2008, "award": "Prix Collégiens"},
    # 2007 - 4ème Édition
    {"title": "99 jours sur la glace", "director": "Jean-Gabriel Leynaud", "year": 2007, "award": "Grand Prix du Jury"},
    {"title": "Siberia", "director": "Philippe Sauve", "year": 2007, "award": "Prix de l'Aventure"},
    {"title": "Amazonian Vertigo", "director": "Evrard Wendenbaum", "year": 2007, "award": "Grand Prix du Public"},
    {"title": "L'île Rouge pas à pas", "director": "Cécile Clocheret & Lydie Bertrand", "year": 2007, "award": "Prix Coup de Cœur"},
    # 2006 - 3ème Édition
    {"title": "Marco, étoile filante", "director": "Bertrand Delapierre", "year": 2006, "award": "Grand Prix du Jury"},
    {"title": "Le Sahara sur un fil", "director": "Régis Belleville", "year": 2006, "award": "Prix de l'Aventure"},
    {"title": "Huis clos sous les étoiles", "director": "Emmanuel & Maximilien Berque", "year": 2006, "award": "Grand Prix du Public"},
    {"title": "Qui es tu Ashaninka ?", "director": "Jéromine Pasteur", "year": 2006, "award": "Prix Coup de Cœur"},
    # 2005 - 2ème Édition
    {"title": "Sur le fil des 4 000", "director": "Gilles Chappaz", "year": 2005, "award": "Grand Prix du Jury"},
    {"title": "Les chemins des cimes", "director": "Carole & Olivier Soudieux", "year": 2005, "award": "Prix de l'Aventure"},
    {"title": "Africa Trek", "director": "Sonia & Alexandre Poussin", "year": 2005, "award": "Grand Prix du Public"},
    {"title": "Les montagnes du silence", "director": "Daniel Buffard", "year": 2005, "award": "Prix Coup de Cœur"},
    # 2004 - 1ère Édition
    {"title": "Les chemins de la liberté", "director": "Sylvain Tesson", "year": 2004, "award": "Prix du Meilleur Film"},
    {"title": "Au pays des Djinns", "director": "Régis Belleville", "year": 2004, "award": "Prix du Meilleur Aventurier"},
    {"title": "Arktika", "director": "Gilles Elkaïm", "year": 2004, "award": "Prix Spécial du Jury"},
]


# Map awards to themes
AWARD_THEME_MAP = {
    "Prix Montagne": "mountain",
    "Prix Environnement": "environment",
    "Prix de l'Aventurière": "portrait",
    "Prix de l'Aventure": "adventure",
    "Grand Prix du Festival": "festival-winner",
    "Grand Prix du Jury": "festival-winner",
    "Grand Prix du Public": "audience-favorite",
    "Prix du Meilleur Film": "festival-winner",
}


class Command(BaseCommand):
    help = "Import FIFAV festival documentary data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made\n"))

        created_count = 0
        updated_count = 0
        skipped_count = 0
        directors_created = 0

        with transaction.atomic():
            # Ensure themes exist
            themes_to_create = set(AWARD_THEME_MAP.values())
            themes_to_create.add("adventure")  # Default theme

            for theme_slug in themes_to_create:
                theme_name = theme_slug.replace("-", " ").title()
                if not dry_run:
                    Theme.objects.get_or_create(
                        slug=theme_slug,
                        defaults={"name": theme_name}
                    )

            self.stdout.write(f"Ensured {len(themes_to_create)} themes exist\n")

            for doc_data in FIFAV_DOCUMENTARIES:
                title = doc_data["title"]
                year = doc_data["year"]
                director_str = doc_data["director"]
                award = doc_data["award"]

                # Check if documentary already exists
                slug = f"{slugify(title)}-{year}"
                existing = Documentary.objects.filter(slug=slug).first()

                if existing:
                    if dry_run:
                        self.stdout.write(f"  SKIP: {title} ({year}) - already exists")
                    skipped_count += 1
                    continue

                # Parse directors (handle multiple directors)
                director_names = self._parse_directors(director_str)

                if dry_run:
                    self.stdout.write(f"  CREATE: {title} ({year}) - Directors: {director_names}")
                    created_count += 1
                    continue

                # Get or create directors
                directors = []
                for name in director_names:
                    director, created = Person.objects.get_or_create(
                        slug=slugify(name),
                        defaults={"name": name}
                    )
                    directors.append(director)
                    if created:
                        directors_created += 1

                # Create documentary with placeholder data
                doc = Documentary.objects.create(
                    title=title,
                    year=year,
                    synopsis=f"Winner of {award} at FIFAV {year}. Directed by {director_str}.",
                    duration_minutes=90,  # Placeholder - will be enriched by TMDB
                    is_published=False,  # Don't publish until enriched
                )
                doc.directors.set(directors)

                # Add theme based on award
                theme_slug = AWARD_THEME_MAP.get(award, "adventure")
                theme = Theme.objects.filter(slug=theme_slug).first()
                if theme:
                    doc.themes.add(theme)

                created_count += 1
                self.stdout.write(f"  Created: {title} ({year})")

            if dry_run:
                # Rollback in dry run
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Import complete:"))
        self.stdout.write(f"  - Created: {created_count} documentaries")
        self.stdout.write(f"  - Skipped: {skipped_count} (already exist)")
        self.stdout.write(f"  - Directors created: {directors_created}")

        if not dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(
                "Next step: Run 'python manage.py enrich_tmdb' to fetch posters and synopses"
            ))

    def _parse_directors(self, director_str: str) -> list[str]:
        """Parse director string into list of names."""
        # Handle various separators
        directors = []

        # Split by common separators
        for sep in [" & ", ", ", " et "]:
            if sep in director_str:
                parts = director_str.split(sep)
                for part in parts:
                    part = part.strip()
                    if part and part not in directors:
                        directors.append(part)
                return directors

        # Single director
        return [director_str.strip()]
