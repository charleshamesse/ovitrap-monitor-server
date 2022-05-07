from django.db import models

class Record(models.Model):
    # ids and status
    uuid = models.CharField(max_length=100, null=True)
    user_id = models.CharField(max_length=200, null=True)
    processed = models.BooleanField()

    # location
    location_code = models.CharField(max_length=100, null=True)
    location_gps_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    location_gps_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    # pictures and counts
    front_pic_url = models.CharField(max_length=200)
    front_count = models.IntegerField(null=True)
    back_pic_url = models.CharField(max_length=200)
    back_count = models.IntegerField(null=True)
    loc_pic_url = models.CharField(max_length=200)
    
    # metadata
    happy = models.BooleanField(null=True)
    timestamp_upload = models.DateTimeField()
    timestamp_process = models.DateTimeField(null=True)