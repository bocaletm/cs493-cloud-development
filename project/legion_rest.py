from flask import Blueprint, request, Response
from json2html import *
from constants import Constants as C
from helpers import CustomResponse
from helpers import Validation
from helpers import Auth
from legion import Legion
from unit import Unit

bp = Blueprint('legion', __name__, url_prefix='/legions')

A = Auth()
R = CustomResponse()
V = Validation()
legion = Legion()
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
    result = V.validateLegion(content)
    print(result)
    if result.get('code') == 0:
        id = legion.store(content['name'], content['level'], content['terrainBonus'], userId) 
    else:
        id = -1
        return R.errorResponse(result.get('code'),result.get('msg'))   
    if id is not -1:
        print('Successfully created: ' + str(id))
        content.update({"id":id})
        content.update({"self": request.base_url + '/' + str(id)})
        content.update({"owner": userId })
        content.update({"units":[]})
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

    if not legion.exists(id):
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)

    if legion.getOwner(id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED + ' ' + id)
    
    return R.codeResponse(legion.delete(id))

@bp.route('', strict_slashes=False, methods=['GET'])
def get():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406, C.MIME_ERR)
    
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult

    userId = authResult

    legions = legion.get(request,userId)
    status = 200 if legions is not None else 500 
    print(legions)
    return R.contentResponse(status,legions)

@bp.route('/<string:legion_id>/units', strict_slashes=False, methods=['GET'])
def getUnits(legion_id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406, C.MIME_ERR)
    
    if V.badInt(legion_id):
        return R.errorResponse(400,C.NO_ID)

    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult

    userId = authResult

    if not legion.exists(legion_id):
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)

    if legion.getOwner(legion_id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED)

    units = legion.getSubentities(request,legion_id)

    print(units)

    status = 200 if units is not None else 500 

    return R.contentResponse(status,units)

@bp.route('/<string:legion_id>', strict_slashes=False, methods=['PUT'])
def put(legion_id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,C.MIME_ERR)
    if V.badInt(legion_id):
        return R.errorResponse(400,C.NO_ID)

    if not legion.exists(legion_id):
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)

    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult

    if legion.getOwner(legion_id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED)

    content = request.json
    result = V.validateLegion(content)
    print(result)
    if result.get('code') == 0:
        updatedLegion = legion.update(legion_id, content['name'], content['level'], content['terrainBonus'], userId)  
    else:
        return R.errorResponse(result.get('code'),result.get('msg'))   
    if updatedLegion is not None:
        updatedLegion.update({
            "id": legion_id,
            "self": request.base_url,
        })  
        print('Successfully updated: ' + str(id))
        return R.contentResponse(201,updatedLegion)
    else:
        return R.errorResponse(500,'Unknown')

@bp.route('/<string:legion_id>/<string:unit_id>', strict_slashes=False, methods=['PUT'])
def putUnit(legion_id,unit_id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,C.MIME_ERR)

    if V.badInt(legion_id) or V.badInt(unit_id):
        return R.errorResponse(400,C.NO_ID)

    if not unit.exists(unit_id):
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)
    
    if not legion.exists(legion_id):
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)

    if legion.legionFromUnit(unit_id) is not None:
        return R.errorResponse(400,C.ALREADY_ASSIGNED)

    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult

    if legion.getOwner(legion_id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED)

    if unit.getOwner(unit_id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED)

    if legion.putUnit(legion_id, unit_id) != None:
        print('Successfully added unit ' + unit_id + ' to legion ' + legion_id)
        return R.codeResponse(201)
    else:
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)

@bp.route('/<string:legion_id>/<string:unit_id>', strict_slashes=False, methods=['DELETE'])
def deleteUnit(legion_id,unit_id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406,C.MIME_ERR)
    if V.badInt(legion_id) or V.badInt(unit_id):
        return R.errorResponse(400,C.NO_ID)

    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult
    userId = authResult

    if not unit.exists(unit_id):
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)
    
    if not legion.exists(legion_id):
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)

    if str(legion.legionFromUnit(unit_id)) != legion_id or str(unit.unitFromLegion(legion_id)) != unit_id:
        return R.errorResponse(404,C.RELATIONSHIP_NOT_FOUND)

    if legion.getOwner(legion_id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED)

    if unit.getOwner(unit_id) != userId:
        return R.errorResponse(403,C.TOKEN_UNAUTHORIZED)

    if legion.deleteUnit(legion_id, unit_id) != None:
        print('Successfully removed unit ' + unit_id + ' from legion ' + legion_id)
        return R.codeResponse(204)
    else:
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)

@bp.route('/<string:id>', strict_slashes=False, methods=['GET'])
def get_one(id):
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406, C.MIME_ERR)
    
    authResult = A.checkAuthHeader(request.headers.get('Authorization'))
    if isinstance(authResult, Response):
        return authResult

    userId = authResult

    entity = legion.getOne(request,id)

    if entity == None:
        return R.errorResponse(404,C.ENTITY_NOT_FOUND)
    elif entity['owner'] != userId:
        return R.errorResponse(403,C.ID_MISMATCH)

    status = 200 if entity is not None else 500 
    print(entity)
    return R.contentResponse(status,entity)

@bp.route('', strict_slashes=False, methods=['DELETE'])
def deleteAll():
    return R.errorResponse(405,C.INVALID_METHOD)