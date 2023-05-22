from django.contrib import messages
from django.forms import model_to_dict
from app.models import CustomUser,Address,Cafe,Playlist,Song,Queue,CafeBlacklist,GlobalBlacklist
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

def logout_view(request):
    cafe_id = request.session.get('cafe_id')
    if cafe_id:
        try:
            user = CustomUser.objects.get(cafe_id=cafe_id)
            user.is_login = False
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


def get_songs(request):
    cafe_id = request.session.get('cafe_id')
    queue = Queue.objects.filter(cafe_id=cafe_id, is_played=False)
    newsongs = [(q.song_link, q.song_name, q.is_played) for q in queue]
    data = {'newsongs': newsongs}
    return JsonResponse(data, encoder=CustomJsonEncoder)

@csrf_exempt
def update_queue(request):
    if request.method == 'POST':
        queue_id = request.POST.get('queue_id')
        print('The first queue ID is:', queue_id)
        try:
            queue = Queue.objects.get(id=queue_id)
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
                api_key = 'AIzaSyCNtdk5YQKiONdmp1E3HZNZsmrAs1xBY5o'
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
            api_key = 'AIzaSyCNtdk5YQKiONdmp1E3HZNZsmrAs1xBY5o'
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
            api_key = 'AIzaSyCNtdk5YQKiONdmp1E3HZNZsmrAs1xBY5o'
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
            api_key = 'AIzaSyCNtdk5YQKiONdmp1E3HZNZsmrAs1xBY5o'
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
        user = CustomUser.objects.create(email=email, contact=contact, password=password, cafe=cafe)

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
        api_key = 'AIzaSyCNtdk5YQKiONdmp1E3HZNZsmrAs1xBY5o'
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
            user.is_login=True
            user.save()
            if user.is_admin==False:
                return redirect('homemanager')
            else:
                return redirect('homeadmin')
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