from flask import Blueprint, request, jsonify, make_response
from google.cloud import datastore
import google.oauth2.id_token
import boat
from constants import Constants as C
from helpers import CustomResponse
from helpers import Validation
import load as L

bp = Blueprint('boat', __name__, url_prefix='/boats')
datastore_client = datastore.Client()

R = CustomResponse()
V = Validation()

def store_boat(name, boatType, length):
    kind = 'Boat'
    boat_key = datastore_client.key(kind)
    boat = datastore.Entity(key=boat_key)
    boat.update({
        "name": name, 
        "type": boatType, 
        "length": length,
        "loads": [],
    })
    try: 
        datastore_client.put(boat)
    except Exception as err: 
        print('Failed to save Boat: ' + name)
        print(err)
        return -1
    return boat.key.id_or_name

def get_boats(baseUri):
    limit = C.limit
    offset = int(request.args.get('offset', '0'))
    query = datastore_client.query(kind='Boat')
    iterator = None
    boats = None
    nextUri = None
    try: 
        iterator = query.fetch(limit=limit, offset=offset)
        pages = iterator.pages
        boats = list(next(pages))
    except:
        print('Failed to fetch Boats')
    for boat in boats:
        id = boat.key.id_or_name
        if (boat['loads'] is not None):
            for loadID in boat['loads']:
                boat['loads'].remove(loadID)
                selfUri =  baseUri.split('boats/', 1)[0] + 'loads/' + str(loadID)
                boat['loads'].append({"id":str(loadID), "self":selfUri})
        selfUri = baseUri + '/' + str(id)
        boat.update({"id":boat.key.id_or_name})
        boat.update({"self":selfUri})
        if iterator.next_page_token:
            nextUri = baseUri + '?offset=' + str(offset + limit)
            boat.update({"next":nextUri})
    if nextUri is not None:
        response = {"boats":boats,"next":nextUri}
    else:
        response = {"boats":boats}
    return response

def get_boat(boat_id, baseUri):
    if V.badInt(boat_id): return None
    query = datastore_client.query(kind='Boat')
    boat_key = datastore_client.key('Boat', int(boat_id))
    query.key_filter(boat_key)
    boats = query.fetch()
    for boat in boats:
        id = boat.key.id_or_name
        if (boat['loads'] is not None):
            for loadID in boat['loads']:
                boat['loads'].remove(loadID)
                selfUri =  baseUri.split('boats/', 1)[0] + 'loads/' + str(loadID)
                boat['loads'].append({"id":str(loadID), "self":selfUri})
        boat.update({"id":id})
        boat.update({"self":baseUri})
        return boat

def update_boat(baseUri, boat_id, name, boatType, length):
    if V.badInt(boat_id): return None
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

def delete_boat(boat_id,baseUri):
    boat_key = datastore_client.key('Boat', int(boat_id))
    if datastore_client.get(boat_key) is not None:
        boat = get_boat(boat_id,baseUri)
        for load in boat['loads']:
            print(L.remove_boat_from_load(load['id'],boat_id))
        datastore_client.delete(boat_key)
    return 204

@bp.route('', methods=['POST'])
def postBoat():
    content = request.json
    if content == None or content.get('name',None) == None or content.get('type',None) == None or content.get('length',None) == None:
        return R.errorResponse(400,C.INCOMPLETE)
    id = store_boat(content['name'],content['type'],content['length']) 
    if id is not -1:
        status = 201 
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        selfUri = request.base_url + '/' + str(id)
        content.update({"self": selfUri })
        return R.contentResponse(status,content)
    else:
        return R.errorResponse(405,'Unknown')

@bp.route('', methods=['GET'])
def getBoats():
    boats = get_boats(request.base_url)
    status = 200 if boats is not None else 405 
    print(boats)
    return make_response(jsonify(boats), status)

@bp.route('/<string:boat_id>', methods=['GET'])
def getBoat(boat_id):
    if V.badInt(boat_id):
        return R.errorResponse(403,C.NO_ID)
    boat = get_boat(boat_id, request.base_url) 
    if boat is not None:
        print(boat)
        return make_response(jsonify(boat), 200)
    else: 
        return R.errorResponse(404,C.NO_ID_BOAT)

@bp.route('/<string:boat_id>', methods=['PATCH'])
def updateBoat(boat_id):
    content = request.json
    if content == None or content.get('name',None) == None or content.get('type',None) == None or content.get('length',None) == None:
        return R.errorResponse(400,C.INCOMPLETE)
    boat = update_boat(request.base_url, boat_id, content['name'], content['type'], content['length']) 
    if boat is not None:
        print(boat)
        return make_response(jsonify(boat), 200)
    else: 
        return R.errorResponse(404,C.NO_ID)

@bp.route('/<string:boat_id>', methods=['DELETE'])
def deleteBoat(boat_id):
    if V.badInt(boat_id):
        return R.errorResponse(403,C.NO_ID)
    return R.codeResponse(delete_boat(boat_id,request.base_url))