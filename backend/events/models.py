from django.contrib.gis.db import models

class Event(models.Model):
    name = models.CharField(max_length=500)
    date = models.DateField()
    wiki_url = models.URLField(max_length=500, unique=True)
    views = models.DecimalField(max_digits=12, decimal_places=1, default=0)
    location = models.PointField(srid=4326)


# tile generation takes too long with all events added, especially with large tiles. I want to have time
# filters so i can't precompute the tiles themselves. I'm pregenerating the clusters (areas in each zoom level 
# represented by a single event) and picking the representative of that cluster based off time filters. 

class Cluster(models.Model):
    zoom_level = models.IntegerField()
    tile_x = models.IntegerField()
    tile_y = models.IntegerField()
    representative_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    cluster_events = models.ManyToManyField(Event, related_name='clusters')
    
    class Meta:
        indexes = [
            models.Index(fields=['zoom_level', 'tile_x', 'tile_y'])
        ]
        unique_together = ['zoom_level', 'tile_x', 'tile_y', 'representative_event']