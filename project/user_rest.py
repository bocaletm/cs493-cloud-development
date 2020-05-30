from legion_rest import legion
from flask import Blueprint, request, Response
from json2html import *
from constants import Constants as C
from helpers import CustomResponse
from helpers import Validation
from user import User

bp = Blueprint('user', __name__, url_prefix='/users')


R = CustomResponse()
V = Validation()
user = User()

@bp.route('', strict_slashes=False, methods=['GET'])
def get():
    if 'application/json' not in request.accept_mimetypes:
        return R.errorResponse(406, C.MIME_ERR)

    users = user.get(request)
    status = 200 if users is not None else 500 
    print(users)
    return R.contentResponse(status,users)