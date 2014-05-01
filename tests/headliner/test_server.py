from unittest import TestCase

from mock import patch
from nose.tools import istest

from up.headliner import Application
from up.headliner.server import main


class MainTest(TestCase):
    @istest
    @patch('up.headliner.server.http')
    @patch('up.headliner.server.get_http_config')
    def instantiates_application_with_config(self, get_http_config, http):
        if hasattr(Application, '_instance'):
            del Application._instance

        main()

        self.assertIsNotNone(Application._instance)
        self.assertEqual(Application._instance.config, get_http_config.return_value)
