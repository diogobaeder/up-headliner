#!/usr/bin/env python
import os
import argparse

from up.headliner import http, settings

DEFAULT_CONFIG_FILEPATH = "/etc/up/headliner.json"

parser = argparse.ArgumentParser(description="Headliner is a JSON API that returns personalized content obtained from providers")
parser.add_argument("--host", metavar="host", type=str, help="Hostname to bind to", default=None)
parser.add_argument("--port", metavar="port", type=int, help="Port to bind to", default=None)
parser.add_argument("--debug", metavar="debug", type=bool, help="Turn on debug mode", default=None)
parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)

class SettingsObj(object):
    def __init__(self, **settings):
        self.__dict__.update(settings)

def main():
    """
    Read configuration from multiple places and start an HTTP server.

    Configuration is obtain with the following priority:

    command line > default config path > specified json config > up.headliner.settings
    """
    options = parser.parse_args()

    sys_settings = None
    if os.path.isfile(DEFAULT_CONFIG_FILEPATH) or options.config:
        file_path = DEFAULT_CONFIG_FILEPATH
        if options.config and os.path.isfile(options.config):
            file_path = option.config
        with open(file_path, "r") as config_file:
            config = json.load(config_file)

        if config.get('server', ''):
            sys_settings = SettingsObj(**config.get('headliner'))
            settings.server['host'] = sys_settings.server.get('host', "127.0.0.1")
            settings.server['port'] = sys_settings.server.get('port', 4355)
            settings.server['debug'] = sys_settings.server.get('debug', False)

    if options.host is not None:
        settings.server['host'] = options.host
    if options.port is not None:
        settings.server['port'] = options.port
    if options.debug is not None:
        settings.server['debug'] = options.debug

    http.app.run(**settings.server)

if __name__ == "__main__":
    main()
