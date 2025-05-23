# Generated by Django 5.2.1 on 2025-05-18 05:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0010_alter_car_id_alter_car_year_alter_reservation_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='delivery_address',
        ),
        migrations.AddField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='car',
            name='year',
            field=models.IntegerField(choices=[(2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025)], default=2025, verbose_name='year'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='booking_method',
            field=models.CharField(default='Online', max_length=100),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='visit_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
