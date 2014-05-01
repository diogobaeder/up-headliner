import logging

from up.headliner import Application
from up.headliner.aggregator_worker import aggregator


logger = logging.getLogger("headliner")


@aggregator.task(ignore_result=True)
def fetch_articles(num_urls=None):
    app = Application.instance()
    most_popular = app.providers["nytimes_mostpopular"]
    if not num_urls:
        num_urls = len(most_popular.api_urls)
    data = most_popular.fetch_many(num_urls)
    app.article_store.save_articles("nytimes_mostpopular", data, most_popular.config["category_max_articles"])
