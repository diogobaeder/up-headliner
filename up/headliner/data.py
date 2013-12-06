import json
from calendar import timegm
import logging
import dateutil.parser as du_parser
from redis import Redis
from up.headliner.backend.scripts import lua_scripts
logger = logging.getLogger("headliner")

TAXONOMY = ["Android", "Apple", "Arts", "Autos", "Baseball", "Basketball", "Boxing", "Business", "Cooking", "Design", "Do-It-Yourself", "Entrepreneur", "Fashion-Men", "Fashion-Women", "Football", "Gardening", "Golf", "Gossip", "Health-Men", "Health-Women", "Hockey", "Home-Design", "Humor", "Ideas", "Mixed-Martial-Arts", "Movies", "Music", "Parenting", "Photography", "Politics", "Programming", "Science", "Soccer", "Sports", "Technology", "Television", "Tennis", "Travel", "Video-Games", "Weddings"],

class ArticleStore(object):

    def __init__(self, pool):
        self._pool = pool
        self.scripts = lua_scripts()
        redis = Redis()
        for name, script in self.scripts.iteritems():
            setattr(self, "_{0}".format(name), redis.register_script(script))

    def _get_connection(self):
        return Redis(connection_pool=self._pool)

    def save_articles(self, collection, data):
        """
        Save articles for later retrieval.
        Articles are stored in a sorted set, ordered by publication date
        """
        persisted = []
        for article in data:
            pub_date = du_parser.parse(article["pub_date"]).date()
            for category in article["labels"]:
                label = "{0}.{1}".format(collection, category)
                item = {
                        "collection": collection,
                        "category": category,
                        "member": article["data"],
                        "score": timegm(pub_date.timetuple()),
                }
                persisted.append(item)

        if persisted:
            conn = self._get_connection()
            num_added = self._articlestore_save_articles(keys=["articles"], args=[json.dumps(persisted)], client=conn)
            # the number of articles sent may not match the one added
            # as duplicates and article updates are not persisted
            logger.info("redis articles_sent:{0} articles_added:{1}".format(len(persisted), num_added))

    def fetch(self, collection, category, limit=None):
        """
        Obtain a set of articles given a collection and a category
        """
        conn = self._get_connection()
        key = "sorted.{0}.{1}".format(collection, category)
        args = {
                "name": key,
                "max": "+inf",
                "min": "-inf",
        }
        if limit:
            args["start"] = 0
            args["num"] = limit
        data = conn.zrevrangebyscore(**args)
        output = [json.loads(d) for d in data]
        return output

    def get_category_counts(self, collection):
        """
        Obtain a category list with the counts of articles given a collection name
        """
        conn = self._get_connection()
        data = conn.hgetall("counts.{0}".format(collection))
        return data

    def clear_all(self):
        conn = self._get_connection()
        conn.flushdb()
