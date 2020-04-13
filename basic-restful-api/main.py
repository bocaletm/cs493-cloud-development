import datetime
import os
from flask import Flask, Response, request, redirect, url_for
from google.cloud import datastore
from google.auth.transport import requests
import google.oauth2.id_token


datastore_client = datastore.Client()

#keyFromEnv = os.environ.get("FIREBASE_API_KEY")

def get_boats():
    return 200

def store_boat():
    return 201

def get_boat(boat_id):
    return 202

def update_boat(boat_id):
    return 200

def delete_boat(boat_id):
    return 200

def get_slips():
    return 200

def store_slip():
    return 201

def get_slip(slip_id):
    return 200

def delete_slip(slip_id):
    return 200

def dock_boat(slip_id, boat_id):
    return 200

def release_boat(slip_id, boat_id):
    return 200

app = Flask(__name__)

@app.route('/boats', methods =['POST']) 
def postBoat():
    status = store_boat() 
    return Response(status=status)

@app.route('/boats', methods =['GET']) 
def getBoats():
    status = get_boats() 
    return Response(status=status, mimetype='application/json')

@app.route('/boats/<string:boat_id>', methods =['GET']) 
def getBoat(boat_id):
    status = get_boat(boat_id) 
    return Response(status=status, mimetype='application/json')

@app.route('/boats/<string:boat_id>', methods =['PATCH']) 
def updateBoat(boat_id):
    status = update_boat(boat_id) 
    return Response(status=status, mimetype='application/json')

@app.route('/boats/<string:boat_id>', methods =['DELETE']) 
def deleteBoat(boat_id):
    status = delete_boat(boat_id) 
    return Response(status=status, mimetype='application/json')

@app.route('/slips', methods =['POST']) 
def postSlip():
    status = store_slip() 
    return Response(status=status)

@app.route('/slips', methods =['GET']) 
def getSlips():
    status = get_slips() 
    return Response(status=status, mimetype='application/json')

@app.route('/slips/<string:slip_id>', methods =['GET']) 
def getSlip(slip_id):
    status = get_slip(slip_id) 
    return Response(status=status, mimetype='application/json')

@app.route('/slips/<string:slip_id>', methods =['DELETE']) 
def deleteSlip(slip_id):
    status = delete_slip(slip_id) 
    return Response(status=status, mimetype='application/json')

@app.route('/slips/<string:slip_id>/<string:boat_id>', methods =['PUT']) 
def dockBoat(slip_id,boat_id):
    status = dock_boat(slip_id,boat_id) 
    return Response(status=status, mimetype='application/json')

@app.route('/slips/<string:slip_id>/<string:boat_id>', methods =['PATCH']) 
def releaseBoat(slip_id,boat_id):
    status = release_boat(slip_id,boat_id) 
    return Response(status=status, mimetype='application/json')

@app.route('/')
def root():
    return Response("{'documentation_uri':'https://canvas.oregonstate.edu/courses/1764544/files/79296197/download'}\n", status=200, mimetype='application/json')
    

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)