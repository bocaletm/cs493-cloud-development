import datetime
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

clientID = os.environ.get("CLIENT_ID")
clientSecret = os.environ.get("CLIENT_SECRET")

@app.route('/user')
def auth():
    return render_template('userinfo.html', user_data='none', error_message='')

@app.route('/')
def root():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)