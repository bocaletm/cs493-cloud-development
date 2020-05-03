from flask import Blueprint, request, jsonify, make_response
from google.cloud import datastore
import google.oauth2.id_token
from json2html import *
from constants import Constants as C
from helpers import CustomResponse
from helpers import Validation

bp = Blueprint('boat', __name__, url_prefix='/boats')
datastore_client = datastore.Client()

R = CustomResponse()
V = Validation()

def nameIsUnique(name,boat_id):
    query = datastore_client.query(kind=C.kind)
    query.add_filter('name', '=', name)
    query.keys_only()
    boats = query.fetch()
    for boat in boats:
        if boat.key.id_or_name != boat_id:
            return False
    return True

def store_boat(name, boatType, length):
    boat_key = datastore_client.key(C.kind)
    boat = datastore.Entity(key=boat_key)
    boat.update({
        "name": name, 
        "type": boatType, 
        "length": length,
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
    query = datastore_client.query(kind=C.kind)
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
    query = datastore_client.query(kind=C.kind)
    boat_key = datastore_client.key(C.kind, int(boat_id))
    query.key_filter(boat_key)
    boats = query.fetch()
    for boat in boats:
        id = boat.key.id_or_name
        boat.update({"id":id})
        boat.update({"self":baseUri})
        return boat

def update_boat(baseUri, boat_id, name, boatType, length):
    if V.badInt(boat_id): return None
    query = datastore_client.query(kind=C.kind)
    boat_key = datastore_client.key(C.kind, int(boat_id))
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
    return None

def patch_boat(baseUri, boat_id, name, boatType, length):
    if V.badInt(boat_id): return None
    query = datastore_client.query(kind=C.kind)
    boat_key = datastore_client.key(C.kind, int(boat_id))
    query.key_filter(boat_key)
    boats = query.fetch()
    for boat in boats:
        id = boat.key.id_or_name
        if name is not None:
            boat.update({
                "name": name, 
            })
        if boatType is not None:
            boat.update({
                "type": boatType, 
            })
        if length is not None:
            boat.update({
                "length": length, 
            })
        datastore_client.put(boat)
        boat.update({
            "id": id,
            "self": baseUri
        })        
        return boat    
    return None
def delete_boat(boat_id,baseUri):
    boat_key = datastore_client.key('Boat', int(boat_id))
    if datastore_client.get(boat_key) is not None:
        datastore_client.delete(boat_key)
    return 204

@bp.route('', methods=['POST'])
def postBoat():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,'Unsupported mimetype in request')
    content = request.json
    if content and content.get('name') and not nameIsUnique(content['name'], 0):
        return R.errorResponse(403,C.NOT_UNIQUE)
    result = V.validateBoat(content)
    print(result)
    if result.get('code') == 0:
        id = store_boat(content['name'],content['type'],content['length']) 
    else:
        id = -1
        return R.errorResponse(result.get('code'),result.get('msg'))   
    if id is not -1:
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        selfUri = request.base_url + '/' + str(id)
        content.update({"self": selfUri })
        return R.contentResponse(201,content)
    else:
        return R.errorResponse(405,'Unknown')

@bp.route('', methods=['GET'])
def getBoats():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,'Unsupported mimetype in request')
    boats = get_boats(request.base_url)
    status = 200 if boats is not None else 500 
    print(boats)
    return R.contentResponse(status,boats)

@bp.route('/<string:boat_id>', strict_slashes=False, methods=['GET'])
def getBoat(boat_id):
    if 'application/json' not in request.accept_mimetypes and 'text/html' not in request.accept_mimetypes:
        return R.errorResponse(406,'Unsupported mimetype in request')
    if V.badInt(boat_id):
        return R.errorResponse(400,C.NO_ID)
    boat = get_boat(boat_id, request.base_url) 
    if boat is not None:
        print(boat)
        if 'application/json' in request.accept_mimetypes:
            print('sending json')
            response =  make_response(jsonify(boat), 200)
            response.headers.set('Content-Type', 'application/json')
        else:
            response = make_response(json2html.convert(json = boat),200)
            response.headers.set('Content-Type', 'text/html')
        return response
    else: 
        return R.errorResponse(404,C.NO_ID_BOAT)

@bp.route('/<string:boat_id>', strict_slashes=False, methods=['PUT'])
def updateBoat(boat_id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,'Unsupported mimetype in request')
    if V.badInt(boat_id):
        return R.errorResponse(400,C.NO_ID)
    content = request.json
    if content and content.get('name') and not nameIsUnique(content['name'], boat_id):
        return R.errorResponse(403,C.NOT_UNIQUE)

    result = V.validateBoat(content)
    print(result)
    if result.get('code') == 0:
        boat = update_boat(request.base_url, boat_id, content['name'], content['type'], content['length']) 
    else:
        return R.errorResponse(result.get('code'),result.get('msg'))
    if boat is not None:
        print(boat)
        response =  make_response(jsonify(boat), 303)
        response.headers['Location'] = request.base_url
        return response
    else: 
        return R.errorResponse(404,C.NO_ID_BOAT)

@bp.route('/<string:boat_id>', strict_slashes=False, methods=['PATCH'])
def patchBoat(boat_id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,'Unsupported mimetype in request')
    if V.badInt(boat_id):
        return R.errorResponse(400,C.NO_ID)
    content = request.json
    if content and content.get('name') and not nameIsUnique(content['name'], boat_id):
        return R.errorResponse(403,C.NOT_UNIQUE)
    result = V.validatePartialBoat(content)
    print(result)
    if result.get('code') == 0:
        boat = patch_boat(request.base_url, boat_id, content.get('name',None), content.get('type',None), content.get('length',None)) 
    else:
        return R.errorResponse(result.get('code'),result.get('msg'))
    if boat is not None:
        print(boat)
        return make_response(jsonify(boat), 201)
    else: 
        return R.errorResponse(404,C.NO_ID_BOAT)

@bp.route('/<string:boat_id>', strict_slashes=False, methods=['DELETE'])
def deleteBoat(boat_id):
    if V.badInt(boat_id):
        return R.errorResponse(403,C.NO_ID)
    return R.codeResponse(delete_boat(boat_id,request.base_url))

@bp.route('/', methods=['GET'])
def badGet():
    return R.redirect(request.base_url[:-1])

@bp.route('/', methods=['POST'])
def badPost():
    return R.redirect(request.base_url[:-1])

@bp.route('', strict_slashes=False, methods=['PUT'])
def badPut():
    return R.errorResponse(405,'Method not allowed')

@bp.route('', strict_slashes=False, methods=['PATCH'])
def badPatch():
    return R.errorResponse(405,'Method not allowed')

@bp.route('', strict_slashes=False, methods=['DELETE'])
def badDelete():
    return R.errorResponse(405,'Method not allowed')