import logging
from flask import request, session
from os import environ
import time
import secrets
import requests

class Constants:
    #logging
    stateErr = 'Could not verify auth server response'
    keyErr = 'Unable to read key from environment variables'
    clientIdErr = 'Unable to read client id from environment variables'
    clientSecretErr = 'Unable to read client secret from environment variables'
    receivedCode = 'Valid request contains code. Obtaining token'
    settingState = 'Initiating Auth with Google and saving state'

    #functional
    clientID = environ.get('GCLOUD_CLIENT_ID')
    clientSecret = environ.get('GCLOUD_CLIENT_SECRET')
    scopes = 'https://www.googleapis.com/auth/userinfo.profile'
    authBaseUrl = 'https://accounts.google.com/o/oauth2/v2/auth'
    tokenBaseUrl = 'https://oauth2.googleapis.com/token'
    googleAuthUrl = authBaseUrl + '?' + 'client_id=' + clientID + '&response_type=code' + '&scope=' + scopes
    tokenUrl = tokenBaseUrl + '?' + 'client_id=' + clientID + '&client_secret=' + clientSecret + '&grant_type=authorization_code'
    namesEmailsUrl = 'https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses' 

class Validation:
    def shutDown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        func()

    def checkEnvironment(self):
        if not environ.get('FLASK_SECRET_KEY',''):
            logging.error(Constants.keyErr)
            self.shutDown()
        if not environ.get('GCLOUD_CLIENT_ID',''):
            logging.error(Constants.clientIdErr)
            self.shutDown()
        if not environ.get('GCLOUD_CLIENT_SECRET',''):
            logging.error(Constants.clientSecretErr)
            self.shutDown()

class Authorization:
    VERIFY_SESSION = dict()

    def saveSession(self,name):
        token = secrets.token_urlsafe(16)
        epoch_time = str(int(time.time()))
        session['name'] = name
        session['token'] = token
        session['time'] = epoch_time
        self.VERIFY_SESSION[name + epoch_time] = token

    def getToken(self,code):
        tokenUrlWithCode = Constants.tokenUrl + '&redirect_uri=' + request.base_url + '&code=' + code
        res = requests.post(tokenUrlWithCode)
        content = res.json()
        return content['access_token']