from django.shortcuts import render
from events.tiling import tile_to_polygon, cluster_events, tile_to_latlon
from events.models import Event, Cluster
import mapbox_vector_tile
from django.http import HttpResponse
from django.contrib.gis.geos import Point
import time

def get_tile_mvt(request, zoom, xtile, ytile):
    start_time = time.time()
    
    # use pre-computed clusters first (for zoom 0-8)
    if zoom <= 8:
        clusters = Cluster.objects.filter(
            zoom_level=zoom,
            tile_x=xtile,
            tile_y=ytile
        ).select_related('representative_event')
        
        if clusters.exists():
            events = [cluster.representative_event for cluster in clusters]
            print(f"Using pre-computed clusters: {len(events)} events in {time.time() - start_time:.3f}s")
        else:
            # fallback to dynamic clustering (shouldn't happen)
            print(f"No pre-computed clusters found for z{zoom}/{xtile}/{ytile}, falling back to dynamic")
            events = get_events_dynamic(zoom, xtile, ytile)
    else:
        # use dynamic clustering for high zoom levels
        events = get_events_dynamic(zoom, xtile, ytile)
    
    features = []
    for event in events:
        # convert to spherical mercator (EPSG:3857) for mvt encoding
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

    # spherical mercator bounds
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

def get_events_dynamic(zoom, xtile, ytile):
    # fallback to original dynamic clustering algorithm
    bbox_polygon = tile_to_polygon(xtile, ytile, zoom)
    
    events_in_tile = Event.objects.filter(
        location__within=bbox_polygon
    ).order_by("-views")

    clustered_events = cluster_events(events_in_tile, zoom)
    
    return clustered_events