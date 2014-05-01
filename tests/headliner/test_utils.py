from unittest import TestCase

from nose.tools import istest

from up.headliner.utils import SettingsObj


class SettingsTest(TestCase):
    @istest
    def updates_first_level_as_attributes(self):
        obj = SettingsObj(foo="Foo")

        obj.update(bar="Bar")

        self.assertEqual(obj.foo, "Foo")
        self.assertEqual(obj.bar, "Bar")

    @istest
    def updates_second_level_as_dict(self):
        obj = SettingsObj()

        obj.update(foo={
            'bar': 'Bar',
        })

        self.assertEqual(obj.foo['bar'], 'Bar')

    @istest
    def replaces_deep_elements_if_new(self):
        obj = SettingsObj(foo={
            'bar': {
                'baz': 'baz',
            },
        })

        obj.update(foo={
            'bar': {
                'baz': 'BAZ',
            },
        })

        self.assertEqual(obj.foo['bar']['baz'], 'BAZ')

    @istest
    def merges_deep_elements(self):
        obj = SettingsObj(foo={
            'bar': {
                'baz1': 'baz1',
            },
        })

        obj.update(foo={
            'bar': {
                'baz2': 'baz2',
            },
        })

        self.assertEqual(obj.foo['bar']['baz1'], 'baz1')
        self.assertEqual(obj.foo['bar']['baz2'], 'baz2')

    @istest
    def replaces_deep_elements_if_initial_is_not_a_dict(self):
        obj = SettingsObj(foo={
            'bar': 123,
        })

        obj.update(foo={
            'bar': {
                'baz': 'BAZ',
            },
        })

        self.assertEqual(obj.foo['bar']['baz'], 'BAZ')

    @istest
    def replaces_deep_elements_if_final_is_not_a_dict(self):
        obj = SettingsObj(foo={
            'bar': {
                'baz1': 'baz1',
            },
        })

        obj.update(foo={
            'bar': 123,
        })

        self.assertEqual(obj.foo['bar'], 123)
