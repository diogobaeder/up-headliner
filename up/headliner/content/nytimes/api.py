import re
import logging
from furl import furl
import requests
import grequests
logger = logging.getLogger("headliner")


class MostPopular(object):
    NUM_CONCURRENT = 1
    SECTIONS = ["arts", "automobiles", "business", "dining", "education", "fashion", "garden", "health", "movies", "music", "politics", "science", "sports", "style", "technology", "television", "travel", "your-money"]

    POPULARITY = ["mostviewed", "mostshared", "mostemailed"]

    WWW_PATH_PATTERN = re.compile(r"/[0-9]{4}/[0-9]{2}/[0-9]{2}/([a-z-]+)/([a-z-]+/)?[a-z0-9-]+\.html")
    BLOG_PATH_PATTERN = re.compile(r"/[0-9]{4}/")

    MAPPINGS = {
            "arts": {
                "__PATH": {
                    "design": ["Design"],
                    "video-games": ["Video-Games"],
                    "__NONE": ["Arts"],
                },
                "__FACET": {
                    "weddings and engagements": ["Weddings"],
                },
            },

            "automobiles": {
                "__ALL": ["Autos"],
            },

            "business": {
                "__ALL": ["Business"],
                "__PATH": {
                    "smallbusiness": ["Entrepreneur"],
                },
            },

            "dining": {
                "__ALL": ["Cooking"],
            },

            "education": {
                "__ALL": ["Ideas"],
            },

            "fashion": {
                "__ALL": ["Fashion-Men", "Fashion-Women"],
                "__PATH": {
                    "weddings": ["Weddings"],
                },
            },

            "garden": {
                "__ALL": ["Do-It-Yourself", "Home-Design"],
            },

            "health": {
                "__ALL": ["Health-Men", "Health-Women"],
            },

            "movies": {
                "__ALL": ["Movies"],
            },

            "music": {
                "__ALL": ["Music"],
            },

            "politics": {
                "__ALL": ["Politics"],
            },

            "science": {
                "__ALL": ["Science"],
            },

            "sports": {
                "__ALL": ["Sports"],
                "__PATH": {
                    "baseball": ["Baseball"],
                    "basketball": ["Basketball"],
                    "football": ["Football"],
                    "golf": ["Golf"],
                    "hockey": ["Hockey"],
                    "soccer": ["Soccer"],
                    "tennis": ["Tennis"],
                },
                "__KEYWORD": {
                    "boxing": ["Boxing"],
                },
                "__COLUMN": {
                    "On Boxing": ["Boxing"],
                },
            },

            "style": {
                "__KEYWORD": {
                    "parenting": ["Parenting"]
                },
                "__FACET": {
                    "parenting": ["Parenting"]
                },
            },

            "technology": {
                "__ALL": ["Programming", "Technology"],
                "__PATH": {
                    "personaltech": ["Android", "Apple"],
                },
                "__FACET": {
                    "computer and video games": ["Video-Games"]
                },
            },

            "television": {
                "__ALL" : ["Television"],
            },

            "travel": {
                "__ALL": ["Travel"],
            },

            "your-money": {
                "__ALL": ["Business"],
            },
    }

    def __init__(self, config):
        self.config = config
        self._url_index = 0
        self.api_urls = self.gen_urls()

    def gen_urls(self):
        """
        Generates API URLS to be called by a class instance
        """
        urls = []
        for pop in MostPopular.POPULARITY:
            for section in MostPopular.SECTIONS:
                urls.append(self.config["api_url"].format(
                    popularity_type=pop,
                    section=section,
                    api_key=self.config["api_key"],
                ))
        return urls

    def next_url(self):
        output = self.api_urls[self._url_index]

        next_index = self._url_index + 1
        self._url_index = 0 if next_index >= len(self.api_urls) else next_index

        return output

    def next_urls(self, num=5):
        urls = []
        for i in range(num):
            urls.append(self.next_url())
        return urls

    def fetch_one(self):
        result_set = None
        url = self.next_url()
        req = requests.get(url)

        if req.status_code == 200:
            result_set = req.json()
        else:
            logger.warn("request_failed status_code:{0} reason:{1} url:{2}".format(req.status_code, req.reason, req.url))
        if result_set:
            return self.extract_data(result_set)
        return None

    def fetch_many(self, num):
        output = []
        urls = self.next_urls(num)
        rs = [grequests.get(u) for u in urls]
        responses = grequests.map(rs, size=self.NUM_CONCURRENT)

        result_groups = []
        for resp in responses:
            if resp.status_code == 200:
                result_groups.append(resp.json())
            else:
                logger.warn("request_failed status_code:{0} reason:{1} url:{2}".format(resp.status_code, resp.reason, resp.url))

        for result_set in result_groups:
            output.extend(self.extract_data(result_set))
        return output

    def extract_categorize(self, article):
        """
        Obtain categorization for a given article, capture data to be stored.
        """
        output = None
        section = article.get("section", "").lower()

        if MostPopular.MAPPINGS.has_key(section):
            uri = furl(article["url"])
            uri.query.add({"src": "moz-up"})

            data = {
                    "url": uri.url,
                    "title": article["title"],
                    "column": article.get("column", ""),
                    "media": article["media"],
            }

            labels = set()
            mapping = MostPopular.MAPPINGS[section]

            if mapping.has_key("__ALL"):
                labels.update(mapping["__ALL"])

            if mapping.has_key("__KEYWORD") and article.has_key("adx_keywords"):
                article_keywords = [k.lower() for k in article["adx_keywords"].split(";")]
                for k in article_keywords:
                    if mapping["__KEYWORD"].has_key(k):
                        labels.update(mapping["__KEYWORD"][k])

            if mapping.has_key("__FACET") and article.has_key("des_facet"):
                article_facets = [f.lower() for f in article["des_facet"]]
                for f in article_facets:
                    if mapping["__FACET"].has_key(f):
                        labels.update(mapping["__FACET"][f])

            if mapping.has_key("__COLUMN") and article.has_key("column"):
                col = article["column"].lower()
                if mapping["__COLUMN"].has_key(col):
                    labels.update(mapping["__COLUMN"][col])

            if mapping.has_key("__PATH"):
                path_match = self.WWW_PATH_PATTERN.match(uri.pathstr)
                if path_match:
                    section, sub_section = path_match.groups()
                    if sub_section:
                        # get rid of trailing '/'
                        sub_section = sub_section[:-1]

                    if sub_section is None and mapping["__PATH"].has_key("__NONE"):
                        labels.update(mapping["__PATH"]["__NONE"])
                    elif sub_section and mapping["__PATH"].has_key(sub_section):
                        labels.update(mapping["__PATH"][sub_section])

            output = {
                    "data": data,
                    "labels": list(labels),
                    "pub_date": article["published_date"]
            }

        return output

    def extract_data(self, input):
        articles = []
        if input['num_results'] > 0:
            for article in input['results']:
                article_data = self.extract_categorize(article)
                if article_data:
                    articles.append(article_data)
        return articles
