from flask import Response
import json

class Validation:
    def badInt(self,s):
        try: 
            int(s)
            return False
        except ValueError:
            return True

class CustomResponse:
    def errorResponse(self,status,msg):
        return Response(json.dumps({'Error': msg}, sort_keys=True, indent=4),status, mimetype='application/json')

    def codeResponse(self,status):
        return Response(status=status,mimetype='application/json')

    def contentResponse(self,status,content):
        return Response(json.dumps(content, sort_keys=True, indent=4),status=status, mimetype='application/json')