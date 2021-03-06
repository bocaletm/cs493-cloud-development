from flask import Flask, Response
from flask_bootstrap import Bootstrap
from google.cloud import datastore
import auth
import boat
import owner
from constants import Constants as C

app = Flask(__name__)
app.register_blueprint(auth.bp)
app.register_blueprint(boat.bp)
app.register_blueprint(owner.bp)
Bootstrap(app)

datastore_client = datastore.Client()

@app.route('/')
def root():
    return Response("{'documentation_uri': " + C.DOCUMENTATION + " }\n", status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)