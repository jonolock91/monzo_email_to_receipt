import webbrowser
import uuid
import os
import time
from datetime import datetime, timedelta
import requests

class MonzoAuth():

    def __init__(self):

        self.account_id = r'acc_xxxxx'
        self.client_id = r'oauth2client_xxxxx'
        self.client_secret = r'xxxxx'
        self.redirect_uri = 'http://127.0.0.1:21234/'
        self.state = uuid.uuid4().hex
        self.access_token = None

    def get_access(self):

        # Remove access token file if over 12 hours old as it will expire
        try:
            access_created = time.ctime(os.path.getctime('access_token.txt'))
            access_created_date = datetime.strptime(
                access_created,
                '%a %b %d %H:%M:%S %Y'
            )

            if access_created_date < (datetime.now() - timedelta(hours=12)):
                os.remove('access_token.txt')
        except:
            pass

        # Check if Monzo access token already exists
        try:
            with open('access_token.txt', 'r') as f:
                self.access_token = f.read()
                return
        except:
            pass

        webbrowser.open_new_tab(
            'https://auth.monzo.com/?client_id={0}&redirect_uri={1}&response_type=code&state={2}'.format(
                self.client_id,
                self.redirect_uri,
                self.state
            )
        )

        # Wait for user to enter response in terminal...
        response_url = input('Paste in the URL Monzo email redirects to...')
        response_url = response_url.replace('http://127.0.0.1:21234/?', '')

        params = response_url.split('&')
        response_values = {}
        for param in params:
            query_str, value = param.split('=')
            response_values[query_str] = value

        # State must come back the same, else it's not safe
        if response_values['state'] != self.state:
            raise Exception('State not the same, abort!')

        r = requests.post('https://api.monzo.com/oauth2/token', data={
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': response_values['code']
        })

        r_json = r.json()

        self.access_token = r_json['access_token']
        self.refresh_token = r_json['refresh_token']

        # Store token for future use
        with open('access_token.txt', 'w') as f:
            f.write(self.access_token)
