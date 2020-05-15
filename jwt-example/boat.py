from flask import Blueprint, request, Response
from google.cloud import datastore
from json2html import *
from constants import Constants as C
from helpers import CustomResponse
from helpers import Validation
from helpers import Auth

bp = Blueprint('boat', __name__, url_prefix='/boats')
datastore_client = datastore.Client()

A = Auth()
R = CustomResponse()
V = Validation()

def getBoatOwner(boat_id):
    query = datastore_client.query(kind=C.kind)
    boat_key = datastore_client.key(C.kind, int(boat_id))
    query.key_filter(boat_key)
    boats = query.fetch()
    for boat in boats:
        return boat['owner']
    return -1

def store_boat(name, boatType, length, userId):
    boat_key = datastore_client.key(C.kind)
    boat = datastore.Entity(key=boat_key)
    boat.update({
        "name": name, 
        "type": boatType, 
        "length": length,
        "owner": userId,
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
        boat.update({"id":boat.key.id_or_name})
        if iterator.next_page_token:
            nextUri = baseUri + '?offset=' + str(offset + limit)
            boat.update({"next":nextUri})
    if nextUri is not None:
        response = {"boats":boats,"next":nextUri}
    else:
        response = {"boats":boats}
    return response
        
def delete_boat(boat_id,baseUri):
    boat_key = datastore_client.key('Boat', int(boat_id))
    if datastore_client.get(boat_key) is not None:
        datastore_client.delete(boat_key)
        return 204
    else:
        return 401

@bp.route('', methods=['POST'])
def postBoat():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,C.MIME_ERR)
    
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult
    content = request.json
    result = V.validateBoat(content)
    print(result)
    if result.get('code') == 0:
        id = store_boat(content['name'],content['type'],content['length'], userId) 
    else:
        id = -1
        return R.errorResponse(result.get('code'),result.get('msg'))   
    if id is not -1:
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        content.update({"owner": userId })
        return R.contentResponse(201,content)
    else:
        return R.errorResponse(500,'Unknown')

@bp.route('', methods=['GET'])
def getBoats():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406, C.MIME_ERR)
    boats = get_boats(request.base_url)
    status = 200 if boats is not None else 500 
    print(boats)
    return R.contentResponse(status,boats)

@bp.route('/<string:boat_id>', strict_slashes=False, methods=['DELETE'])
def deleteBoat(boat_id):
    if V.badInt(boat_id):
        return R.errorResponse(400,C.NO_ID)
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult
        
    boatOwner = getBoatOwner(boat_id)
    if boatOwner == userId:
        return R.codeResponse(delete_boat(boat_id,request.base_url))
    elif boatOwner == -1:
        return R.errorResponse(403, C.kind + ' ' + boat_id + ' ' + C.NOT_EXISTS)
    else: 
        return R.errorResponse(403, C.TOKEN_UNAUTHORIZED + ' ' + boat_id)

@bp.route('/', methods=['GET'])
def badGet():
    return R.redirect(request.base_url[:-1])

@bp.route('/', methods=['POST'])
def badPost():
    return R.redirect(request.base_url[:-1])

@bp.route('', strict_slashes=False, methods=['DELETE'])
def badDelete():
    return R.errorResponse(405, C.BAD_METHOD)