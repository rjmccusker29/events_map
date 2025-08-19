from django.shortcuts import render
from tiling import tile_to_polygon, cluster_events
from events.models import Event
import mapbox_vector_tile
from django.http import HttpResponse

def get_tile_mvt(request, zoom, xtile, ytile):
    bbox_polygon = tile_to_polygon(xtile, ytile, zoom)
    
    events_in_tile = Event.objects.filter(
        location__within=bbox_polygon
    ).order_by("-views")

    clustered_events = cluster_events(events_in_tile, zoom)

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

    tile_data = mapbox_vector_tile.encode({
        'events': {
            'features': features,
            'version': 2
        }
    })

    response = HttpResponse(
        tile_data,
        content_type='application/vnd.mapbox-vector-tile'
    )

    return response