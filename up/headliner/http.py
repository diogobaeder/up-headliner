import up.headliner
from flask import Flask, Response
webapp = Flask("up.headliner")

@webapp.route("/status")
def root():
    return Response("Headliner {0} STATUS OK".format(up.headliner.__VERSION__), mimetype="text/plain")

def load_routes(routes):
    for route in routes:
        __import__(route)
