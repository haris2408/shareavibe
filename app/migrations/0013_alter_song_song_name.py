# Generated by Django 4.1.7 on 2023-04-01 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_song'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='song_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
