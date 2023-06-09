
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class Cafe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    current_token = models.IntegerField(default=0, null=True)
    next_token = models.IntegerField(default=1, null=True)
    logo = models.ImageField(upload_to='cafe_logos', null=True, blank=True)

    def __str__(self):
        return self.name

class Playlist(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    playlist_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.cafe.name +": "+self.playlist_name 

class CafeBlacklist(models.Model):
    song_name = models.CharField(max_length=255,null=True)
    song_link = models.CharField(max_length=255)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)

class GlobalBlacklist(models.Model):
    song_name = models.CharField(max_length=255,null=True)
    song_link = models.CharField(max_length=255)

class CustomUser(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    password = models.CharField(max_length=255)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE,null=True)
    is_admin = models.BooleanField(default=False)
    is_login=models.BooleanField(default=False)
    session_id = models.CharField(max_length=255,null=True)
    is_approved=models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    
class Song(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song_name = models.CharField(max_length=255,null=True)
    song_link = models.CharField(max_length=255)
    is_blacklisted = models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.playlist.playlist_name+": "+self.song_name

class Queue(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    date = models.DateTimeField()
    song_link = models.CharField(max_length=255,null=True)
    song_name = models.CharField(max_length=255,null=True)
    token_no = models.IntegerField(null=True)
    is_played = models.BooleanField(default=False)
    def set_played(self):
        self.is_played = True
        self.save()
    def __str__(self) -> str:
        return self.cafe.name

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    full_address = models.CharField(max_length=100)
    area = models.CharField(max_length=50)
    topLeft_coord_lat = models.FloatField(default = 0.0, max_length=25)
    topLeft_coord_long = models.FloatField(default = 0.0, max_length=25)

    topRight_coord_lat = models.FloatField(default = 0.0, max_length=25)
    topRight_coord_long = models.FloatField(default = 0.0, max_length=25)

    bottomLeft_coord_lat = models.FloatField(default = 0.0, max_length=25)
    bottomLeft_coord_long = models.FloatField(default = 0.0, max_length=25)

    BottomRight_coord_lat = models.FloatField(default = 0.0, max_length=25)
    BottomRight_coord_long = models.FloatField(default = 0.0, max_length=25)

    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.full_address
    
class MobileAppUsers(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, unique=True)
    name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20, null=True)
    password = models.CharField(max_length=255, null=False)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE,null=True)
    token_no = models.IntegerField(null=True, default=-1)
    longitude = models.FloatField(default = 0.0, max_length=25)
    latitude = models.FloatField(default = 0.0, max_length=25)
    no_of_pushes = models.IntegerField(default=1)
    session_id = models.CharField(max_length=255,null=True)
    USERNAME_FIELD = 'email'