from unittest import TestCase

from nose.tools import istest

from up.headliner.http import load_routes, webapp
from up.headliner.utils import read_config_file


class RoutesTest(TestCase):
    def setUp(self):
        self.app = webapp.test_client()
        self.config = read_config_file()

    @istest
    def gets_the_app_status(self):
        response = self.app.get('/status')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'Headliner 0.5 STATUS OK')

    @istest
    def loads_necessary_routes(self):
        self.assertEqual(len(webapp.url_map._rules), 2)  # static, status

        load_routes(self.config.server["routes"])

        self.assertGreater(len(webapp.url_map._rules), 2)
