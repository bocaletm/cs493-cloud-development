import google.cloud.logging
import logging
import requests
import secrets
from os import environ
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, redirect, session, url_for
from helpers import Validation, Constants, Authorization

client = google.cloud.logging.Client()
client.setup_logging()

C = Constants()
V = Validation()
Auth = Authorization()

app = Flask(__name__)

V.checkEnvironment()

app.secret_key = environ.get('FLASK_SECRET_KEY')

Bootstrap(app)

@app.route('/user')
def user():
    sessionKey = session.get('name','none') + session.get('time','none')
    if session.get('name','') and session.get('token','session') == Auth.VERIFY_SESSION.get(sessionKey,'saved'):
        return render_template('userinfo.html',name=session.get('name'),state=session.get('state',''))
    elif session.get('name',''): 
        return render_template('userinfo.html',trick='You\'re trying to trick me. Shame on you!')
    else:
        return redirect(url_for('root',error='No name found for user'))

@app.route('/auth')
def auth():
    if request.args.get('code', '') and request.args.get('state', '') and session.get('state','') and request.args.get('state') == session.get('state'): 
        logging.info(C.receivedCode)
        token = Auth.getToken(request.args.get('code', ''))

        res = requests.get(
            C.namesEmailsUrl,
            headers=dict(
                Authorization='Bearer ' + token
            )
        )
        names = res.json()['names'][0]
        name = names.get('displayName')
        Auth.saveSession(name)
        return redirect(url_for('user'))
    elif request.args.get('error', ''):
        error = request.args.get('error', '')
        logging.info(error)
        return redirect(url_for('root',error=error))
    else:
        logging.info(C.settingState)
        session['state'] = secrets.token_urlsafe(16)
        return redirect(C.googleAuthUrl + '&redirect_uri=' + request.base_url + '&state=' + session['state'])

@app.route('/')
def root():
    return render_template('index.html',error=request.args.get('error',''))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)