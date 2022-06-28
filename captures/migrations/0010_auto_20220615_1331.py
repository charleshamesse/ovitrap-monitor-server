# Generated by Django 3.2.5 on 2022-06-15 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captures', '0009_station'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='location_gps_lat',
            field=models.DecimalField(blank=True, decimal_places=15, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='station',
            name='location_gps_lon',
            field=models.DecimalField(blank=True, decimal_places=15, max_digits=18, null=True),
        ),
    ]