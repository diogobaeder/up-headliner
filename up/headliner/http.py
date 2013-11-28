from flask import Flask, jsonify, request
app = Flask("up.headliner")

@app.route('/nytimes/popular')
def index():
    interests = request.args.get("interests", "").split(",")
    return jsonify(type="echo", interests=interests)
