from django.shortcuts import render
from tiling import tile_to_polygon
from events.models import Event

def get_tile_mvt(request, xtile, ytile, zoom):
    bbox_polygon = tile_to_polygon(xtile, ytile, zoom)
    
    events_in_tile = Event.objects.filter(
        location__within=bbox_polygon
    ).order_by("-views")

    