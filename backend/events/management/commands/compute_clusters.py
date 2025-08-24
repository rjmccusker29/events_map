from django.core.management.base import BaseCommand, CommandError
from events.models import Event, Cluster
from events.tiling import tile_to_polygon, cluster_events, latlon_to_tile, find_cluster_radius
import time
from django.db import transaction

class Command(BaseCommand):
    help = "Precompute event clusters"

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-zoom',
            type=int,
            default=0,
        )
        parser.add_argument(
            '--max-zoom',
            type=int,
            default=6,
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
        )

    def handle(self, *args, **options):
        min_zoom = options['min_zoom']
        max_zoom = options['max_zoom']

        if options['clear_existing']:
            self.stdout.write("Clearing existing clusters")
            Cluster.objects.all().delete()
            self.stdout.write("Cleared existing clusters")

        total_time = time.time()

        for zoom in range(min_zoom, max_zoom+1):
            zoom_start = time.time()
            tiles_processed = 0
            
            self.stdout.write(f"Processing zoom level {zoom}")
            tiles_with_events = self.get_tiles_with_events(zoom)
            self.stdout.write(f'Found {len(tiles_with_events)} tiles with events at zoom {zoom}')

            for tile_x, tile_y in tiles_with_events:
                tile_start = time.time()

                bbox_polygon = tile_to_polygon(tile_x, tile_y, zoom)
                events_in_tile = Event.objects.filter(
                    location__within=bbox_polygon
                ).order_by("-views")
                
                if events_in_tile.count() == 0:
                    continue
                
                clustered_events = cluster_events(events_in_tile, zoom)
                with transaction.atomic():
                    for event in clustered_events:
                        cluster, created = Cluster.objects.get_or_create(
                            zoom_level=zoom,
                            tile_x=tile_x,
                            tile_y=tile_y,
                            representative_event=event
                        )

                        if created:
                            # find all events that would be clustered with this representative
                            cluster_radius = find_cluster_radius(zoom)
                            nearby_events = events_in_tile.filter(
                                location__distance_lte=(event.location, cluster_radius)
                            )
                            cluster.cluster_events.set(nearby_events)

                tiles_processed += 1
                tile_time = time.time() - tile_start
                
                if tiles_processed % 10 == 0:
                    self.stdout.write(f'Processed {tiles_processed}/{len(tiles_with_events)} tiles ({tile_time:.2f}s)')
            
            zoom_time = time.time() - zoom_start
            self.stdout.write(
                self.style.SUCCESS(
                    f'Zoom {zoom} complete {zoom_time:.2f}s'
                )
            )

        total_time = time.time() - total_time
        self.stdout.write(
            self.style.SUCCESS(
                f'Cluster precomputation complete'
                f'Total time: {total_time:.2f}s'
            )
        )


    def get_tiles_with_events(self, zoom):
        # get all tiles at this zoom level that contain events
        tiles_with_events = set()

        events = Event.objects.all().values('location')
        for event in events:
            tile_x, tile_y = latlon_to_tile(event['location'].y, event['location'].x, zoom)
            tiles_with_events.add((tile_x, tile_y))

        return list(tiles_with_events)
    
