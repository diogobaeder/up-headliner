#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging

from up.headliner import Application
from up.headliner.utils import read_config_file, setup_basic_logger


setup_basic_logger()
logger = logging.getLogger("headliner")


def get_periodic_shell_config():
    """
    Read configuration, then start a task that is periodic
    """
    parser = argparse.ArgumentParser(description="This will populate the datastore with articles")
    parser.add_argument("--purge", action="store_true", help="Purge the datastore before populating", default=False)
    parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)
    options = parser.parse_args()
    config = read_config_file(options)

    config.server["purge"] = options.purge

    return config


def main():
    config = get_periodic_shell_config()
    app = Application.instance(config)
    most_popular = app.providers["nytimes_mostpopular"]

    num_urls = len(most_popular.api_urls)
    logger.info("Populating data store with data with {0} API calls".format(num_urls))

    logger.info("Fetching data")
    data = most_popular.fetch_many(num_urls)

    if config.server["purge"]:
        logger.info("Clearing the datastore")
        app.article_store.clear_all()

    logger.info("Saving data")
    app.article_store.save_articles("nytimes_mostpopular", data)


if __name__ == "__main__":
    main()
