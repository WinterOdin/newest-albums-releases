import requests
import datetime
import json
import base64
from urllib.parse import urlencode
client_id = 'f00af83a96874760a3b8a3ebafabb29a'
client_secret = '5abcde8d5d154a4ca6c469fe622b96f5'
class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
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
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in'] # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

spotify = SpotifyAPI(client_id, client_secret)

spotify.perform_auth()

access_token = spotify.access_token

headers = {
    "Authorization": f"Bearer {access_token}"
}
endpoint = "https://api.spotify.com/v1/browse/new-releases"
lookup_url = f"{endpoint}"

r = requests.get(lookup_url, headers=headers)
a = r.json()

artist_name = []
artist_url  = []
album_url   = []
album_pic   = []
album_name  = []
for x in range(0,20):#20 because it's Default limit in query it's 20 you can change it up to 50 in the endpoint
    artist_name.append(a["albums"]["items"][x]["artists"][0]['name'])
    artist_url.append(a["albums"]["items"][x]["artists"][0]['external_urls']['spotify'])
    album_url.append(a["albums"]["items"][x]["external_urls"]['spotify'])
    album_pic.append(a["albums"]["items"][x]["images"][0]['url'])
    album_name.append(a["albums"]["items"][x]["name"])

print(album_pic)