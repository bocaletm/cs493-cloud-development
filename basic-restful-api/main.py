import datetime
import os
import json
from flask import Flask, Response, request, jsonify, make_response
from google.cloud import datastore
from google.auth.transport import requests
import google.oauth2.id_token


datastore_client = datastore.Client()

NO_ID = 'No boat with this boat_id exists'
NO_ID_SLIP = 'No slip with this slip_id exists'
NO_SLIP_OR_BOAT = 'The specified boat and/or slip don’t exist'
SLIP_OCCUPIED = 'The slip is not empty'
ALREADY_DOCKED = 'Boat already docked at Slip '
DOCKING_NOT_FOUND = 'No boat with this boat_id is at the slip with this slip_id'
INCOMPLETE = 'The request object is missing at least one of the required attributes'
INCOMPLETE_SLIP = 'The request object is missing the required number'
DOCUMENTATION = 'https://canvas.oregonstate.edu/courses/1764544/files/79296197/download'

def badInt(s):
    try: 
        int(s)
        return False
    except ValueError:
        return True

def errorResponse(status,msg):
    return Response(json.dumps({'Error': msg}, sort_keys=True, indent=4),status, mimetype='application/json')

def codeResponse(status):
    return Response(status=status,mimetype='application/json')

def contentResponse(status,content):
    return Response(json.dumps(content, sort_keys=True, indent=4),status=status, mimetype='application/json')

def boat_is_docked(boat_id):
    query = datastore_client.query(kind='Slip')
    query.add_filter('current_boat', '=', int(boat_id))
    query.keys_only()
    slips = query.fetch()
    for slip in slips:
        return slip.key.id_or_name
    return None

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
        selfUri = baseUri + '/' + str(id)
        boat.update({"id":boat.key.id_or_name})
        boat.update({"self":selfUri})
    return boats

def get_boat(boat_id, baseUri):
    if badInt(boat_id): return None
    query = datastore_client.query(kind='Boat')
    boat_key = datastore_client.key('Boat', int(boat_id))
    query.key_filter(boat_key)
    boats = query.fetch()
    for boat in boats:
        id = boat.key.id_or_name
        boat.update({"id":id})
        boat.update({"self":baseUri})
        return boat

def update_boat(baseUri, boat_id, name, boatType, length):
    if badInt(boat_id): return None
    query = datastore_client.query(kind='Boat')
    boat_key = datastore_client.key('Boat', int(boat_id))
    query.key_filter(boat_key)
    boats = query.fetch()
    for boat in boats:
        id = boat.key.id_or_name
        boat.update({
            "name": name, 
            "type": boatType, 
            "length": length,
        })
        datastore_client.put(boat)
        boat.update({
            "id": id,
            "self": baseUri
        })        
        return boat    

def delete_boat(boat_id):
    if badInt(boat_id): return 404
    slip_id = boat_is_docked(boat_id)
    if slip_id is not None: print(release_boat(slip_id,boat_id))
    boat_key = datastore_client.key('Boat', int(boat_id))
    if datastore_client.get(boat_key) is not None:
        datastore_client.delete(boat_key)
        return 204
    else:
        return 404

def store_slip(number):
    kind = 'Slip'
    slip_key = datastore_client.key(kind)
    slip = datastore.Entity(key=slip_key)
    slip.update({
        "number": number, 
        "current_boat": None
    })
    try: 
        datastore_client.put(slip)
    except: 
        print('Failed to save Slip: ' + slip_key)
        return -1
    return slip.key.id_or_name

def get_slips(baseUri):
    query = datastore_client.query(kind='Slip')
    slips = None
    try: 
        slips = list(query.fetch())
    except:
        print('Failed to fetch Slips')
    for slip in slips:
        id = slip.key.id_or_name
        selfUri = baseUri + '/' + str(id)
        slip.update({"id":slip.key.id_or_name})
        slip.update({"self":selfUri})
    return slips

def get_slip(slip_id, baseUri):
    if badInt(slip_id): return None
    query = datastore_client.query(kind='Slip')
    slip_key = datastore_client.key('Slip', int(slip_id))
    query.key_filter(slip_key)
    slips = query.fetch()
    for slip in slips:
        id = slip.key.id_or_name
        slip.update({"id":id})
        slip.update({"self":baseUri})
        return slip

def delete_slip(slip_id):
    if badInt(slip_id): return 404
    slip_key = datastore_client.key('Slip', int(slip_id))
    if datastore_client.get(slip_key) is not None:
        datastore_client.delete(slip_key)
        return 204
    else:
        return 404

def dock_boat(slip_id, boat_id):
    if badInt(slip_id) or badInt(boat_id): return errorResponse(404, NO_SLIP_OR_BOAT)
    dockedSlip = boat_is_docked(boat_id)
    if dockedSlip != None:
        return errorResponse(403, SLIP_OCCUPIED)
    boat_key = datastore_client.key('Boat', int(boat_id))
    slip_key = datastore_client.key('Slip', int(slip_id))
    if datastore_client.get(boat_key) is None or datastore_client.get(slip_key) is None:
        return errorResponse(404, NO_SLIP_OR_BOAT)
    query = datastore_client.query(kind='Slip')
    query.key_filter(slip_key)
    slips = query.fetch()
    for slip in slips:
        if slip.get('current_boat',None) != None:
            return errorResponse(403, SLIP_OCCUPIED)
        slip.update({
            "current_boat": int(boat_id)
        })
        datastore_client.put(slip)
        return codeResponse(204)

def release_boat(slip_id, boat_id):
    if badInt(slip_id) or badInt(boat_id): return errorResponse(404, DOCKING_NOT_FOUND)
    dockedSlip = boat_is_docked(boat_id)
    boat_key = datastore_client.key('Boat', int(boat_id))
    slip_key = datastore_client.key('Slip', int(slip_id))
    if dockedSlip == None or int(dockedSlip) != int(slip_id) or datastore_client.get(boat_key) is None or datastore_client.get(slip_key) is None:
        return errorResponse(404, DOCKING_NOT_FOUND)

    query = datastore_client.query(kind='Slip')
    query.key_filter(slip_key)
    slips = query.fetch()
    for slip in slips:
        slip.update({
            "current_boat": None
        })
        datastore_client.put(slip)
        return codeResponse(204)

app = Flask(__name__)

@app.route('/boats', methods =['POST']) 
def postBoat():
    content = request.json
    if content == None or content.get('name',None) == None or content.get('type',None) == None or content.get('length',None) == None:
        return errorResponse(400,INCOMPLETE)
    id = store_boat(content['name'],content['type'],content['length']) 
    if id is not -1:
        status = 201 
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        selfUri = request.base_url + '/' + str(id)
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
    boat = get_boat(boat_id, request.base_url) 
    if boat is not None:
        print(boat)
        return make_response(jsonify(boat), 200)
    else: 
        return errorResponse(404,NO_ID)

@app.route('/boats/<string:boat_id>', methods =['PATCH']) 
def updateBoat(boat_id):
    content = request.json
    if content == None or content.get('name',None) == None or content.get('type',None) == None or content.get('length',None) == None:
        return errorResponse(400,INCOMPLETE)
    boat = update_boat(request.base_url, boat_id, content['name'], content['type'], content['length']) 
    if boat is not None:
        print(boat)
        return make_response(jsonify(boat), 200)
    else: 
        return errorResponse(404,NO_ID)

@app.route('/boats/<string:boat_id>', methods =['DELETE']) 
def deleteBoat(boat_id):
    status = delete_boat(boat_id) 
    if status == 204:
        return codeResponse(status)
    else:
        return errorResponse(status,NO_ID)

@app.route('/slips', methods =['POST']) 
def postSlip():
    content = request.json
    if content == None or content.get('number',None) == None:
        return errorResponse(400,INCOMPLETE_SLIP)
    id = store_slip(content['number']) 
    if id is not -1:
        status = 201 
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        content.update({"current_boat":None})
        selfUri = request.base_url + '/' + str(id)
        content.update({"self": selfUri })
        return contentResponse(status,content)
    else:
        return errorResponse(405,'Unknown')

@app.route('/slips', methods =['GET']) 
def getSlips():
    slips = get_slips(request.base_url)
    status = 200 if slips is not None else 405 
    print(slips)
    return make_response(jsonify(slips), status)

@app.route('/slips/<string:slip_id>', methods =['GET']) 
def getSlip(slip_id):
    slip = get_slip(slip_id, request.base_url) 
    if slip is not None:
        print(slip)
        return make_response(jsonify(slip), 200)
    else: 
        return errorResponse(404,NO_ID_SLIP)

@app.route('/slips/<string:slip_id>', methods =['DELETE']) 
def deleteSlip(slip_id):
    status = delete_slip(slip_id) 
    if status == 204:
        return codeResponse(status)
    else:
        return errorResponse(status,NO_ID_SLIP)

@app.route('/slips/<string:slip_id>/<string:boat_id>', methods =['PUT']) 
def dockBoat(slip_id, boat_id):
    response = dock_boat(slip_id, boat_id) 
    return response

@app.route('/slips/<string:slip_id>/<string:boat_id>', methods =['DELETE']) 
def releaseBoat(slip_id,boat_id):
    response = release_boat(slip_id,boat_id) 
    return response

@app.route('/')
def root():
    return Response("{'documentation_uri': " + DOCUMENTATION + " }\n", status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)