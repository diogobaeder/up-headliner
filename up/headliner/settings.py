message_broker = {
        "type": "redis",
        "host": "localhost",
        "port": 6379,
        "database": 1,
        "password": None,
        "redis_max_connections": 5,
}

redis = {
        "host": "127.0.0.1",
        "port": 6379,
        "database": 0,
        "password": None,
        "max_connections": 10,
}

providers = {
        "nytimes_mostpopular" : {
            "api_url": "http://api.nytimes.com/svc/mostpopular/v2/{popularity_type}/{section}/30.json?api-key={api_key}",
            "api_key" : "",
        },
}

server = {
        "host": "127.0.0.1",
        "port": 4355,
        "debug": True,
}
