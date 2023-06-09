# Generated by Django 4.1.7 on 2023-05-25 21:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_globalblacklist_remove_queue_song_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileAppUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('contact', models.CharField(max_length=20, null=True)),
                ('password', models.CharField(max_length=255)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profile_pics')),
                ('token_no', models.IntegerField(default=-1, null=True)),
                ('longitude', models.FloatField(default=0.0, max_length=25)),
                ('latitude', models.FloatField(default=0.0, max_length=25)),
                ('no_of_pushes', models.IntegerField(default=1)),
                ('session_id', models.CharField(max_length=255, null=True)),
                ('cafe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.cafe')),
            ],
        ),
    ]
