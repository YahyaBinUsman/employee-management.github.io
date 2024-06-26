# Generated by Django 5.0.3 on 2024-04-14 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_alter_employee_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='hourly_rate',
            field=models.FloatField(default=15.0),
        ),
        migrations.AddField(
            model_name='employee',
            name='overtime_rate',
            field=models.FloatField(default=22.5),
        ),
    ]
