import math
from typing import Tuple, List
from django.contrib.gis.geos import Polygon
from events.models import Event
from django.contrib.gis.measure import D
from django.db.models import QuerySet

def latlon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
    # Determines which tile we're in based on coordinates and zoom
    n = 2.0 ** zoom
    lat_rad = math.radians(lat)

    # Equations found online, don't super understand how they work
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)

    return (xtile, ytile)

def tile_to_latlon(xtile: int, ytile: int, zoom: int) -> Tuple[float, float, float, float]:
    # Finds latlon bounding box corresponding to a tile
    n = 2 ** zoom

    lon_left = xtile / n * 360.0 - 180.0
    lon_right = (xtile + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ytile / n))))
    lat_bottom = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (ytile + 1) / n))))

    return (lon_left, lat_bottom, lon_right, lat_top)

def tile_to_polygon(xtile: int, ytile: int, zoom: int) -> Polygon:
    # Finds the bounding box polygon corresponding to a tile
    left, bottom, right, top = tile_to_latlon(xtile, ytile, zoom)

    return Polygon.from_bbox(left, bottom, right, top)

def find_cluster_radius(zoom: int) -> float:
    # Find how big of a radius each event should cover for zoom level
    base_radius = 5000.0

    # equation subject to change based on results
    return base_radius / (2 ** (zoom * 0.8))



def cluster_events(events: QuerySet[Event], zoom: int, max_events_per_tile: int = 50) -> List[Event]:
    # Pick the events that will be displayed
    clustered_events = []
    remaining_events = events.order_by('-views')

    while len(clustered_events) < max_events_per_tile and remaining_events:
        top_event = remaining_events[0]
        clustered_events.append(top_event)

        cluster_radius = find_cluster_radius(zoom)

        nearby_events = Event.objects.filter(
            location__distance_lte=(top_event.location, D(km=cluster_radius))
        )

        nearby_ids = list(nearby_events.values_list('id', flat=True))
        remaining_events = remaining_events.exclude(id__in=nearby_ids)

    return clustered_events
