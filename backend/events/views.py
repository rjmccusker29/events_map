from django.shortcuts import render
from events.tiling import tile_to_polygon, cluster_events, tile_to_latlon
from events.models import Event
import mapbox_vector_tile
from django.http import HttpResponse
from django.contrib.gis.geos import Point

def get_tile_mvt(request, zoom, xtile, ytile):
    bbox_polygon = tile_to_polygon(xtile, ytile, zoom)
    
    events_in_tile = Event.objects.filter(
        location__within=bbox_polygon
    ).order_by("-views")

    clustered_events = cluster_events(events_in_tile, zoom)
    
    features = []
    for event in clustered_events:
        # convert to spherical mercator (EPSG:3857) for mvt encoding; fixes latitude shift problem
        point_4326 = Point(event.location.x, event.location.y, srid=4326)
        point_3857 = point_4326.transform(3857, clone=True)
            
        features.append({
            'geometry': {
                'type': 'Point',
                'coordinates': [point_3857.x, point_3857.y]
            },
            'properties': {
                'id': event.id,
                'name': event.name,
                'date': event.date.isoformat(),
                'views': float(event.views),
                'wiki_url': event.wiki_url,
            }
        })

    lon_left, lat_bottom, lon_right, lat_top = tile_to_latlon(xtile, ytile, zoom)

    # spherical mercator bounds; fixes latitude shift problem
    sw_point = Point(lon_left, lat_bottom, srid=4326)
    ne_point = Point(lon_right, lat_top, srid=4326)
    sw_3857 = sw_point.transform(3857, clone=True)
    ne_3857 = ne_point.transform(3857, clone=True)
    
    layer_data = {
        'name': 'events',
        'features': features
    }
    
    tile_data = mapbox_vector_tile.encode(
        layer_data, 
        quantize_bounds=(sw_3857.x, sw_3857.y, ne_3857.x, ne_3857.y)
    )

    response = HttpResponse(
        tile_data,
        content_type='application/vnd.mapbox-vector-tile'
    )

    return response