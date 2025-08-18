from django.contrib.gis.db import models

class Event(models.Model):
    name = models.CharField(max_length=500)
    date = models.DateField()
    wiki_url = models.URLField(max_length=500, unique=True)
    views = models.DecimalField(max_digits=12, decimal_places=1, default=0)
    location = models.PointField(srid=4326)