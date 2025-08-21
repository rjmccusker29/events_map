from django.shortcuts import render
from events.tiling import tile_to_polygon, cluster_events, tile_to_latlon
from events.models import Event
import mapbox_vector_tile
from django.http import HttpResponse

def get_tile_mvt(request, zoom, xtile, ytile):
    bbox_polygon = tile_to_polygon(xtile, ytile, zoom)
    
    events_in_tile = Event.objects.filter(
        location__within=bbox_polygon
    ).order_by("-views")

    clustered_events = cluster_events(events_in_tile, zoom)
    lon_left, lat_bottom, lon_right, lat_top = tile_to_latlon(xtile, ytile, zoom)

    features = []
    for event in clustered_events:
        features.append({
            'geometry': {
                'type': 'Point',
                'coordinates': [event.location.x, event.location.y]  # lon, lat
            },
            'properties': {
                'id': event.id,
                'name': event.name,
                'date': event.date.isoformat(),
                'views': float(event.views),
                'wiki_url': event.wiki_url,
            }
        })

    layer_data = {
        'name': 'events',
        'features': features
    }
    
    tile_data = mapbox_vector_tile.encode(
        layer_data, 
        quantize_bounds=(lon_left, lat_bottom, lon_right, lat_top),
    )

    response = HttpResponse(
        tile_data,
        content_type='application/vnd.mapbox-vector-tile'
    )

    return response