from celery.schedules import crontab

message_broker = {
        "type": "redis",
        "host": "localhost",
        "port": 6379,
        "database": 1,
        "password": None,
        "redis_max_connections": 5,
}

task_results_backend = {
        "type": "redis",
        "host": "localhost",
        "port": 6379,
        "database": 2,
        "password": None,
}

scheduler = {
        "CELERYBEAT_SCHEDULE": {
            "nytimes-fetch_articles-120-mins": {
                "task": "up.headliner.content.nytimes.tasks.fetch_articles",
                "schedule": crontab(hour="*/2"),
            },
        },
        "CELERY_TIMEZONE": "UTC",
}

tasks = [
        "up.headliner.content.nytimes.tasks",
]

redis = {
        "host": "127.0.0.1",
        "port": 6379,
        "database": 0,
        "password": None,
        "max_connections": 10,
}

providers = {
        "nytimes_mostpopular" : {
            "api_class": "up.headliner.content.nytimes.api.MostPopular",
            "api_url": "http://api.nytimes.com/svc/mostpopular/v2/{popularity_type}/{section}/30.json?api-key={api_key}",
            "api_key" : "",
            "category_max_articles": 50,
            "url_decoration": {
                "src": "recmoz",
            }
        },
}

server = {
        "http": {
            "host": "127.0.0.1",
            "port": 4355,
            "debug": True,
        },
        "routes": [
            "up.headliner.content.nytimes.urls"
        ],
}
