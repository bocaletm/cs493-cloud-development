import datetime
import os
import json
from flask import Flask, Response, request, jsonify, make_response
from google.cloud import datastore
from google.auth.transport import requests
import google.oauth2.id_token


datastore_client = datastore.Client()

def errorResponse(status,msg):
    return Response(json.dumps({'Error': msg}, sort_keys=True, indent=4),status, mimetype='application/json')

def contentResponse(status,content):
    return Response(json.dumps(content, sort_keys=True, indent=4),status=status, mimetype='application/json')

def store_boat(name, boatType, length):
    kind = 'Boat'
    boat_key = datastore_client.key(kind)
    boat = datastore.Entity(key=boat_key)
    boat.update({
        "name": name, 
        "type": boatType, 
        "length": length
    })
    try: 
        datastore_client.put(boat)
    except: 
        print('Failed to save Boat: ' + name)
        return -1
    return boat.key.id_or_name

def get_boats(baseUri):
    query = datastore_client.query(kind='Boat')
    boats = None
    try: 
        boats = list(query.fetch())
    except:
        print('Failed to fetch Boats')
    for boat in boats:
        id = boat.key.id_or_name
        selfUri = baseUri + str(id)
        boat.update({"id":boat.key.id_or_name})
        boat.update({"self":selfUri})
    return boats

def get_boat(boat_id, baseUri):
    query = datastore_client.query(kind='Boat')
    boat_key = datastore_client.key('Boat', int(boat_id))
    query.key_filter(boat_key)
    boats = query.fetch()
    for boat in boats:
        id = boat.key.id_or_name
        selfUri = baseUri + str(id)
        boat.update({"id":id})
        boat.update({"self":selfUri})
        return boat

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
    content = request.json
    if content.get('name',None) == None or content.get('type',None) == None or content.get('length',None) == None:
        return errorResponse(400,'The request object is missing at least one of the required attributes')
    id = store_boat(content['name'],content['type'],content['length']) 
    if id is not -1:
        status = 201 
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        selfUri = request.base_url + '/boats/' + str(id)
        content.update({"self": selfUri })
        return contentResponse(status,content)
    else:
        return errorResponse(405,'Unknown')

@app.route('/boats', methods =['GET']) 
def getBoats():
    boats = get_boats(request.base_url)
    status = 200 if boats is not None else 405 
    print(boats)
    return make_response(jsonify(boats), status)

@app.route('/boats/<string:boat_id>', methods =['GET']) 
def getBoat(boat_id):
    boat = None
    boat = get_boat(boat_id, request.base_url) 
    if boat is not None:
        print(boat)
        return make_response(jsonify(boat), 200)
    else: 
        return errorResponse(404,'No boat with this boat_id exists')

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