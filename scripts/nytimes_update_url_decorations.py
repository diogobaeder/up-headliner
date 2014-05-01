#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import re

from furl import furl
from redis import Redis

from up.headliner import Application
from up.headliner.utils import __read_config_file, setup_basic_logger


setup_basic_logger()
logger = logging.getLogger("headliner")
LABEL_PATTERN = re.compile(r"^sorted\.(.+)\.(.+)$")


def get_periodic_shell_config():
    """
    Read configuration, then start a task that is periodic
    """
    parser = argparse.ArgumentParser(description="This will populate the datastore with articles")
    parser.add_argument("--purge", action="store_true", help="Purge the datastore before populating", default=False)
    parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)
    options = parser.parse_args()
    config = __read_config_file(options)

    config.server["purge"] = options.purge

    return config


def main():
    num_changes = 0
    num_articles = 0
    num_dupes_removed = 0

    config = get_periodic_shell_config()
    app = Application.instance(config)
    most_popular = app.providers["nytimes_mostpopular"]

    redis = Redis(connection_pool=app._redis_pool)
    sorted_sets = redis.keys("sorted*")
    sorted_sets.sort()
    for sorted_name in sorted_sets:
        collection, category = LABEL_PATTERN.match(sorted_name).groups()
        label = ".".join([collection, category])

        logger.info("Making changes for: {0}".format(label))

        data = redis.zrange(sorted_name, 0, -1, withscores=True)

        old_url = None
        new_url = None
        for article_json, score in data:
            num_articles += 1
            article = json.loads(article_json)
            old_url = article["url"]

            uri = furl(old_url)
            for key, val in most_popular.config.get("url_decoration", {}).iteritems():
                uri.args[key] = val
            new_url = uri.url

            if new_url != old_url:
                num_changes += 1
                article_json = article_json.decode("utf8")
                new_article_json = article_json.replace(old_url.replace("/", "\\/"), new_url.replace("/", "\\/"))

                # persist change in sorted set
                redis.zrem(sorted_name, article_json)
                redis.zadd(sorted_name, new_article_json, score)

                # persis change in set
                set_name = "set.{0}".format(label)
                redis.srem(set_name, old_url)
                redis.sadd(set_name, new_url)

                sorted_num = redis.zcard(sorted_name)
                set_num = redis.scard(set_name)
                count = int(redis.hget(".".join(["counts", collection]), category))

                if (set_num != sorted_num):
                    logger.warn("set/sortedset mismatch: set:{0} sorted:{1}".format(set_num, sorted_num))

                if set_num != count:
                    num_dupes_removed += abs(count - set_num)
                    redis.hset(collection, category, set_num)

    logger.info("num article changes: {0}/{1}".format(num_changes, num_articles))
    logger.info("num dupes removed: {0}".format(num_dupes_removed))


if __name__ == "__main__":
    main()
