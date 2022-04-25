from django.db import models

class Record(models.Model):
    # uuid
    uuid = models.CharField(max_length=100)

    # location
    location_code = models.CharField(max_length=100)
    location_gps_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    location_gps_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    # pictures and counts
    front_pic_url = models.CharField(max_length=200)
    front_count = models.IntegerField()
    back_pic_url = models.CharField(max_length=200)
    back_count = models.IntegerField()
    
    # metadata
    happy = models.BooleanField()
    timestamp = models.DateTimeField()
    phone_info = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, null=True)