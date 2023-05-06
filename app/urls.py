from django.urls import path
from .views import add_user,homemanager,makelogin,homeadmin,add_cafe,playlist,add_song,play_song,update_cafe_status,update_queue,get_songs,update_queueisplayed
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings
import app.views as views

urlpatterns = [
    #path('add-user/', add_user, name='add_user'),
    #path('add-cafe/', add_cafe, name='add_cafe'),
    path('login/homeadmin/', homeadmin, name='homeadmin'),
    path('login/homeadmin/add_cafe/', add_cafe, name='add_cafe'),
    path('login/homeadmin/add_user/', add_user, name='add_user'),
    #path('playlists/', playlist, name='playlists'),
    path('login/', makelogin, name='makelogin'),
    path('login/homemanager', homemanager, name='homemanager'),
    path('login/homemanager/playlists/', playlist, name='playlists'),
    path('login/homemanager/playlists/<int:playlist_id>/add_song/', add_song, name='add_song'),
    path('api/play-song/', play_song, name='play_song'),
    path('api/update-cafe-status/', update_cafe_status, name='update_cafe_status'),
    path('api/update-queue/', update_queue, name='update_queue'),
    path('get-songs/', get_songs, name='get_songs'),
    path('update-queueisplayed/', update_queueisplayed, name='update_queueisplayed'),

    path('verify/<lat>/<long>', views.verify_coord, name='verify_coord'),
    path('getcafes/<lat>/<long>', views.get_cafes, name='get_cafes'),
    # Add other URL patterns as necessary
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
