from flask import Blueprint, request, render_template
from os import environ
from google.cloud import datastore
import google.oauth2.id_token
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from constants import Constants as C
from user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
datastore_client = datastore.Client()

client_id = environ.get("CLIENT_ID")
print(client_id)
client_secret = environ.get("CLIENT_SECRET")

redirect_uri = environ.get("OAUTH_REDIRECT")

scope = C.AUTH_SCOPES
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,scope=scope)

user = User()

@bp.route('', strict_slashes=False)
def authRoute():
    try:
        authorization_url, state = oauth.authorization_url('https://accounts.google.com/o/oauth2/auth',
            access_type="offline", prompt="select_account")
        if authorization_url == '': raise Exception
    except:
        error = 'Unable to obtain authentication url'
        return render_template('index.html',error=error)
    return render_template('index.html',url=authorization_url)

@bp.route('/oauth')
def oauthRoute():
    try: 
        token = oauth.fetch_token('https://accounts.google.com/o/oauth2/token',
            authorization_response=request.url,
            client_secret=client_secret)
        req = requests.Request()

        id_info = id_token.verify_oauth2_token(token['id_token'], req, client_id)
        email = id_info['email']
        user_id = ['sub']
        jwt = token['id_token']
        if user.conditionalCreate(user_id) == -1:
            raise Exception('User creation error')
    except Exception as err:
        return render_template('index.html',error=err)
    return render_template('index.html',email=email,jwt=jwt)
