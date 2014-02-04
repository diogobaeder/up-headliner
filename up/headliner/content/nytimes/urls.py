import math
from operator import attrgetter
from flask import jsonify, request, Response
from up.headliner import Application
from up.headliner.http import webapp
import json

ERR_NO_QUERY = '{"err":"no query object provided"}'
ERR_INVALID_QUERY = '{"err":"invalid query"}'
MAX_RESPONSE_SIZE = 100

@webapp.route("/nytimes/mostpopular.json", methods=["GET"])
def index():
    """
    Return a listing of available interests
    """
    app = Application.instance()
    categories = app.article_store.get_category_counts("nytimes_mostpopular")
    for category, score in categories.iteritems():
        categories[category] = int(score)
    return jsonify(d=categories)

@webapp.route("/nytimes/mostpopular/personalize", methods=["POST"])
def personalize():
    """
    Return results based on user query
    Request Content-Type must be set to application/json
    The payload must be a json ascii string.

    e.g. {"Arts":0.9,"Autos":0.9}
    """
    limit = request.args.get("limit", 20)
    try:
        limit = int(limit)
    except ValueError:
        return Response(response=ERR_INVALID_QUERY, status=400)

    if limit < 0:
        return Response(response=ERR_INVALID_QUERY, status=400)
    elif limit > MAX_RESPONSE_SIZE:
        limit = MAX_RESPONSE_SIZE

    query = request.get_json()
    if query is None:
        return Response(response=ERR_NO_QUERY, status=400)
    elif type(query) != dict:
        return Response(response=ERR_INVALID_QUERY, status=400)

    numbers = {}
    weight_total = 0.0
    for category, weight in query.iteritems():
        if type(weight) not in (float, int) or weight < 0 or weight > 1:
            return Response(response=ERR_INVALID_QUERY, status=400)
        # weight_total should always be float
        weight_total += weight
    for category, weight in query.iteritems():
        numbers[category] = int(math.ceil(weight/weight_total*limit))

    # collect all recommendations for each category
    app = Application.instance()
    recommendations = []
    for category in numbers:
        recommendations.extend(app.article_store.fetch("nytimes_mostpopular", category, limit=numbers[category], withscores=True))

    # sort and deduplicate recommendations. store results in articles array
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    articles = []
    url_set = set()
    for article in recommendations:
        if article["url"] not in url_set:
            del article["score"]
            articles.append(article)
            url_set.add(article["url"])
        # inforce articles limit
        if len(articles) >= limit:
            break

    return jsonify(d=articles,num_articles=len(articles))

@webapp.route("/nytimes/mostpopular/<interest_name>.json", methods=["GET"])
def fetch_interest(interest_name):
    """
    Returns articles belonging to the provided interest name
    """
    limit = request.args.get("limit", 20)
    try:
        limit = int(limit)
    except ValueError:
        return Response(response=ERR_INVALID_QUERY, status=400)

    if limit < 0:
        return Response(response=ERR_INVALID_QUERY, status=400)
    elif limit > MAX_RESPONSE_SIZE:
        limit = MAX_RESPONSE_SIZE

    app = Application.instance()
    articles = app.article_store.fetch("nytimes_mostpopular", interest_name, limit)
    return jsonify(d=articles,num_articles=len(articles))
