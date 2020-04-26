import boat as B
from json import load
from helpers import Conversion
from flask import Blueprint, request, jsonify, make_response
from google.cloud import datastore
import google.oauth2.id_token
from constants import Constants as C
from helpers import Conversion 
from helpers import CustomResponse
from helpers import Validation

bp = Blueprint('load', __name__, url_prefix='/loads')
datastore_client = datastore.Client()

convert = Conversion()
R = CustomResponse()
V = Validation()
kind = 'Load'

def already_assigned(load_id):
    query = datastore_client.query(kind='Boat')
    query.add_filter('loads', '=', int(load_id))
    query.keys_only()
    boats = query.fetch()
    for boat in boats:
        print('load already assigned to boats: ' + str(boat))
        return True
    return False

def add_load_to_boat(load_id,boat_id):
    boat_key = datastore_client.key('Boat', int(boat_id))
    load_key = datastore_client.key('Load', int(load_id))
    boat_query = datastore_client.query(kind='Boat')
    boat_query.key_filter(boat_key)
    boats = boat_query.fetch()
    try:
        for boat in boats:
            boat['loads'].append(load_key.id_or_name)
            datastore_client.put(boat)
            return True
    except Exception as err:
        print(err)
        return False

def add_boat_to_load(load_id,boat_id):
    boat_key = datastore_client.key('Boat', int(boat_id))
    load_key = datastore_client.key('Load', int(load_id))
    load_query = datastore_client.query(kind='Load')
    load_query.key_filter(load_key)
    loads = load_query.fetch()
    try:
        for load in loads:
            load.update({'carrier':boat_key.id_or_name})
            datastore_client.put(load)
            return True
    except Exception as err:
        print(err)
        return False

def assign_load(load_id,boat_id):
    boat_key = datastore_client.key('Boat', int(boat_id))
    load_key = datastore_client.key('Load', int(load_id))
    if datastore_client.get(boat_key) is None or datastore_client.get(load_key) is None:
        return R.errorResponse(404, C.NO_LOAD_OR_BOAT)
    
    boatSucceeded = add_boat_to_load(load_id,boat_id)
    loadSucceded = add_load_to_boat(load_id,boat_id)

    error = False
    
    if not loadSucceded:
        remove_boat_from_load(load_id,boat_id)
        error = True
        print('failed to add load ' + load_id +  ' to boat ' + boat_id)
    if not boatSucceeded:
        remove_load_from_boat(load_id,boat_id)
        error = True
        print('failed to add boat ' + boat_id + ' to load ' + load_id)

    if error: 
        return R.codeResponse(500)
    else: 
        return R.codeResponse(201)

def delete_load(load_id,baseUri):
    if V.badInt(load_id): return 403
    load_key = datastore_client.key('Load', int(load_id))
    if datastore_client.get(load_key) is not None:
        load = get_load(load_id,baseUri)
        boat_id = load['carrier']
        if boat_id is not None:
            remove_load_from_boat(load_key.id_or_name,int(boat_id['id']))
        datastore_client.delete(load_key)
    return 204

def remove_load_from_boat(load_id,boat_id):
    boat_key = datastore_client.key('Boat', int(boat_id))
    load_key = datastore_client.key('Load', int(load_id))
    boat_query = datastore_client.query(kind='Boat')
    boat_query.key_filter(boat_key)
    boats = boat_query.fetch()
    try:
        for boat in boats:
            boat['loads'].remove(load_key.id_or_name)
            datastore_client.put(boat)
            return True
    except:
        return False

def remove_boat_from_load(load_id,boat_id):
    load_key = datastore_client.key('Load', int(load_id))
    load_query = datastore_client.query(kind='Load')
    load_query.key_filter(load_key)
    loads = load_query.fetch()
    try:
        for load in loads:
            load.update({"carrier": None})
            datastore_client.put(load)
            return True
    except:
        return False

def remove_load(load_id,boat_id):
    try:
        remove_load_from_boat(load_id,boat_id)
        remove_boat_from_load(load_id,boat_id)
        print("load_id: " + load_id + " boat_id: " + boat_id)
        return R.codeResponse(204)
    except: 
        print("load_id: " + load_id + " boat_id: " + boat_id)
        return R.codeResponse(500)

def store_load(weight,content,delivery_date):
    load_key = datastore_client.key(kind)
    load = datastore.Entity(key=load_key)
    load.update({
        "weight": weight, 
        "carrier": None, 
        "content": content,
        "delivery_date": delivery_date,
    })
    try: 
        datastore_client.put(load)
    except Exception as err: 
        print('Failed to save Load: ' + content)
        print(err)
        return -1
    return load.key.id_or_name

def get_loads(baseUri):
    limit = C.limit
    offset = int(request.args.get('offset', '0'))
    query = datastore_client.query(kind=kind)
    iterator = None
    loads = None
    nextUri = None
    try: 
        iterator = query.fetch(limit=limit, offset=offset)
        pages = iterator.pages
        loads = list(next(pages))
    except:
        print('Failed to fetch page from ' + kind)
    for load in loads:
        id = load.key.id_or_name
        selfUri = baseUri + '/' + str(id)
        if (load['carrier'] is not None):
            print(load['carrier'])
            boat = B.get_boat(load['carrier'],baseUri)
            boatSelfUri =  baseUri.split('loads', 1)[0] + 'boats/' + str(boat['id'])
            boat['self'] = boatSelfUri
            del boat['loads']
            del boat['length']
            del boat['type']
            load.update({"carrier":boat})
        load.update({"id":load.key.id_or_name})
        load.update({"self":selfUri})
        date = convert.stringFromEpoch(load.get('delivery_date'))
        load.update({"delivery_date":date})
        if iterator.next_page_token:
            nextUri = baseUri + '?offset=' + str(offset + limit)
            load.update({"next":nextUri})
    if nextUri is not None:
        response = {"loads":loads,"next":nextUri}
    else:
        response = {"loads":loads}
    return response

def get_load(load_id, baseUri):
    if V.badInt(load_id): return None
    query = datastore_client.query(kind=kind)
    load_key = datastore_client.key(kind, int(load_id))
    query.key_filter(load_key)
    loads = query.fetch()
    for load in loads:
        id = load.key.id_or_name
        date = convert.stringFromEpoch(load.get('delivery_date'))
        if (load['carrier'] is not None):
            boat = B.get_boat(load['carrier'],baseUri)
            boatSelfUri =  baseUri.split('loads', 1)[0] + 'boats/' + str(boat['id'])
            boat['self'] = boatSelfUri
            del boat['loads']
            del boat['length']
            del boat['type']
            load.update({"carrier":boat})
        load.update({"id":id})
        load.update({"delivery_date":date})
        load.update({"self":baseUri})
        return load

@bp.route('', methods=['POST'])
def postLoad():
    content = request.json
    if content == None or content.get('weight',None) == None or content.get('content',None) == None or content.get('delivery_date',None) == None:
        return R.errorResponse(400,C.INCOMPLETE)
    dashedDate = content['delivery_date'].replace('/','-')
    if V.badDate(dashedDate) or V.badInt(content['weight']):
        return R.errorResponse(500,C.INVALID_DATA)
    id = store_load(content['weight'],content['content'],convert.epochFromString(content['delivery_date'])) 
    if id is not -1:
        status = 201 
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        content.update({"carrier":{}})
        selfUri = request.base_url + '/' + str(id)
        content.update({"self": selfUri })
        return R.contentResponse(status,content)
    else:
        return R.errorResponse(405,'Unknown')

@bp.route('/<string:load_id>', methods=['GET'])
def getLoad(load_id):
    if V.badInt(load_id):
        return R.errorResponse(403,C.NO_ID)
    load = get_load(load_id, request.base_url) 
    if load is not None:
        print(load)
        return make_response(jsonify(load), 200)
    else: 
        return R.errorResponse(404,C.NO_ID_LOAD)

@bp.route('', methods=['GET'])
def getLoads():
    loads = get_loads(request.base_url)
    status = 200 if loads is not None else 405 
    print(loads)
    return make_response(jsonify(loads), status)

@bp.route('/<string:load_id>/<string:boat_id>', methods=['PUT'])
def assignLoad(load_id,boat_id):
    if V.badInt(load_id) or V.badInt(boat_id):
        return R.errorResponse(403,C.NO_ID)
    if already_assigned(load_id):
        return R.errorResponse(403,C.ALREADY_ASSIGNED)
    return assign_load(load_id,boat_id)

@bp.route('/<string:load_id>/<string:boat_id>', methods=['DELETE'])
def removeLoad(load_id,boat_id):
    if V.badInt(load_id) or V.badInt(boat_id):
        return R.errorResponse(404,C.NO_ID)
    return remove_load(load_id,boat_id)

@bp.route('/<string:load_id>', methods=['DELETE'])
def deleteLoad(load_id):
    if V.badInt(load_id):
        return R.errorResponse(403,C.NO_ID)
    return R.codeResponse(delete_load(load_id,request.base_url))