from furl import furl
from urlparse import urlparse, parse_qs
from nose.tools import assert_equals, assert_is_not_none, assert_not_equals
from up.headliner.content.nytimes.api import MostPopular

class TestMostPopular:
    @classmethod
    def setup_class(cls):
        MostPopular.SECTIONS = ["all", "multiple"]
        MostPopular.POPULARITY = ["mostviewed", "mostshared", "mostemailed"]

        MostPopular.MAPPINGS = {
                "all": {
                    "__ALL": ["All-Under-Section"],
                    "__PATH": {
                        "sub-path": ["Sub-Path-Sensitive"],
                    },
                    "__KEYWORD": {
                        "keyword": ["Keyword-Matched"],
                    },
                    "__COLUMN": {
                        "columned": ["Column-Matched"],
                    },
                    "__FACET": {
                        "faceted": ["Facet-Matched"],
                    },
                },
                "multiple": {
                    "__ALL": ["Interest-One", "Interest-Two"],
                    "__PATH": {
                        "interests": ["Interest-Three"],
                    },
                },
                "none": {
                    "__PATH": {
                        "__NONE": ["No-Subsection"]
                    },
                }
        }

    def setup(self):
        self.config = {
                "api_url": "http://example.com/svc/mostpopular/v2/{popularity_type}/{section}/30.json?api-key={api_key}",
                "api_key": "test_key",
                "url_decoration": {
                    "src": "recmoz",
                }
        }
        self.most_popular = MostPopular(self.config)

    def test_init(self):
        """
        Sanity check that all things that should be there are there at init time
        """
        assert_equals(self.most_popular._url_index, 0)
        assert_is_not_none(self.most_popular.api_urls)

    def test_gen_urls(self):
        """
        Test urls generated are all there and are well formed
        """
        expected_num_urls = len(MostPopular.SECTIONS) * len(MostPopular.POPULARITY)
        generated_urls = self.most_popular.gen_urls()
        assert_equals(len(generated_urls), expected_num_urls)
        for url in generated_urls:
            uri = urlparse(url)
            qs = parse_qs(uri.query)
            assert_equals(qs.get("api-key")[0], "test_key")

    def test_next_url(self):
        """
        Test that next_url will wrap around after finishing the set of URL's in order
        """
        assert_equals(self.most_popular._url_index, 0)
        urls = self.most_popular.api_urls

        index = 0
        while index < len(urls):
            assert_equals(self.most_popular._url_index, index)
            assert_equals(self.most_popular.next_url(), urls[index])
            index += 1

        assert_equals(self.most_popular._url_index, 0)
        assert_equals(self.most_popular.next_url(), urls[0])

    def test_next_urls(self):
        """
        Test the next_urls wrapper functions as expected: just a bunch of next_url calls
        """
        # do a full wrap-around
        num_urls = len(MostPopular.SECTIONS) * len(MostPopular.POPULARITY)

        assert_equals(self.most_popular._url_index, 0)
        urls = self.most_popular.next_urls(num_urls)
        assert_equals(self.most_popular._url_index, 0)

        assert_equals(len(urls), num_urls)
        assert_equals(urls, self.most_popular.api_urls)

        # off by one wrap-around, causing the result to wrap around in the resulting list
        _ = self.most_popular.next_url()

        assert_equals(self.most_popular._url_index, 1)
        urls = self.most_popular.next_urls(num_urls)
        assert_equals(self.most_popular._url_index, 1)

        assert_equals(urls[0], self.most_popular.api_urls[1])
        assert_equals(urls[-1], self.most_popular.api_urls[0])

    def test_extract_categorize_keys(self):
        article = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all"
        }
        result = self.most_popular.extract_categorize(article)
        assert_equals(set(result), set(["data", "labels", "pub_date"]))
        assert_equals(set(result["data"]), set(["url", "title", "column", "media"]))

    def test_extract_categorize_src(self):
        article = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all"
        }
        result = self.most_popular.extract_categorize(article)
        assert_equals(result["data"]["url"][0:len(article["url"])], article["url"])
        assert_equals(result["data"]["url"][len(article["url"]):], "?src=recmoz")

        article = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html?other=args",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all"
        }
        result = self.most_popular.extract_categorize(article)

        uri = furl(result["data"]["url"])
        assert_equals(uri.query.params["src"], "recmoz")
        assert_equals(uri.query.params["other"], "args")
        assert_equals(len(uri.query.params), 2)
        assert_equals(result["data"]["url"][0:len(article["url"])], article["url"])

    def test_extract_categorize_labels(self):
        """
        Test categorization
        """
        # section-only categorization
        section_only = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all",
        }
        result = self.most_popular.extract_categorize(section_only)
        assert_equals(result["labels"], ["All-Under-Section"])
 
        multiple = {
                "url": "https://example.com/2013/12/03/multiple/interests/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "multiple",
        }
        result = self.most_popular.extract_categorize(multiple)
        assert_equals(set(result["labels"]), set(["Interest-One", "Interest-Two", "Interest-Three"]))

        path = {
                "url": "https://example.com/2013/12/03/all/sub-path/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all",
        }
        result = self.most_popular.extract_categorize(path)
        assert_equals(set(result["labels"]), set(["All-Under-Section", "Sub-Path-Sensitive"]))

        keyword = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all",
                "adx_keywords": "foo;bar;keyword;baz",
        }
        result = self.most_popular.extract_categorize(keyword)
        assert_equals(set(result["labels"]), set(["All-Under-Section", "Keyword-Matched"]))
 
        facet = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all",
                "des_facet": ["FACETED"],
        }
        result = self.most_popular.extract_categorize(facet)
        assert_equals(set(result["labels"]), set(["All-Under-Section", "Facet-Matched"]))
 
        column = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all",
                "column": "columned"
        }
        result = self.most_popular.extract_categorize(column)
        assert_equals(set(result["labels"]), set(["All-Under-Section", "Column-Matched"]))

        none = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "none",
        }
        result = self.most_popular.extract_categorize(none)
        assert_equals(set(result["labels"]), set(["No-Subsection"]))

        none_2 = {
                "url": "https://example.com/2013/12/03/all/sub-path/foo-bar.html",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "none",
        }
        result = self.most_popular.extract_categorize(none_2)
        assert_equals(set(result["labels"]), set([]))

    def test_clean_data_mixed_types(self):
        sample = {
            "data": {
                "url": "http://www.nytimes.com/2010/08/31/science/31bedbug.html",
                "column": "",
                "title": "They Crawl, They Bite, They Baffle Scientists",
                "media": [
                    {
                        "subtype": "photo",
                        "caption": "THE ICK FACTOR  The lab of Stephen A. Kells, a University of Minnesota entomologist. Bedbugs are not known to transmit disease.",
                        "media-metadata": [
                            {
                                "url": "http://graphics8.nytimes.com/images/2010/08/31/science/31bedbug/31bedbugspan-thumbStandard.jpg",
                                "width": 75,
                                "format": "Standard Thumbnail",
                                "height": 75
                            }
                        ],
                        "copyright": "Allen Brisson-Smith for The New York Times",
                        "type": "image"
                    },
                    {
                        "subtype": "photo",
                        "caption": "LITTLE RESEARCH  Stephen A. Kells is one of the few specializing in bedbugs.",
                        "media-metadata": [
                            {
                                "url": "http://graphics8.nytimes.com/images/2010/08/31/science/31bedbug2/31bedbug2-thumbStandard.jpg",
                                "width": 75,
                                "format": "Standard Thumbnail",
                                "height": 75
                            }
                        ],
                        "copyright": "Allen Brisson-Smith for The New York Times",
                        "type": "image"
                    }
                ]
            },
            "labels": [
                "Science"
            ],
            "pub_date": "2010-08-31"
        }

        # complex objects
        cleaned = self.most_popular.clean_data(sample)
        assert_equals(cleaned, sample)

    def test_clean_data_content_stripping(self):
        # html, url and date stripping
        data = {
                "data": "<script>hello</script>",
                "url": "javascript:alert('invalid')",
                "pub_date": "invalid",
                "nested": {
                    "url": "http://totallyvalid.com",
                    "data1": "<b>strong</b>",
                    "pub_date": "2014-01-01",
                    "data2": [
                        "<em>emphasis</em>",
                        {
                            "data3": "<span>span</span>",
                            "url": "javascript:alert('invalid')",
                        }
                    ]
                }
        }
        cleaned = self.most_popular.clean_data(data, aggressive=False)
        assert_not_equals(cleaned, data)
        assert_equals(cleaned["data"], "hello")
        assert_equals(cleaned["url"], "")
        assert_equals(cleaned["pub_date"], "")
        assert_equals(cleaned["nested"]["data1"], "strong")
        assert_equals(cleaned["nested"]["pub_date"], "2014-01-01")
        assert_equals(cleaned["nested"]["url"], "http://totallyvalid.com")
        assert_equals(cleaned["nested"]["data2"][0], "emphasis")
        assert_equals(cleaned["nested"]["data2"][1]["data3"], "span")
        assert_equals(cleaned["nested"]["data2"][1]["url"], "")

    def test_clean_data_aggressive(self):
        data = {
                "url": "javascript:alert('invalid')",
        }
        cleaned = self.most_popular.clean_data(data, aggressive=True)
        assert_equals(cleaned, None)

        data = {
                "pub_date": "invalid",
        }

        cleaned = self.most_popular.clean_data(data, aggressive=True)
        assert_equals(cleaned, None)
