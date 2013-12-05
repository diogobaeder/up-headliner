#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from up.headliner import Application
from up.headliner.utils import get_http_config, setup_basic_logger
setup_basic_logger()
logger = logging.getLogger("headliner")

def main():
    config = get_http_config()
    app = Application.instance(config)
    most_popular = app.providers["nytimes_mostpopular"]

    num_urls = len(most_popular.api_urls)
    logger.info("Populating data store with data with {0} API calls".format(num_urls))

    logger.info("Fetching data")
    data = most_popular.fetch_many(num_urls)

    logger.info("Saving data")
    app.article_store.save_articles("nytimes_mostpopular", data)

if __name__ == "__main__":
    main()
