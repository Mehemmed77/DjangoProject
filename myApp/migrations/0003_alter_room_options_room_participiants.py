# Generated by Django 5.0.1 on 2024-01-13 18:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0002_topic_room_host_message_room_topic'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='room',
            name='participiants',
            field=models.ManyToManyField(blank=True, related_name='participiants', to=settings.AUTH_USER_MODEL),
        ),
    ]
