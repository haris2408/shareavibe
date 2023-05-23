from django.urls import path
from .views import add_user,homemanager,makelogin,homeadmin,add_cafe,playlist,add_song,play_song,update_cafe_status,update_queue,get_songs,update_queueisplayed,add_to_blacklist,add_to_Gblacklist,play_youtube,add_to_blacklist2,logout_view,cafeblacklist,globalblacklist
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings
import app.views as views

urlpatterns = [
    #path('add-user/', add_user, name='add_user'),
    #path('add-cafe/', add_cafe, name='add_cafe'),
    path('logout_view/', logout_view, name='logout_view'),
    path('login/homeadmin/', homeadmin, name='homeadmin'),
    path('login/homeadmin/add_cafe/', add_cafe, name='add_cafe'),
    path('login/homeadmin/add_user/', add_user, name='add_user'),
    #path('playlists/', playlist, name='playlists'),
    path('login/', makelogin, name='makelogin'),
    path('login/homemanager', homemanager, name='homemanager'),
    path('login/homemanager/playlists/', playlist, name='playlists'),
    path('login/homemanager/cafeblacklist/', cafeblacklist, name='cafeblacklist'),
    path('login/homeadmin/globalblacklist/', globalblacklist, name='globalblacklist'),
    path('login/homemanager/playlists/<int:playlist_id>/add_song/', add_song, name='add_song'),
    path('api/play-song/', play_song, name='play_song'),
    path('api/update-cafe-status/', update_cafe_status, name='update_cafe_status'),
    path('api/update-queue/', update_queue, name='update_queue'),
    path('get-songs/', get_songs, name='get_songs'),
    path('update-queueisplayed/', update_queueisplayed, name='update_queueisplayed'),
    path('api/add-to-blacklist/', add_to_blacklist, name='add_to_blacklist'),
    path('api/add-to-blacklist2/', add_to_blacklist2, name='add_to_blacklist2'),
    path('api/add-to-Gblacklist/', add_to_Gblacklist, name='add_to_Gblacklist'),
    path('verify/<lat>/<long>', views.verify_coord, name='verify_coord'),
    path('getcafes/<lat>/<long>', views.get_cafes, name='get_cafes'),
    path('api/play-youtube/', play_youtube, name='play_youtube'),
    # Add other URL patterns as necessary
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
