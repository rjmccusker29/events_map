from django.core.management import BaseCommand, CommandError
import requests
from datetime import datetime, timedelta
from urllib.parse import quote
from django.contrib.gis.geos import Point
from events.models import Event
import time

class Command(BaseCommand):
    help = "load events from nj into the database"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Loading events")
        )

        events = self.run_sparql_query()
        event_count = len(events)
        if not events:
            raise CommandError('no events found')
        self.stdout.write(f'Found {event_count} events')

        created_count = 0
        updated_count = 0

        for i, event_data in enumerate(events, 1):
            try:
                event, created = self.process_event(event_data)
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created: {event.name}')
                else:
                    updated_count += 1
                    self.stdout.write(f'  Updated: {event.name}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing event {i}/{event_count}: {str(e)}')
                )
                continue

            time.sleep(0.1) # avoid api limit
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Import complete! Created: {created_count}, Updated: {updated_count}'
            )
        )

    def run_sparql_query(self):
        sparql_query = """
            SELECT DISTINCT ?item ?itemLabel ?itemDescription ?pointInTime ?startTime ?locationLabel ?instanceOfLabel ?article ?coords WHERE {
            # any item with a time
            {
                ?item wdt:P585 ?pointInTime .  # point in time
            } UNION {
                ?item wdt:P580 ?startTime .    # start time
            }
            
            # has a location property
            ?item wdt:P276 ?location .
            
            # anything in New Jersey
            ?location wdt:P131* wd:Q1408 .  # New Jersey
            
            # coordinates if available (either from item or location)
            OPTIONAL { 
                ?item wdt:P625 ?coords .
            }
            OPTIONAL { 
                ?location wdt:P625 ?coords .
            }
            
            # show what type of thing this is
            OPTIONAL { ?item wdt:P31 ?instanceOf . }
            
            # must have english wikipedia article
            ?article schema:about ?item ;
                    schema:isPartOf <https://en.wikipedia.org/> .
            
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            ORDER BY ?pointInTime ?startTime
            """
        
        endpoint = "https://query.wikidata.org/sparql"
        headers = {
            'User-Agent': 'HistoricalEventsApp/1.0 (thepotentialofpaper@gmail.com)',
            'Accept': 'application/sparql-results+json'
        }

        params = {
            'query': sparql_query,
            'format': 'json'
        }
        
        self.stdout.write("Running SPARQL query...")
        response = requests.get(endpoint, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data['results']['bindings']
        else:
            raise CommandError(f"SPARQL query failed: {response.status_code} - {response.text}")

    def process_event(self, event_data):
        name = event_data.get('itemLabel', {}).get('value', 'Unknown Event')
        wiki_url = event_data.get('article', {}).get('value', '')
        date = self.extract_date(event_data)
        coordinates = self.extract_coordinates(event_data)

        if not wiki_url:
            raise ValueError("No Wikipedia URL found")
        
        if not coordinates:
            raise ValueError("No coordinates found")
        
        if not date:
            raise ValueError("No date found")
        
        views = 0
        wikipedia_title = self.extract_wiki_title(wiki_url)
        if wikipedia_title:
            views = self.get_pageviews(wikipedia_title)

        event, created = Event.objects.update_or_create(
            wiki_url=wiki_url,
            defaults={
                'name': name,
                'date': date,
                'views': views,
                'location': coordinates,
            }
        )

        return event, created

    def extract_wiki_title(self, url):
        if not url or "en.wikipedia.org/wiki/" not in url:
            return None
        return url.split('/wiki/')[-1]

    def get_pageviews(self, article_title):
        if not article_title:
            return 0
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')

            encoded_title = quote(article_title.replace(' ', '_'))

            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{encoded_title}/daily/{start_str}/{end_str}"
            headers = {
                'User-Agent': 'HistoricalEventsApp/1.0 (thepotentialofpaper@gmail.com)'
            }
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "items" in data and data["items"]:
                    total_views = sum(item.get("views", 0) for item in data["items"])
                    avg_daily_views = total_views / len(data['items']) if data['items'] else 0
                    return round(avg_daily_views, 1)
            elif response.status_code == 404:
                self.stdout.write(f"Article not found in pageviews api: {article_title}")
                return 0
            else:
                self.stdout.write(f"API error {response.status_code} for: {article_title}")
                return 0

        except Exception as e:
            self.stdout.write(f"Error fetching pageviews for {article_title}: {str(e)}")
        
    def extract_date(self, event_data):
        point_in_time = event_data.get('pointInTime', {}).get('value')
        start_time = event_data.get('startTime', {}).get('value')

        date_str = point_in_time or start_time

        if date_str:
            date_only = date_str.split('T')[0]
            try:
                return datetime.strptime(date_only, '%Y-%m-%d').date()
            except ValueError:
                # Handle cases like "+1776-07-04T00:00:00Z"
                if date_only.startswith('+'):
                    date_only = date_only[1:]
                return datetime.strptime(date_only, '%Y-%m-%d').date()
            
        return None
    
    def extract_coordinates(self, event_data):
        coords_str = event_data.get('coords', {}).get('value', '')

        if coords_str and coords_str.startswith('Point('):
            # Format: "Point(-74.756 40.337)"
            coords_part = coords_str.replace('Point(', '').replace(')', '')
            try:
                lon, lat = map(float, coords_part.split())
                return Point(lon, lat, srid=4326)
            except (ValueError, IndexError):
                pass
        
        return None