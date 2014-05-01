from unittest import TestCase

from mock import patch, MagicMock
from nose.tools import istest

from up.headliner import Application
from up.headliner.server import main


class MainTest(TestCase):
    @istest
    @patch('up.headliner.server.http')
    @patch('up.headliner.server.get_http_config')
    def instantiates_application_with_config(self, get_http_config, http):
        Application._instance = None

        main()

        self.assertIsNotNone(Application._instance)
        self.assertEqual(Application._instance.config, get_http_config.return_value)


class ApplicationTest(TestCase):
    @istest
    def returns_same_instance_if_config_not_provided(self):
        Application._instance = None

        config = MagicMock()
        inst1 = Application.instance(config)
        inst2 = Application.instance()

        self.assertEqual(inst1, inst2)

    @istest
    def returns_new_instance_if_config_provided(self):
        Application._instance = None

        config = MagicMock()
        inst1 = Application.instance(config)
        inst2 = Application.instance(config)

        self.assertNotEqual(inst1, inst2)
