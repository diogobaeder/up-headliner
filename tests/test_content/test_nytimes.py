from furl import furl
from urlparse import urlparse, parse_qs
from nose.tools import assert_equals, assert_is_not_none
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
        assert_equals(result["data"]["url"][len(article["url"]):], "?src=moz-up")

        article = {
                "url": "https://example.com/2013/12/03/all/foo-bar.html?other=args",
                "title": "Foo Bar",
                "media": {},
                "published_date": "2013-12-04",
                "section": "all"
        }
        result = self.most_popular.extract_categorize(article)

        uri = furl(result["data"]["url"])
        assert_equals(uri.query.params["src"], "moz-up")
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
