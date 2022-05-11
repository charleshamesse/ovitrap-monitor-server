from django.db import models
from rest_framework import serializers

class Record(models.Model):
    # ids and status
    uuid = models.CharField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=100)
    processed = models.BooleanField()

    # location
    location_code = models.CharField(max_length=100, null=True, blank=True)
    location_gps_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_gps_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # pictures and counts
    front_pic_url = models.CharField(max_length=200)
    front_count = models.IntegerField(null=True, blank=True)
    back_pic_url = models.CharField(max_length=200)
    back_count = models.IntegerField(null=True, blank=True)
    loc_pic_url = models.CharField(max_length=200)
    
    # metadata
    happy = models.BooleanField(null=True, blank=True)
    timestamp_upload = models.DateTimeField()
    timestamp_process = models.DateTimeField(null=True, blank=True)