import copy
import logging
import re

import requests
import bleach
from furl import furl


logger = logging.getLogger("headliner")


VALID_LINK_PATTERN = re.compile(r"^https?://")
VALID_TEXT_TYPES = set([unicode, str])
VALID_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


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
                "music": ["Music"],
                "television": ["Television"],
                "video-games": ["Video-Games"],
                "__NONE": ["Arts"],
                "__DEFAULT": ["Arts"],
            },
            "__FACET": {
                "weddings and engagements": ["Weddings"],
            },
        },

        "automobiles": {
            "__ALL": ["Autos"],
        },

        "business day": {
            "__ALL": ["Business"],
            "__PATH": {
                "smallbusiness": ["Entrepreneur"],
            },
        },

        "dining & wine": {
            "__ALL": ["Cooking"],
        },

        "education": {
            "__ALL": ["Ideas"],
        },

        "fashion & style": {
            "__ALL": ["Fashion-Men", "Fashion-Women"],
            "__PATH": {
                "weddings": ["Weddings"],
            },
        },

        "health": {
            "__ALL": ["Health-Men", "Health-Women"],
        },

        "home & garden": {
            "__ALL": ["Do-It-Yourself", "Home-Design"],
        },

        "movies": {
            "__ALL": ["Movies"],
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

        "travel": {
            "__ALL": ["Travel"],
        },

        "u.s.": {
            "__PATH": {
                "politics": ["Politics"],
            },
        },

        "your money": {
            "__ALL": ["Business"],
        },
    }

    def __init__(self, config):
        self.__check_config(config)
        self.config = config
        self._url_index = 0
        self.api_urls = self.gen_urls()

    def __check_config(self, config):
        if not config["api_key"]:
            raise ConfigError("An api_key must be provided")

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
        for i in range(num):
            data = self.fetch_one()
            if data:
                output.append(data[0])
        return output

    def extract_categorize(self, article):
        """
        Obtain categorization for a given article, capture data to be stored.
        """
        result = None
        section = article.get("section", "").lower()

        # NB: The article's section can be different from the section url path
        if section in MostPopular.MAPPINGS:
            uri = furl(article["url"])
            for key, val in self.config.get("url_decoration", {}).iteritems():
                uri.args[key] = val

            data = {
                "url": uri.url,
                "title": article["title"],
                "column": article.get("column", ""),
                "media": article["media"],
            }

            labels = set()
            mapping = MostPopular.MAPPINGS[section]

            if "__ALL" in mapping:
                labels.update(mapping["__ALL"])

            if "__KEYWORD" in mapping and "adx_keywords" in article:
                article_keywords = [k.lower() for k in article["adx_keywords"].split(";")]
                for k in article_keywords:
                    if k in mapping["__KEYWORD"]:
                        labels.update(mapping["__KEYWORD"][k])

            if "__FACET" in mapping and "des_facet" in article:
                article_facets = [f.lower() for f in article["des_facet"]]
                for f in article_facets:
                    if f in mapping["__FACET"]:
                        labels.update(mapping["__FACET"][f])

            if "__COLUMN" in mapping and "column" in article:
                col = article["column"].lower()
                if col in mapping["__COLUMN"]:
                    labels.update(mapping["__COLUMN"][col])

            if "__PATH" in mapping:
                path_match = self.WWW_PATH_PATTERN.match(uri.pathstr)
                if path_match:
                    section, sub_section = path_match.groups()
                    if sub_section:
                        # get rid of trailing '/'
                        sub_section = sub_section[:-1]

                    if sub_section is None and "__NONE" in mapping["__PATH"]:
                        labels.update(mapping["__PATH"]["__NONE"])
                    elif sub_section and sub_section in mapping["__PATH"]:
                        labels.update(mapping["__PATH"][sub_section])
                    elif "__DEFAULT" in mapping["__PATH"]:
                        labels.update(mapping["__PATH"]["__DEFAULT"])

            result = {
                "data": data,
                "labels": list(labels),
                "pub_date": article["published_date"]
            }

        cleaned = self.clean_data(result)
        return cleaned

    def extract_data(self, input):
        articles = []
        if input['num_results'] > 0:
            for article in input['results']:
                article_data = self.extract_categorize(article)
                if article_data:
                    articles.append(article_data)
        return articles

    def clean_data(self, article, aggressive=True):
        """
        Strip all html tags and make sure urls start with either http or https
        Expected input is a headliner-formatted article

        If aggressive is set to True, function will return None in case of invalid pub_date or url
        """
        data = None
        if article:
            data = copy.deepcopy(article)
            object_stack = [(data, data.keys())]
            reject = False
            while(len(object_stack) != 0 and not reject):
                item, keys = object_stack.pop()
                for key in keys:
                    val = item[key]
                    if key == "url":
                        if not VALID_LINK_PATTERN.match(item[key]):
                            if aggressive:
                                reject = True
                                break
                            else:
                                item[key] = ""
                    elif key == "pub_date":
                        if not VALID_DATE_PATTERN.match(item["pub_date"]):
                            if aggressive:
                                reject = True
                                break
                            else:
                                item[key] = ""
                    elif type(val) in VALID_TEXT_TYPES:
                        item[key] = bleach.clean(val, strip=True, tags=[])
                    elif type(val) == list:
                        object_stack.append((val, range(len(val))))
                    elif type(val) == dict:
                        object_stack.append((val, val.keys()))
            if reject:
                return None
        return data


class ConfigError(Exception):
    """
    Should be raised if there's a configuration error.
    """
