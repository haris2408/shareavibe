# Generated by Django 4.1.7 on 2023-04-01 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_song_song_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cafe',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
