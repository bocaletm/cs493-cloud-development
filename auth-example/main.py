import time
import requests
import secrets
from os import environ
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = environ.get('FLASK_SECRET_KEY')

Bootstrap(app)

stateError = 'Could not verify auth server response'
clientID = environ.get('GCLOUD_CLIENT_ID')
clientSecret = environ.get('GCLOUD_CLIENT_SECRET')
scopes = 'https://www.googleapis.com/auth/userinfo.profile'
authBaseUrl = 'https://accounts.google.com/o/oauth2/v2/auth'
tokenBaseUrl = 'https://oauth2.googleapis.com/token'
googleAuthUrl = authBaseUrl + '?' + 'client_id=' + clientID + '&response_type=code' + '&scope=' + scopes
tokenUrl = tokenBaseUrl + '?' + 'client_id=' + clientID + '&client_secret=' + clientSecret + '&grant_type=authorization_code'
    
namesEmailsUrl = 'https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses'

VERIFY_SESSION = dict()

def saveSession(name):
    token = secrets.token_urlsafe(16)
    epoch_time = str(int(time.time()))
    session['name'] = name
    session['token'] = token
    session['time'] = epoch_time
    VERIFY_SESSION[name + epoch_time] = token

def getToken(code):
    tokenUrlWithCode = tokenUrl + '&redirect_uri=' + request.base_url + '&code=' + code
    res = requests.post(tokenUrlWithCode)
    content = res.json()
    return content['access_token']

@app.route('/user')
def user():
    sessionKey = session.get('name','none') + session.get('time','none')
    if session.get('name','') and session.get('token','session') == VERIFY_SESSION.get(sessionKey,'saved'):
        return render_template('userinfo.html',name=session.get('name'),state=session.get('state',''))
    elif session.get('name',''): 
        return render_template('userinfo.html',trick='You\'re trying to trick me. Shame on you!')
    else:
        return redirect(url_for('root',error='No name found for user'))

@app.route('/auth')
def auth():
    if request.args.get('code', '') and request.args.get('state', '') and session.get('state','') and request.args.get('state') == session.get('state'): 
        token = getToken(request.args.get('code', ''))

        res = requests.get(
            namesEmailsUrl,
            headers=dict(
                Authorization='Bearer ' + token
            )
        )
        names = res.json()['names'][0]
        name = names.get('displayName')
        saveSession(name)
        return redirect(url_for('user'))
    elif request.args.get('error', ''):
        error = request.args.get('error', '')
        return redirect(url_for('root',error=error))
    else:
        print('setting state ' + session['state'])
        session['state'] = secrets.token_urlsafe(16)
        return redirect(googleAuthUrl + '&redirect_uri=' + request.base_url + '&state=' + session['state'])

@app.route('/')
def root():
    return render_template('index.html',error=request.args.get('error',''))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)