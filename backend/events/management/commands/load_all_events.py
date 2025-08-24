from django.core.management import BaseCommand, CommandError
from datetime import datetime
from django.contrib.gis.geos import Point
from events.models import Event
import time
import os
from django.conf import settings
import csv

class Command(BaseCommand):
    help = "load events from nj into the database"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Loading events")
        )

        csv_file = os.path.join(settings.BASE_DIR, 'events', 'data', 'all_events.csv')
        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file does not exist: {csv_file}')

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip if no coordinates
                longitude = row.get('longitude', '').strip()
                latitude = row.get('latitude', '').strip()
                if not longitude or not latitude:
                    continue

                Event.objects.get_or_create(
                    wiki_url=row['wikipedia_url'],
                    defaults={
                        'name': row['name'],
                        'date': datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                        'views': int(row.get('pageviews', '0') or '0'),
                        'location': Point(float(longitude), float(latitude), srid=4326),
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'Import complete'))