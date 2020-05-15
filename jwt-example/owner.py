from flask import Blueprint, request, jsonify, make_response, Response
from google.cloud import datastore
import google.oauth2.id_token
from json2html import *
from constants import Constants as C
from helpers import Auth
from helpers import CustomResponse
from helpers import Validation

bp = Blueprint('owner', __name__, url_prefix='/owners')
datastore_client = datastore.Client()

A = Auth()
R = CustomResponse()
V = Validation()

def get_boats(owner_id, baseUri):
    limit = C.limit
    offset = int(request.args.get('offset', '0'))
    query = datastore_client.query(kind=C.kind)
    query.add_filter('owner', '=', owner_id)
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

@bp.route('/<string:owner_id>/boats', strict_slashes=False, methods=['GET'])
def getBoats(owner_id):
    if 'application/json' not in request.accept_mimetypes and 'text/html' not in request.accept_mimetypes:
        return R.errorResponse(406,C.MIME_ERR)
    if V.badInt(owner_id):
        return R.errorResponse(400,C.NO_ID)

    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult
    if userId != owner_id:
        print('owner_id ' + owner_id + ' does not match the id in the token ' + userId )
        return R.errorResponse(403,C.ID_MISMATCH)

    boat = get_boats(owner_id, request.base_url) 
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