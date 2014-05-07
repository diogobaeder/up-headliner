import json
import os
from unittest import TestCase

import redis
from nose.tools import istest

from up.headliner.data import ArticleStore
from up.headliner.utils import read_config_file


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
NY_TIMES_DATA = os.path.join(THIS_DIR, 'fixtures', 'nytimes.json')
NY_TIMES_COLLECTION = 'nytimes_mostpopular'


class ArticleStoreTest(TestCase):
    def setUp(self):
        config = read_config_file()
        pool = redis.ConnectionPool(
            host=config.redis["host"],
            port=config.redis["port"],
            db=config.redis["database"],
            password=config.redis["password"],
        )
        self.client = redis.Redis(connection_pool=pool)
        self.store = ArticleStore(pool)

    def tearDown(self):
        self.client.flushdb()

    @istest
    def saves_data_to_the_store(self):
        with open(NY_TIMES_DATA) as f:
            data = json.load(f, encoding='utf-8')

        self.store.save_articles(NY_TIMES_COLLECTION, data)

        articles = self.store.fetch(NY_TIMES_COLLECTION, 'Arts')
        self.assertEqual(len(articles), 2)
        for article in articles:
            if article['title'] == 'Peter Matthiessen, Lyrical Writer and Naturalist, Is Dead at 86':
                break
        else:
            self.fail('The expected article was not found')
        self.assertEqual(article['column'], '')
        self.assertEqual(article['url'], 'http://www.nytimes.com/2014/04/06/books/peter-matthiessen-author-and-naturalist-is-dead-at-86.html?src=recmoz')
        self.assertEqual(article['media'][0]['caption'], 'The author, at his home in Sagaponack, N.Y., in 2008, won the National Book Award in both fiction and nonfiction.')
        self.assertEqual(article['media'][0]['copyright'], 'Gordon M. Grant for The New York Times')
        self.assertEqual(article['media'][0]['subtype'], 'photo')
        self.assertEqual(article['media'][0]['type'], 'image')
        self.assertEqual(article['media'][0]['media-metadata'][0]['format'], 'Standard Thumbnail')
        self.assertEqual(article['media'][0]['media-metadata'][0]['url'], 'http://graphics8.nytimes.com/images/2014/04/06/nyregion/Matthiessen-obit-4/Matthiessen-obit-4-thumbStandard.jpg')
        self.assertEqual(article['media'][0]['media-metadata'][0]['height'], 75)
        self.assertEqual(article['media'][0]['media-metadata'][0]['width'], 75)

    @istest
    def fetches_data_with_limit(self):
        with open(NY_TIMES_DATA) as f:
            data = json.load(f, encoding='utf-8')
        self.store.save_articles(NY_TIMES_COLLECTION, data)

        articles = self.store.fetch(NY_TIMES_COLLECTION, 'Arts', limit=1)

        self.assertEqual(len(articles), 1)

    @istest
    def fetches_data_with_scores(self):
        with open(NY_TIMES_DATA) as f:
            data = json.load(f, encoding='utf-8')
        self.store.save_articles(NY_TIMES_COLLECTION, data)

        articles = self.store.fetch(NY_TIMES_COLLECTION, 'Arts', withscores=True)
        for article in articles:
            if article['title'] == 'Peter Matthiessen, Lyrical Writer and Naturalist, Is Dead at 86':
                break
        else:
            self.fail('The expected article was not found')
        self.assertGreater(article['score'], 0)

    @istest
    def gets_category_counts(self):
        with open(NY_TIMES_DATA) as f:
            data = json.load(f, encoding='utf-8')
        self.store.save_articles(NY_TIMES_COLLECTION, data)

        counts = self.store.get_category_counts(NY_TIMES_COLLECTION)

        self.assertEqual(counts['Arts'], '2')

    @istest
    def clears_all_data(self):
        with open(NY_TIMES_DATA) as f:
            data = json.load(f, encoding='utf-8')
        self.store.save_articles(NY_TIMES_COLLECTION, data)

        self.store.clear_all()

        self.assertEqual(self.store.get_category_counts(NY_TIMES_COLLECTION), {})
