import datetime
from flask import Response
import json

class Validation:
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