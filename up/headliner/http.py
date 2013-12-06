from flask import Flask
webapp = Flask("up.headliner")

def load_routes(routes):
    for route in routes:
        __import__(route)
