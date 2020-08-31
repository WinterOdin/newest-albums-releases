from django.shortcuts import render
import requests
import datetime
import json
import base64
from urllib.parse import urlencode
from itertools import islice 
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count, Sum, Max
from json import dumps 

client_id       = 'f00af83a96874760a3b8a3ebafabb29a'
client_secret   = '5abcde8d5d154a4ca6c469fe622b96f5'
class SpotifyAPI(object):
    access_token            = None
    access_token_expires    = datetime.datetime.now()
    access_token_did_expire = True
    client_id               = None
    client_secret           = None
    token_url               = "https://accounts.spotify.com/api/token"
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id       = client_id
        self.client_secret   = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id           = self.client_id
        client_secret       = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds        = f"{client_id}:{client_secret}"
        client_creds_b64    = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        } 
    
    def perform_auth(self):
        token_url                       = self.token_url
        token_data                      = self.get_token_data()
        token_headers                   = self.get_token_headers()
        r                               = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            return False
        data                            = r.json()
        now                             = datetime.datetime.now()
        access_token                    = data['access_token']
        expires_in                      = data['expires_in'] # seconds
        expires                         = now + datetime.timedelta(seconds=expires_in)
        self.access_token               = access_token
        self.access_token_expires       = expires
        self.access_token_did_expire    = expires < now
        return True




def mainView(request):
    spotify = SpotifyAPI(client_id, client_secret)
    spotify.perform_auth()
    access_token = spotify.access_token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    endpoint = "https://api.spotify.com/v1/browse/new-releases?&limit=21"
    lookup_url = f"{endpoint}"
    r = requests.get(lookup_url, headers=headers)
    a = r.json()

    artist_name       = []
    artist_url        = []
    album_url         = []
    album_pic         = []
    album_name        = []
    album_id          = []
    albums_list       = []
    album_track_total = []
    song_list         = []  
    track_numbers     = [] # list of length in which we have to split

    for x in range(0,21):#21 because it's Default limit in query it's 21 you can change it up to 50 in the endpoint
        album_id.       append(a["albums"]["items"][x]['id'])
        album_name.     append(a["albums"]["items"][x]["name"])
        album_pic.      append(a["albums"]["items"][x]["images"][1]['url'])
        artist_name.    append(a["albums"]["items"][x]["artists"][0]['name'])
        album_url.      append(a["albums"]["items"][x]["external_urls"]['spotify'])
        artist_url.     append(a["albums"]["items"][x]["artists"][0]['external_urls']['spotify'])
        
        
        
        


    for x in album_id :
        album_query = "https://api.spotify.com/v1/albums/"+x+ "/tracks"
        lookup_album_url     = f"{album_query}"
        album_tracks_request = requests.get(lookup_album_url, headers=headers)
        albums_list.append(album_tracks_request.json())


    for x in albums_list:
        for y  in  range(len(x['items'])):
            song_list.append(x['items'][y]["name"])
        track_numbers.append(x['total'])


    song_list_input = iter(song_list) 
    grouped_tracks  = [list(islice(song_list_input, x)) for x in track_numbers] 
    wholeData       = list(zip(album_pic,album_url,album_name,artist_name,artist_url,grouped_tracks))

    context={
        'wholeData'        : wholeData 
    }
    return render(request,'index.html',context)
    
