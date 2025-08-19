import math
from typing import Tuple, List
from django.contrib.gis.geos import Polygon

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
    base_radius = 50.0

    return base_radius / (2 ** (zoom * 0.8))

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Distance accounting for earth's curve
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    # Haversine formula (standard way to calculate distance on a sphere)
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance