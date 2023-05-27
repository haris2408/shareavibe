from django.urls import path
from .views import add_user,homemanager,makelogin,homeadmin,add_cafe,playlist,add_song,play_song,update_cafe_status,update_queue,get_songs,update_queueisplayed,add_to_blacklist,add_to_Gblacklist,play_youtube,add_to_blacklist2,logout_view,cafeblacklist,globalblacklist,remove_song,remove_blacklist_song,remove_Gblacklist_song,remove_playlist
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings
import app.views as views

urlpatterns = [
    #path('add-user/', add_user, name='add_user'),
    #path('add-cafe/', add_cafe, name='add_cafe'),
    path('api/playlists/<int:playlist_id>/remove', remove_playlist, name='remove_playlist'),
    path('api/blacklists/<int:blacklist_song_id>/remove', remove_blacklist_song, name='remove_blacklist_song'),
    path('api/Gblacklists/<int:Gblacklist_song_id>/remove', remove_Gblacklist_song, name='remove_Gblacklist_song'),
    path('api/songs/<int:song_id>/remove', remove_song, name='remove_song'),
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
    path('api/get_playlist/<cafe_id>', views.get_playlist, name='get_playlist'),
    path('api/get_songs/<playlist_id>', views.get_songs, name='get_songs'),
    path('api/login_mobile', views.login_mobile, name='login_mobile'),
    path('api/signup_mobile', views.signup_mobile, name='signup_mobile'),
    path('api/logout_mobile', views.logout_mobile, name='logout_mobile'),
    path('api/verify_session_mobile', views.verify_session_mobile, name='verify_session_mobile'),
    path('api/add_to_queue_mobile', views.add_to_queue_mobile, name = 'add_to_queue_mobile'),
    path('get_csrf_token/', views.get_csrf_token, name='get-csrf-token'),

    # Add other URL patterns as necessary
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
