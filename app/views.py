import uuid
from django.contrib import messages
from django.forms import model_to_dict
from app.models import CustomUser,Address,Cafe,Playlist,Song,Queue,CafeBlacklist,GlobalBlacklist,MobileAppUsers
from django.shortcuts import get_object_or_404, render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from googleapiclient.discovery import build
from django.contrib.auth import logout
import re
import json
from django.core.serializers import serialize
from django.http import JsonResponse
from django.db.models.query import QuerySet
from django.db.models import Model
from django.utils.encoding import force_str
import json
from .helper_functions.is_point_in_polygon import is_inside_polygon
from .helper_functions.is_cafe_in_radius import get_cafes_within_radius
from .serializers import cafeSerializer, addressSerializer
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

def get_managers(request):
    manager = CustomUser.objects.filter(is_approved=False).values('email', 'contact', 'password')
    return JsonResponse({'get_managers': list(manager)})

def add_manager(request):
    if request.method == 'POST':
        # Get the data from the request
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        user = CustomUser.objects.create(email=email, contact=contact, password=password)

        # Redirect to the homepage
        return redirect('login')

    return render(request, 'signup_manager.html')

def get_global_blacklist(request):
    global_blacklist = GlobalBlacklist.objects.all().values('song_link', 'song_name')
    return JsonResponse({'global_blacklist': list(global_blacklist)})

def get_cafe_name(request):
    cafe_name = Cafe.objects.all().values('name', 'logo')
    return JsonResponse({'cafe_name': list(cafe_name)})

@csrf_exempt
def remove_playlist(request, playlist_id):
    try:
        playlist = Playlist.objects.get(id=playlist_id)
        songs = Song.objects.filter(playlist=playlist)
        songs.delete()
        playlist.delete()
        return JsonResponse({"message": "Playlist and associated songs removed successfully."})
    except Playlist.DoesNotExist:
        return JsonResponse({"message": "Playlist not found."}, status=404)
    except Exception as e:
        return JsonResponse({"message": "An error occurred.", "error": str(e)}, status=500)

@csrf_exempt  # Disabling CSRF protection for simplicity. Make sure to enable it in production.
def remove_Gblacklist_song(request, Gblacklist_song_id):
    try:
        blacklist_song = GlobalBlacklist.objects.get(id=Gblacklist_song_id)
        blacklist_song.delete()
        return JsonResponse({"message": "Blacklist song removed successfully."})
    except CafeBlacklist.DoesNotExist:
        return JsonResponse({"message": "Blacklist song not found."}, status=404)
    except Exception as e:
        return JsonResponse({"message": "An error occurred.", "error": str(e)}, status=500)

@csrf_exempt  # Disabling CSRF protection for simplicity. Make sure to enable it in production.
def remove_blacklist_song(request, blacklist_song_id):
    try:
        blacklist_song = CafeBlacklist.objects.get(id=blacklist_song_id)
        blacklist_song.delete()
        return JsonResponse({"message": "Blacklist song removed successfully."})
    except CafeBlacklist.DoesNotExist:
        return JsonResponse({"message": "Blacklist song not found."}, status=404)
    except Exception as e:
        return JsonResponse({"message": "An error occurred.", "error": str(e)}, status=500)
    
@csrf_exempt  # Disabling CSRF protection for simplicity. Make sure to enable it in production.
def remove_song(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
        song.delete()
        return JsonResponse({"message": "Song removed successfully."})
    except Song.DoesNotExist:
        return JsonResponse({"message": "Song not found."}, status=404)
    except Exception as e:
        return JsonResponse({"message": "An error occurred.", "error": str(e)}, status=500)
    
def globalblacklist(request):
    cafe_id = request.session.get('cafe_id')
    if request.method == 'POST':
        
        # Extract the song link from the form data
        blacklist_link = request.POST['blacklist_link']
        existing_blacklist = GlobalBlacklist.objects.filter(song_link=blacklist_link).exists()
        if existing_blacklist:
            # Display a message indicating that the song is already blacklisted
            messages.info(request, 'This song is already blacklisted.')
        else:
            api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
            youtube = build('youtube', 'v3', developerKey=api_key)
            video_id = re.search(r'(?<=v=)[^&]+', blacklist_link).group()
            video_info = youtube.videos().list(part='snippet', id=video_id).execute()
            song_name = video_info['items'][0]['snippet']['title']
            # Create a new Song object with the extracted link and the playlist object
            blacklist = GlobalBlacklist.objects.create(song_link=blacklist_link,song_name=song_name)
        return redirect('globalblacklist')
  
    blacklists = GlobalBlacklist.objects.all()
    
    context = {'blacklists': blacklists}
    return render(request, 'globalblacklist.html', context)



def cafeblacklist(request):
    cafe_id = request.session.get('cafe_id')
    if request.method == 'POST':
        
        # Extract the song link from the form data
        blacklist_link = request.POST['blacklist_link']
        existing_blacklist = CafeBlacklist.objects.filter(song_link=blacklist_link, cafe_id=cafe_id).exists()
        if existing_blacklist:
            # Display a message indicating that the song is already blacklisted
            messages.info(request, 'This song is already blacklisted.')
        else:
            api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
            youtube = build('youtube', 'v3', developerKey=api_key)
            video_id = re.search(r'(?<=v=)[^&]+', blacklist_link).group()
            video_info = youtube.videos().list(part='snippet', id=video_id).execute()
            song_name = video_info['items'][0]['snippet']['title']
            # Create a new Song object with the extracted link and the playlist object
            blacklist = CafeBlacklist.objects.create(song_link=blacklist_link,song_name=song_name,cafe_id=cafe_id)
        return redirect('cafeblacklist')
  
    blacklists = CafeBlacklist.objects.filter(cafe_id=cafe_id).values('id','song_name', 'song_link')
    
    context = {'blacklists': blacklists}
    return render(request, 'cafeblacklist.html', context)

def logout_view(request):
    cafe_id = request.session.get('cafe_id')
    if cafe_id:
        try:
            user = CustomUser.objects.get(cafe_id=cafe_id)
            user.is_login = False
            user.session_id=None
            user.save()
        except CustomUser.DoesNotExist:
            pass
    return redirect('login')


def update_queueisplayed(request):
  if request.method == 'POST':
    song_link = request.POST.get('song_link')
    song_link= "https://www.youtube.com/watch?v=" + song_link;
    cafe_id = request.session.get('cafe_id')
    queue = Queue.objects.filter(cafe_id=cafe_id, is_played=False,song_link=song_link).first()
    if queue:
      queue.is_played = True
      queue.save()
      return JsonResponse({'message': 'Queue object updated successfully.'})
    else:
      return JsonResponse({'message': 'No matching Queue object found.'})
  else:
    return JsonResponse({'message': 'Invalid request method.'})

class CustomJsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that can serialize Django QuerySet and Model objects.
    """

    def default(self, obj):
        if isinstance(obj, QuerySet):
            return serialize('json', obj)
        elif isinstance(obj, Model):
            return json.loads(serialize('json', [obj])[1:-1])
        else:
            return super().default(obj)


def get_songss(request):
    cafe_id = request.session.get('cafe_id')
    queue = Queue.objects.filter(cafe_id=cafe_id, is_played=False)
    newsongs = [(q.song_link, q.song_name, q.is_played,q.token_no) for q in queue]
    data = {'newsongs': newsongs}
    return JsonResponse(data, encoder=CustomJsonEncoder)

@csrf_exempt
def update_queue(request):
    if request.method == 'POST':
        cafe_id = request.session.get('cafe_id')
        queue_id = request.POST.get('queue_id')
        print('The first queue ID is:', queue_id)
        try:
            queue = Queue.objects.get(id=queue_id,cafe_id=cafe_id,)
            queue.is_played = True
            queue.save()
            return JsonResponse({'status': 'success'})
        except Queue.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'Queue object with id {queue_id} does not exist'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def update_cafe_status(request):
    if request.method == 'POST':
        cafe_id = request.session.get('cafe_id')
        cafe = Cafe.objects.get(id=cafe_id)
        cafe.is_active = not cafe.is_active  # Toggle the is_active field
        cafe.save()
        # Return success response with updated cafe object
        return JsonResponse({'success': True, 'cafe': {
            'is_active': cafe.is_active,
            'current_token': cafe.current_token,
            'next_token': cafe.next_token,
        }})
    # Return error response if not POST request
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def play_song(request):
    if request.method == 'POST':
        #song_id = request.POST.get('song_id')
        cafe_id = request.session.get('cafe_id')
        song_link = request.POST.get('song_link')
        cafe = Cafe.objects.get(id=cafe_id)
        #song = Song.objects.get(id=song_id)
        #song = Song.objects.get(song_link=song_link)
        song = Song.objects.filter(song_link=song_link).first()
        next_token = cafe.next_token
        # create new Queue object using song_id and song_link
        queue = Queue.objects.create(song_link=song_link ,date=timezone.now(),cafe_id=cafe_id)
        queue.token_no=next_token
        queue.song_name = song.song_name
        queue.save()
        cafe.next_token+=1
        cafe.save()
        # return success response
        return JsonResponse({'success': True})
    # return error response if not POST request
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
@csrf_exempt
def play_youtube(request):
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        cafe_id = request.session.get('cafe_id')
        # Check if the youtube_link is blacklisted
        if cafe_id and youtube_link:
            is_blacklisted2 = GlobalBlacklist.objects.filter(song_link=youtube_link).exists()
            
            if is_blacklisted2:
                print('This song is globally blacklisted')
                return JsonResponse({'success': False, 'error': 'This song is globally blacklisted'})
            is_blacklisted = CafeBlacklist.objects.filter(cafe_id=cafe_id,song_link=youtube_link).exists()
            if is_blacklisted:
                print('This song is blacklisted')
                return JsonResponse({'success': False, 'error': 'This song is blacklisted'})
            else:
                cafe = Cafe.objects.get(id=cafe_id)
                next_token = cafe.next_token
                api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
                youtube = build('youtube', 'v3', developerKey=api_key)
                video_id = re.search(r'(?<=v=)[^&]+', youtube_link).group()
                video_info = youtube.videos().list(part='snippet', id=video_id).execute()
                song_name = video_info['items'][0]['snippet']['title']
                
                queue = Queue.objects.create(song_link=youtube_link,date=timezone.now(),cafe_id=cafe_id,song_name=song_name)
                queue.token_no=next_token
                cafe.next_token += 1
                cafe.save()
                queue.save()
                return JsonResponse({'success': True,'token':queue.token_no})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def add_to_blacklist(request):
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        cafe_id = request.session.get('cafe_id')
        cafe_blacklist = CafeBlacklist.objects.filter(cafe_id=cafe_id, song_link=youtube_link)
        if cafe_blacklist.exists():
            print('This song is already blacklisted')
        else:
            api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
            youtube = build('youtube', 'v3', developerKey=api_key)
            video_id = re.search(r'(?<=v=)[^&]+', youtube_link).group()
            video_info = youtube.videos().list(part='snippet', id=video_id).execute()
            song_name = video_info['items'][0]['snippet']['title']
            CafeBlacklist.objects.create(song_link=youtube_link, cafe_id=cafe_id,song_name=song_name)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def add_to_blacklist2(request):
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        cafe_id = request.session.get('cafe_id')
        
        # Update is_played=true for songs with the same youtube_link in the Queue model for that cafe
        Queue.objects.filter(song_link=youtube_link,cafe_id=cafe_id).update(is_played=True)
        cafe_blacklist = CafeBlacklist.objects.filter(cafe_id=cafe_id, song_link=youtube_link)
        if cafe_blacklist.exists():
            print('This song is already blacklisted')
        else:
            api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
            youtube = build('youtube', 'v3', developerKey=api_key)
            video_id = re.search(r'(?<=v=)[^&]+', youtube_link).group()
            video_info = youtube.videos().list(part='snippet', id=video_id).execute()
            song_name = video_info['items'][0]['snippet']['title']
            CafeBlacklist.objects.create(song_link=youtube_link, cafe_id=cafe_id,song_name=song_name)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@csrf_exempt
def add_to_Gblacklist(request):
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        cafe_blacklist = GlobalBlacklist.objects.filter(song_link=youtube_link)
        if cafe_blacklist.exists():
            print('This song is already blacklisted')
        else:
            api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
            youtube = build('youtube', 'v3', developerKey=api_key)
            video_id = re.search(r'(?<=v=)[^&]+', youtube_link).group()
            video_info = youtube.videos().list(part='snippet', id=video_id).execute()
            song_name = video_info['items'][0]['snippet']['title']
            GlobalBlacklist.objects.create(song_link=youtube_link, song_name=song_name)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    
def add_cafe(request):
    if request.method == 'POST':
        # Get the data from the request
        cafe_name = request.POST.get('cafe_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        full_address = request.POST.get('address')
        area = request.POST.get('area')
        tllat = request.POST.get('tllat')
        tllong = request.POST.get('tllong')
        trlat = request.POST.get('trlat')
        trlong = request.POST.get('trlong')
        bllat = request.POST.get('bllat')
        bllong = request.POST.get('bllong')
        brlat = request.POST.get('brlat')
        brlong = request.POST.get('brlong')

        # Retrieve the uploaded file data
        print(request.FILES)
        logo = request.FILES.get('logo')
        print(logo)

        # Create the Cafe object
        cafe = Cafe.objects.create(name=cafe_name, logo=logo)

        # Create the Address object
        # address = Address.objects.create(full_address=full_address, area=area, topLeft_coord_lat = tllat, , cafe=cafe)
        address = Address.objects.create(full_address=full_address, area=area, topLeft_coord_lat = tllat, topLeft_coord_long = tllong, topRight_coord_lat = trlat, topRight_coord_long = trlong, bottomLeft_coord_lat = bllat, bottomLeft_coord_long = bllong, BottomRight_coord_lat = brlat, BottomRight_coord_long = brlong, cafe=cafe)

        # Create the CustomUser object
        user = CustomUser.objects.create(email=email, contact=contact, password=password, cafe=cafe,is_approved=True)

        # Redirect to the homepage
        return redirect('homeadmin')

    return render(request, 'add_cafe.html')

def homemanager(request):
    cafe_id = request.session.get('cafe_id')
    try:
        cafe = Cafe.objects.get(id=cafe_id)
    except Cafe.DoesNotExist:
        print(f"No Cafe object found with id {cafe_id}")
        cafe = None
    queue = Queue.objects.filter(cafe_id=cafe_id, is_played=False)
    songs = [(q.song_link,q.song_name,q.is_played,) for q in queue]
    context = {'cafe': cafe, 'songs': songs, 'queue': queue}
    return render(request, 'homemanager.html', context)

def homeadmin(request):
    # Your view code here
    return render(request, 'homeadmin.html')

def add_user(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        password = request.POST['password']
        is_admin = request.POST.get('is_admin')
        if is_admin !='True':
            cafe_id = request.POST['cafe_id']
            # Check if email already exists in the database
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email is already registered.')
                return redirect('add_user')
            # Check if cafe with given id exists
            if not Cafe.objects.filter(id=cafe_id).exists():
                messages.error(request, f'Cafe with ID {cafe_id} does not exist.')
                return redirect('add_user')
        if is_admin == 'True':
            is_admin = True
            user = CustomUser(name=name, email=email, contact=contact, password=password, is_admin=is_admin)
            user.save()
        else:
            is_admin = False
            user = CustomUser(name=name, email=email, contact=contact, password=password, cafe_id=cafe_id, is_admin=is_admin)
            user.save()
        
        
        return redirect('homeadmin')

    return render(request, 'add_user.html')

def add_song(request, playlist_id):
    # Retrieve the playlist with the given ID
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    if request.method == 'POST':
        # Extract the song link from the form data
        song_link = request.POST['song_link']
        api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
        youtube = build('youtube', 'v3', developerKey=api_key)
        video_id = re.search(r'(?<=v=)[^&]+', song_link).group()
        video_info = youtube.videos().list(part='snippet', id=video_id).execute()
        song_name = video_info['items'][0]['snippet']['title']
        # Create a new Song object with the extracted link and the playlist object
        song = Song.objects.create(playlist=playlist, song_link=song_link,song_name=song_name)
        
        # Redirect to the add_song page for this playlist
        return redirect('add_song', playlist_id=playlist_id)
    
    # Retrieve the list of songs for this playlist
    songs = playlist.song_set.all()
    
    # Render the add_song template with the list of songs
    context = {'playlist': playlist, 'songs': songs}
    return render(request, 'add_song.html', context)

def playlist(request):
    cafe_id = request.session.get('cafe_id')
    if request.method == 'POST':
        playlist_name = request.POST['playlist_name']
        new_playlist = Playlist(playlist_name=playlist_name, cafe_id=cafe_id)
        new_playlist.save()
        return redirect('playlists')
    else:
        playlists = Playlist.objects.filter(cafe_id=cafe_id)
        return render(request, 'playlists.html', {'playlists': playlists})

def makelogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None
        request.session['cafe_id'] = user.cafe.id if user and user.cafe else None
        if user is not None and password==user.password:
            # Get the cafe associated with the user
            cafe = user.cafe
            if user.is_admin:
                
                session_id = uuid.uuid4()
                # store the session id in the database
                user.session_id = session_id
                user.save()
                response_data = {
                        'status': 'success',
                        'session_id': session_id,
                        'user': model_to_dict(user)
                        
                    }
                return JsonResponse(response_data)
            else:
                cafe_dict = model_to_dict(cafe)
                if cafe_dict['logo']:
                    cafe_dict['logo'] = cafe_dict['logo'].url
                session_id = uuid.uuid4()
                # store the session id in the database
                user.session_id = session_id
                user.save()
                response_data = {
                        'status': 'success',
                        'session_id': session_id,
                        'user': model_to_dict(user),
                        'logo' : cafe_dict['logo']
                        
                    }
                return JsonResponse(response_data)
        else:
            print(password)
            # Login failed, display error message on the login form
            messages.error(request, 'Incorrect username or password')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def verify_coord(request,lat,long):
    latt = float(lat)
    longg = float(long)
    adresses = Address.objects.all()
    print(lat)
    print(long)
    print(adresses)
    for addr in adresses:
        if is_inside_polygon((latt,longg),[(addr.topLeft_coord_lat,addr.topLeft_coord_long),(addr.topRight_coord_lat,addr.topRight_coord_long),(addr.BottomRight_coord_lat,addr.BottomRight_coord_long),(addr.bottomLeft_coord_lat,addr.bottomLeft_coord_long)]):
            return JsonResponse({'status':'success','cafe_id':addr.cafe.id, 'cafe_name':addr.cafe.name})
    return JsonResponse({'status':'failure'})
    


def get_cafes(request,lat,long):
    cafes = get_cafes_within_radius(float(lat),float(long),70)
    if cafes:
        cafes_list = []
        for cafe in cafes:
            cafe_dict = model_to_dict(cafe)
            # convert the logo to the URL string representation
            if cafe_dict['logo']:
                cafe_dict['logo'] = cafe_dict['logo'].url
            cafes_list.append(cafe_dict) 
        return JsonResponse({'status':'success','cafes':cafes_list})
    return JsonResponse({'status':'failure'})

def thisIsjustatest(request):
    return JsonResponse({'status':'success'})

def get_playlist(request,cafe_id):
    if request.method == 'GET':
        # cafe_id = request.GET.get('cafe_id')
        cafe_id = int(cafe_id)
        playlists = Playlist.objects.filter(cafe_id=cafe_id)
        print(playlists)
        if playlists:
            playlists = [model_to_dict(playlist) for playlist in playlists]
            return JsonResponse({'status':'success','playlists':playlists})
    return JsonResponse({'status':'failure'})

def get_songs(request, playlist_id):
    if request.method == 'GET':
        # playlist_id = request.data.get('playlist_id')
        playlist_id = int(playlist_id)
        songs = Song.objects.filter(playlist_id=playlist_id)
        if songs:
            songs_list = []
            for song in songs:
                song_dict = model_to_dict(song)
                songs_list.append(song_dict)
            return JsonResponse({'status':'success','songs':songs_list})
    return JsonResponse({'status':'failure'})

@csrf_exempt
def login_mobile(request):
    # use MobileAppUsers model, generate and store a session id for the user and send it back to the app
    if request.method == 'POST':
        print("in login_mobile")
        body = json.loads(request.body)
        
        email = body['email']
        password = body['password']
        print(email)
        print(password)

        try:
            user = MobileAppUsers.objects.get(email=email)
        except MobileAppUsers.DoesNotExist:
            user = None
        print(user)
        if user and password==user.password:
            # generate a session id for the user
            session_id = uuid.uuid4()
            # store the session id in the database
            user.session_id = session_id
            user.save()
            
            # send back the session id and email to the app
            return JsonResponse({'status':'success','session_id':session_id,'user':model_to_dict(user, exclude=['profile_pic'])})
            
        else:
            print(password)
            # Login failed, display error message on the login form
            return JsonResponse({'status':'failure'})
    else:
        return JsonResponse({'status':'failure'})
    
@csrf_exempt    
def verify_session_web(request):
    # get the session id from the app
    if request.method == 'POST':
        body = json.loads(request.body)
        session_id = body['session_id']
        
        # get the user with this session id
        try:
            user = CustomUser.objects.get(session_id=session_id)
        except CustomUser.DoesNotExist:
            user = None
            
        # check if the user exists
        if user is not None:
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'status':'failure'})
    else:
        return JsonResponse({'status':'failure'})

@csrf_exempt
def signup_mobile(request):
    # name email and password received from the app
    if request.method == 'POST':
        print("in signup_mobile")
        print(request.body)
        body = json.loads(request.body)
        name = body['name']
        email = body['email']
        password = body['password']
        
        # create a new user
        user = MobileAppUsers.objects.create(name=name,email=email,password=password)
        
        #check if the user was created successfully
        if user is None:
            return JsonResponse({'status':'failure'})
        else:
            # save user and send back success message
            user.save()
            return JsonResponse({'status':'success'})
        
    else:
        return JsonResponse({'status':'failure'})
@csrf_exempt    
def logout_mobile(request):
    # get the session id from the app
    if request.method == 'POST':
        body = json.loads(request.body)
        session_id = body['session_id']
        
        # get the user with this session id
        try:
            user = MobileAppUsers.objects.get(session_id=session_id)
        except MobileAppUsers.DoesNotExist:
            user = None
            
        # check if the user exists
        if user is not None:
            # delete the session id
            user.session_id = None
            user.save()
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'status':'failure'})
    else:
        return JsonResponse({'status':'failure'})
@csrf_exempt    
def verify_session_mobile(request):
    # get the session id from the app
    if request.method == 'POST':
        body = json.loads(request.body)
        session_id = body['session_id']
        
        # get the user with this session id
        try:
            user = MobileAppUsers.objects.get(session_id=session_id)
        except MobileAppUsers.DoesNotExist:
            user = None
            
        # check if the user exists
        if user is not None:
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'status':'failure'})
    else:
        return JsonResponse({'status':'failure'})

def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

@csrf_exempt
def add_to_queue_mobile(request):
    if request.method == 'POST':
        print(f"********body: {request.body}")
        body = json.loads(request.body)
        youtube_link = body.get('youtube_link','')
        cafe_id = body.get('cafe_id', '')
        session_id = body.get('session_id', '')
        # Check if the youtube_link is blacklisted
        if cafe_id and youtube_link and session_id:
            cafe_id = int(cafe_id)
            try:
                user = MobileAppUsers.objects.get(session_id=session_id)
            except MobileAppUsers.DoesNotExist:
                user = None
            if user is None:
                print('User not found')
                return JsonResponse({'success': False, 'error': 'session ended'})
            is_blacklisted2 = GlobalBlacklist.objects.filter(song_link=youtube_link).exists()
            
            if is_blacklisted2:
                print('This song is globally blacklisted')
                return JsonResponse({'success': False, 'error': 'This song is globally blacklisted'})
            is_blacklisted = CafeBlacklist.objects.filter(cafe_id=cafe_id,song_link=youtube_link).exists()
            if is_blacklisted:
                print('This song is blacklisted')
                return JsonResponse({'success': False, 'error': 'This song is blacklisted'})
            else:
                cafe = Cafe.objects.get(id=cafe_id)
                next_token = cafe.next_token
                api_key = 'AIzaSyD9hpr10WRoTNtjujmRFpkHawvXFl51JOI'
                youtube = build('youtube', 'v3', developerKey=api_key)
                video_id = youtube_link.split('/')[-1]
                youtube_link = f'https://www.youtube.com/watch?v={video_id}'
                # video_id = re.search(r'(?<=v=)[^&]+', youtube_link).group()
                video_info = youtube.videos().list(part='snippet', id=video_id).execute()
                song_name = video_info['items'][0]['snippet']['title']
                
                queue = Queue.objects.create(song_link=youtube_link,date=timezone.now(),cafe_id=cafe_id,song_name=song_name)
                queue.token_no=next_token
                user.token_no = next_token
                cafe.next_token += 1
                cafe.save()
                queue.save()
                user.save()
                return JsonResponse({'success': True,'token':queue.token_no})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})




@csrf_exempt
def set_user_cafe_mobile(request):
    if request.method == 'POST':
        print(f"********body: {request.body}")
        body = json.loads(request.body)
        email = body.get('email', '')
        cafe_id = body.get('cafe_id','')
        session_id = body.get('session_id', '')
        try:
            if email and cafe_id and session_id:
                try:
                    user = MobileAppUsers.objects.get(email=email)
                except MobileAppUsers.DoesNotExist:
                    user = None
                if user:
                    if user.session_id == session_id:
                        try:
                            cafe = Cafe.objects.get(id = cafe_id)
                        except Cafe.DoesNotExist:
                            cafe = None
                        if cafe:
                            user.cafe = cafe
                            user.save()
                            print(model_to_dict(user))
                            return JsonResponse({'status':'success', 'body': 'user added to cafe'})
                        else:
                            return JsonResponse({'status':'failuire', 'body': 'cafe not found'})
                    else:
                        return JsonResponse({'status':'failuire', 'body': 'user session expired'})
                else:
                    return JsonResponse({'status':'failuire', 'body': 'user not found'})
            else:
                return JsonResponse({'status':'invalid request'})
        except Exception as e:
            print("exception in set_user_cafe_mobile")
            print(e)
            return JsonResponse({'status':'error in api'})


@csrf_exempt
def get_current_playing_song(request):
    if request.method == 'POST':
        print(f"********body: {request.body}")
        body = json.loads(request.body)
        email = body.get('email', '')
        cafe_id = body.get('cafe_id','')
        session_id = body.get('session_id', '')
        try:
            if email and cafe_id and session_id:
                cafe_id = int(cafe_id)
                try:
                    user = MobileAppUsers.objects.get(email=email)
                except MobileAppUsers.DoesNotExist:
                    user = None
                if user:
                    print("*****************")
                    # print(model_to_dict( user))
                    # print(f"usercafeid: {user.cafe.id}")
                    if user.session_id == session_id:
                        try:
                            user_cafe_id = Cafe.objects.get(id = user.cafe.id)
                        except Cafe.DoesNotExist:
                            user_cafe_id = None
                        if user_cafe_id:
                            
                            if user_cafe_id.id == cafe_id:
                                curr_token_no = user_cafe_id.current_token

                                song_name = Queue.objects.filter(cafe_id = cafe_id,  token_no = curr_token_no)
                                if song_name:
                                    song_name = song_name[0].song_name
                                    # print(curr_token_no,song_name)
                                    return JsonResponse({'status':'success', 'body':{'curr_token': curr_token_no, 'song_name': song_name}})
                                else:

                                    return JsonResponse({'status':'failuire', 'body':'no song found'})    
                            else:
                                return JsonResponse({'status':'failuire', 'body':'user not in this cafe'})    
                        else:
                            return JsonResponse({'status':'failuire', 'body':' cafe not found'})
                    else:
                        return JsonResponse({'status':'failuire', 'body': 'user session expired'})    
                else:
                    return JsonResponse({'status':'failuire', 'body': 'user not found'})
            else:
                return JsonResponse({'status':'invalid request'})
        except Exception as e:
            print("exception in get_current_playing_song")
            print(e)
            return JsonResponse({'status':'error in api'})


@csrf_exempt
def get_user_token(request):
    if request.method == 'POST':
        print(f"********body: {request.body}")
        body = json.loads(request.body)
        email = body.get('email', '')
        cafe_id = body.get('cafe_id','')
        session_id = body.get('session_id', '')
        try:
            if email and cafe_id and session_id:
                cafe_id = int(cafe_id)
                try:
                    user = MobileAppUsers.objects.get(email=email)
                except MobileAppUsers.DoesNotExist:
                    user = None
                if user:
                    print("*****************")
                    # print(model_to_dict( user))
                    # print(f"usercafeid: {user.cafe.id}")
                    if user.session_id == session_id:
                        try:
                            user_cafe_id = Cafe.objects.get(id = user.cafe.id)
                        except Cafe.DoesNotExist:
                            user_cafe_id = None
                        if user_cafe_id:
                            print(user.token_no)
                            if user_cafe_id.id == cafe_id:
                                toknnum = user.token_no   
                                
                                if toknnum>=0:
                                    return JsonResponse({'status':'success', 'body': {'token_num': toknnum}})    
                                else:
                                    return JsonResponse({'status':'failuire', 'body': '-'})
                            else:
                                return JsonResponse({'status':'failuire', 'body':'user not in this cafe'})    
                        else:
                            return JsonResponse({'status':'failuire', 'body':' cafe not found'})
                    else:
                        return JsonResponse({'status':'failuire', 'body': 'user session expired'})    
                else:
                    return JsonResponse({'status':'failuire', 'body': 'user not found'})
            else:
                return JsonResponse({'status':'invalid request'})
        except Exception as e:
            print("exception in get_user_token")
            print(e)
            return JsonResponse({'status':'error in api'})

