from django.contrib import admin

# Register your models here.

from .models import Cafe, Playlist, CustomUser, Song, Queue, Address, CafeBlacklist, GlobalBlacklist,MobileAppUsers

admin.site.register(Cafe)
admin.site.register(Playlist)
admin.site.register(CustomUser)
admin.site.register(Song)
admin.site.register(Queue)
admin.site.register(Address)
admin.site.register(CafeBlacklist)
admin.site.register(GlobalBlacklist)
admin.site.register(MobileAppUsers)