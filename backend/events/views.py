from django.shortcuts import render
from events.tiling import tile_to_polygon, cluster_events, tile_to_latlon
from events.models import Event, Cluster
import mapbox_vector_tile
from django.http import HttpResponse
from django.contrib.gis.geos import Point
import time
from datetime import datetime
def get_tile_mvt(request, zoom, xtile, ytile, start_date, end_date):
    date_filter = parse_date_range(start_date, end_date)

    # use pre-computed clusters first (for zoom 0-8)
    if zoom <= 8:
        if date_filter:
            clusters = Cluster.objects.filter(
                zoom_level=zoom,
                tile_x=xtile,
                tile_y=ytile
            ).prefetch_related('cluster_events')
        
            if clusters.exists():
                events = []
                for cluster in clusters:
                    # get best event from cluster within date range
                    filtered_events = cluster.cluster_events.filter(**date_filter).order_by('-views')
                    if filtered_events.exists():
                        events.append(filtered_events.first())
            else:
                # fallback to dynamic clustering (shouldn't happen)
                print(f"No pre-computed clusters found for z{zoom}/{xtile}/{ytile}, falling back to dynamic")
                events = get_events_dynamic(zoom, xtile, ytile)
        else:
            # just use the cluster representative (no time filter)
            clusters = Cluster.objects.filter(
                zoom_level=zoom,
                tile_x=xtile,
                tile_y=ytile
            ).select_related('representative_event')
            
            if clusters.exists():
                events = [cluster.representative_event for cluster in clusters]
            else:
                # fallback to dynamic clustering (shouldn't happen)
                print(f"No pre-computed clusters found for z{zoom}/{xtile}/{ytile}, falling back to dynamic")
                events = get_events_dynamic(zoom, xtile, ytile)
    else:
        # use dynamic clustering for high zoom levels
        events = get_events_dynamic(zoom, xtile, ytile, date_filter)
    
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

def get_events_dynamic(zoom, xtile, ytile, date_filter=None):
    # fallback to original dynamic clustering algorithm with optional date filter
    bbox_polygon = tile_to_polygon(xtile, ytile, zoom)
    
    events_query = Event.objects.filter(location__within=bbox_polygon)
    
    # apply date filter if provided
    if date_filter:
        events_query = events_query.filter(**date_filter)
    
    events_in_tile = events_query.order_by("-views")
    
    clustered_events = cluster_events(events_in_tile, zoom)
    
    return clustered_events

def parse_date_range(start_date_str, end_date_str):
    # return django filter dict
    date_filter = {}
    
    if start_date_str != '-':
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        date_filter['date__gte'] = start_date
    
    if end_date_str != '-':
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        date_filter['date__lte'] = end_date
    
    return date_filter if date_filter else None