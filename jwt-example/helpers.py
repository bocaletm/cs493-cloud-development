import datetime
from flask import Response
from google.oauth2 import id_token
from google.auth.transport import requests
import json
import re
from os import environ
from constants import Constants as C

class Validation:
    def validationSwitch(self,num):
        switcher = {
            0: {
                'code': 0, 
                'msg': ''
            },
            1: {
                'code': 400, 
                'msg': C.EXTRA_ATTRIBUTES
            },          
            2: {
                'code': 400, 
                'msg': C.INCOMPLETE
            },
            3: {
                'code': 400, 
                'msg': C.ID_UPDATE
            },
            4: {
                'code': 400, 
                'msg': C.INVALID_DATA
            }
        }
        return switcher.get(num)

    def badInt(self,s):
        try: 
            int(s)
            return False
        except ValueError:
            return True

    def badDate(self,s):
        try:
            date = datetime.datetime.strptime(s, '%m-%d-%Y')
            return False
        except Exception:
            return True

    def hasInvalidChars(self,stringToCheck):
        if not re.search(C.validChars, stringToCheck):
            return True
        return False

    def validBoatContent(self,name,boatType,length):
        if self.badInt(length):
            print('Error: bad int in length')
            return False
        if length > C.maxBoatLength:
            print('Error: boat too long')
            return False
        if (len(name) < C.minStringLength or len(boatType) < C.minStringLength):
            print('Error: name or type too short')
            return False
        if len(name) > C.maxNameLength:
            print('Error: name too long')
            return False
        if len(boatType) > C.maxTypeLength:
            print('Error: type too long')
            return False
        if self.hasInvalidChars(name):
            print('Error: name has invalid characters')
            return False
        if self.hasInvalidChars(boatType):
            print('Error: type has invalid characters')
            return False
        return True

    def validateBoat(self,content):
        if content == None or len(content) > C.NUM_BOAT_ATTRIBUTES:
            return self.validationSwitch(1)
        if content.get('name',None) == None or content.get('type',None) == None or content.get('length',None) == None:
            return self.validationSwitch(2)
        if content.get('id') != None or content.get('_id') != None:
            return self.validationSwitch(3)
        if not self.validBoatContent(name=content['name'], boatType=content['type'],length=content['length']):
            return self.validationSwitch(4)
        return self.validationSwitch(0)

    def validatePartialBoat(self,content):
        modifiedContent = dict(content)
        modifiedContent['name'] = content.get('name','default')
        modifiedContent['type'] = content.get('type','default')
        modifiedContent['length'] = content.get('length',100)
        return self.validateBoat(modifiedContent)

class Conversion:
    def epochFromString(self,s):
        return datetime.datetime.timestamp(datetime.datetime.strptime(s.replace('/','-'), '%m-%d-%Y'))

    def stringFromEpoch(self,e):
        return datetime.datetime.fromtimestamp(e).strftime('%m-%d-%Y').replace('-','/')

class CustomResponse:
    def errorResponse(self,status,msg):
        return Response(json.dumps({'Error': msg}, sort_keys=True, indent=4),status, mimetype='application/json')

    def codeResponse(self,status):
        return Response(status=status,mimetype='application/json')

    def contentResponse(self,status,content):
        return Response(json.dumps(content, sort_keys=True, indent=4),status=status, mimetype='application/json')

    def redirect(self,location):
        response = Response(status=301)
        response.headers['Location'] = location
        return response

class Auth:
    R = CustomResponse()
    def validateJwtGetSub(self,jwt):
        id_info = id_token.verify_oauth2_token(jwt, requests.Request(), environ.get("CLIENT_ID"))
        print(id_info)
        if id_info['iss'] != C.AUTH_ISSUER:
            raise ValueError('Wrong issuer')
        return id_info['sub']

    def checkAuthHeader(self,auth_header):
        authToken = ''
        userId = ''
        tokenArray = []
        if auth_header:
            try:
                tokenArray = auth_header.split(' ')
                if tokenArray[0] != 'Bearer' or tokenArray[1] == '':
                    raise IndexError
                authToken = tokenArray[1]
            except IndexError:
                return self.R.errorResponse(401, C.BEARER_ERR + ' ' + tokenArray[0])
            try: 
                userId = self.validateJwtGetSub(authToken)
            except ValueError:
                return self.R.errorResponse(401,C.INVALID_TOKEN)
        else:
            return self.R.errorResponse(401,C.NO_TOKEN)
        if userId == '':
            return self.R.errorResponse(500,C.UNKNOWN_AUTH)
        else:
            return userId