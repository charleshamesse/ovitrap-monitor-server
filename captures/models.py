from django.db import models

class Capture(models.Model):
    location_code = models.CharField(max_length=100)
    front_pic_url = models.CharField(max_length=200)
    front_count = models.IntegerField()
    back_pic_url = models.CharField(max_length=200)
    back_count = models.IntegerField()
    happy = models.BooleanField()
    timestamp = models.DateTimeField()