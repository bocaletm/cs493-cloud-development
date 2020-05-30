from legion_rest import legion
from flask import Blueprint, request, Response
from json2html import *
from constants import Constants as C
from helpers import CustomResponse
from helpers import Validation
from helpers import Auth
from unit import Unit

bp = Blueprint('unit', __name__, url_prefix='/units')


A = Auth()
R = CustomResponse()
V = Validation()
unit = Unit()

@bp.route('', strict_slashes=False, methods=['POST'])
def post():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,C.MIME_ERR)
    
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult

    content = request.json
    result = V.validateUnit(content)
    print(result)
    if result.get('code') == 0:
        id = unit.store(content['name'], content['strength'], content['targetRange'], content['category'], userId) 
    else:
        id = -1
        return R.errorResponse(result.get('code'),result.get('msg'))   
    if id is not -1:
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        content.update({"self": request.base_url + '/' + str(id)})
        content.update({"owner": userId })
        return R.contentResponse(201,content)
    else:
        return R.errorResponse(500,'Unknown')

@bp.route('/<string:id>', strict_slashes=False, methods=['DELETE'])
def delete(id):
    if V.badInt(id):
        return R.errorResponse(400,C.NO_ID)
    
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult

    if unit.getOwner(id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED + ' ' + id)
        
    legion_id = legion.legionFromUnit(id)

    if legion_id != None:
        legion.deleteUnit(legion_id,id)

    return R.codeResponse(unit.delete(id))

@bp.route('', strict_slashes=False, methods=['GET'])
def get():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406, C.MIME_ERR)
    
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult

    userId = authResult

    units = unit.get(request,userId)
    status = 200 if units is not None else 500 
    print(units)
    return R.contentResponse(status,units)

@bp.route('/<string:id>', strict_slashes=False, methods=['GET'])
def get_one(id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406, C.MIME_ERR)
    
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult

    userId = authResult

    entity = unit.getOne(request,id)

    if entity == None:
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)
    elif entity['owner'] != userId:
        return R.errorResponse(403,C.ID_MISMATCH)

    status = 200 if entity is not None else 500 
    print(entity)
    return R.contentResponse(status,entity)

@bp.route('/<string:unit_id>', strict_slashes=False, methods=['PUT'])
def put(unit_id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,C.MIME_ERR)
    if V.badInt(unit_id):
        return R.errorResponse(400,C.NO_ID)


    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult

    if unit.getOwner(unit_id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED)

    content = request.json
    result = V.validateUnit(content)
    print(result)
    if result.get('code') == 0:
        updatedUnit = unit.update(unit_id, content['name'], content['strength'], content['targetRange'], content['category'], userId)  
    else:
        return R.errorResponse(result.get('code'),result.get('msg'))   
    if updatedUnit is not None:
        updatedUnit.update({
            "id": unit_id,
            "self": request.base_url,
        })  
        print('Successfully updated: ' + str(id))
        return R.contentResponse(201,updatedUnit)
    else:
        return R.errorResponse(500,'Unknown')