#!/usr/bin/env python
"""
This code can be run with command python get_client_access_token.py "client_id" "client_secret".
Running this code will pop up strava webpabe and will ask you to authorize access.
For purposes of using the migration tool, you have to click authorize.
After that, a code will appear on the webpage. Save this code in clipboard and use it in
runtastic_to_strava_migration_tool.
"""
import stravalib
import subprocess
import sys
from flask import Flask, request

app = Flask(__name__)

API_CLIENT = stravalib.Client()

@app.route("/auth")
def auth_callback():
    code = request.args.get('code')
    access_token = API_CLIENT.exchange_code_for_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=code
        )
    return access_token['access_token']


if __name__ == '__main__':
    CLIENT_ID, CLIENT_SECRET = int(sys.argv[1]), sys.argv[2]
    auth_url = API_CLIENT.authorization_url(
        client_id=int(sys.argv[1]),
        redirect_uri='http://127.0.0.1:5000/auth'.format(),
        scope=['activity:write','activity:read_all','profile:read_all','profile:write','read_all'],
        state='from_cli'
        )
    if sys.platform == 'darwin':
        print('On OS X - launching {0} at default browser'.format(auth_url))
        subprocess.call(['open', auth_url])
    else:
        print('Go to {0} to authorize access: '.format(auth_url))
    app.run()