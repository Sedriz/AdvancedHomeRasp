import base64
import datetime
from urllib.parse import urlencode

import requests


class SpotifyAPI:
    __client_id: str = None
    __client_secret: str = None

    __access_token: str = None
    __access_token_expires: datetime = datetime.datetime.now()
    __access_token_did_expire: bool = True
    __refresh_token: str = None

    __auth_token: str = None
    __user_code: str = None

    def __init__(self, client_id: str, client_secret: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client_id = client_id
        self.__client_secret = client_secret

    def __get_token_header(self):
        client_creds = f'{self.__client_id}:{self.__client_secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return {
            'Authorization': f'Basic {client_creds_b64.decode()}'
        }

    def __perform_auth(self) -> bool:
        redirect_uri = 'http://localhost:8080/'

        token_url = 'https://accounts.spotify.com/api/token'
        token_data = {
            'grant_type': 'authorization_code',
            'code': self.__user_code,
            'redirect_uri': redirect_uri
        }

        r = requests.post(token_url, data=token_data, headers=self.__get_token_header())
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client!")

        token_response_data = r.json()
        now = datetime.datetime.now()
        access_token = token_response_data['access_token']
        refresh_token = token_response_data['refresh_token']
        expires_in = token_response_data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.__access_token = access_token
        self.__access_token_expires = expires
        self.__access_token_did_expire = expires < now
        self.__refresh_token = refresh_token
        return True

    def refresh_token(self):
        token_url = 'https://accounts.spotify.com/api/token'
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.__refresh_token,
        }

        r = requests.post(token_url, data=token_data, headers=self.__get_token_header())
        if r.status_code not in range(200, 299):
            raise Exception("Could not refresh client token!")

        token_response_data = r.json()
        now = datetime.datetime.now()
        access_token = token_response_data['access_token']
        expires_in = token_response_data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.__access_token = access_token
        self.__access_token_expires = expires
        self.__access_token_did_expire = expires < now
        return True

    def request_authorization(self):
        endpoint = "https://accounts.spotify.com/authorize/"
        scope = 'user-read-currently-playing ' \
                'user-read-recently-played ' \
                'user-read-playback-state ' \
                'user-read-playback-position'
        redirect_uri = 'http://localhost:8080/'

        request_dict = {
            'client_id': self.__client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'show_dialog': True,
            'scope': scope,
        }
        rq_query = urlencode(request_dict)
        return f'{endpoint}?{rq_query}'

    def __get_access_token(self):
        auth_done = self.__perform_auth()
        if not auth_done:
            return Exception("Authentication failed")
        token = self.__access_token
        expires = self.__access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.__perform_auth()
            return self.__get_access_token()
        elif token is None:
            self.__perform_auth()
            return self.__get_access_token()
        return token

    def get_current_track(self) -> str:
        endpoint = "https://api.spotify.com/v1/me/player/currently-playing"
        headers = {
            "Authorization": f"Bearer {self.__get_access_token() }"
        }
        r = requests.get(endpoint, headers=headers)

        if r.status_code not in range(200, 299):
            raise Exception("Could not get current playing track!")

        if r.status_code == 204:
            return ''

        return r.json()

    def search(self, query: str, search_type: str):
        endpoint = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {self.__get_access_token()}"
        }
        data = urlencode({
            'q': query,
            'type': search_type
        })
        lookup_url = f'{endpoint}?{data}'
        response = requests.get(lookup_url, headers=headers)

        if response.status_code not in range(200, 299):
            return {}
        return response.json()

    def search_track(self, track_name: str):
        return self.search(track_name, 'track')

    def set_code(self, code):
            self.__user_code = code
