import datetime
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import datastore
from google.auth.transport import requests
import google.oauth2.id_token


datastore_client = datastore.Client()

def store_todo(title,checked,email):
    entity = datastore.Entity(key=datastore_client.key('User',email,'todo'))
    entity.update({
        'checked': checked,
        'title': title
    })
    datastore_client.put(entity)

def delete_todo(title,email):
    query = datastore_client.query(kind='todo')
    query.add_filter('title', '=', title)
    results = list(query.fetch())
    for result in results:
        print(result.key)
        datastore_client.delete(result.key)

def fetch_todos(email):
    ancestor = datastore_client.key('User', email)
    query = datastore_client.query(kind='todo', ancestor=ancestor)
    todos =  query.fetch()
    print('fetched todos:')
    print(todos)
    return todos

def store_time(email,dt):
    entity = datastore.Entity(key=datastore_client.key('User',email,'visit'))
    entity.update({
        'timestamp': dt
    })
    datastore_client.put(entity)


def fetch_times(email,limit):
    ancestor = datastore_client.key('User', email)
    query = datastore_client.query(kind='visit', ancestor=ancestor)
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times

app = Flask(__name__)

firebase_request_adapter = requests.Request()

@app.route('/addtodo', methods =['POST']) 
def addtodo(): 
            # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. 
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            store_todo(request.form['todo'],False,claims['email']) 
        except ValueError as exc:
            # This will be raised if the token is expired or any other
            error_message = str(exc)
    return redirect(url_for('root'))

@app.route('/deletetodo', methods =['POST']) 
def deletetodo(): 
                # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. 
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            delete_todo(request.form['todo'],claims['email']) 
        except ValueError as exc:
            # This will be raised if the token is expired or any other
            error_message = str(exc)
    return redirect(url_for('root'))

@app.route('/toggletodo', methods =['GET']) 
def toggletodo(): 
    title = request.args.get('title')
    checked = False
    if request.args.get('checked') == 'True':
        checked = False
    else:
        checked = True
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. 
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            delete_todo(title,claims['email']) 
            store_todo(title,checked,claims['email']) 
        except ValueError as exc:
            # This will be raised if the token is expired or any other
            error_message = str(exc)
    return redirect(url_for('root'))

@app.route('/')
def root():
        # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    todos = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. 
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            store_time(claims['email'], datetime.datetime.now())
            times = fetch_times(claims['email'], 1)
            todos = fetch_todos(claims['email'])
        except ValueError as exc:
            # This will be raised if the token is expired or any other
            error_message = str(exc)

    return render_template('index.html', user_data=claims, error_message=error_message, times=times, todos=todos)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)