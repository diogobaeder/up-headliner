import os
import argparse
from up.headliner import settings, DEFAULT_CONFIG_FILEPATH

class SettingsObj(object):
    def __init__(self, **settings):
        self.__dict__.update(settings)

def __read_config_file(options):
    # read default config
    config_obj = SettingsObj()
    config_obj.server = settings.server 
    config_obj.redis = settings.redis
    config_obj.providers = settings.providers
    config_obj.message_broker = settings.message_broker

    # load external JSON
    if os.path.isfile(DEFAULT_CONFIG_FILEPATH) or options.config:
        file_path = DEFAULT_CONFIG_FILEPATH
        if options.config and os.path.isfile(options.config):
            file_path = option.config
        with open(file_path, "r") as config_file:
            config = json.load(config_file)

        if config.get('server') and config.get('storage'):
            sys_settings = SettingsObj(**config)
            config_obj.server['host'] = sys_settings.server.get('host', "127.0.0.1")
            config_obj.server['port'] = sys_settings.server.get('port', 4355)
            config_obj.server['debug'] = sys_settings.server.get('debug', False)
            config_obj.redis['host'] = sys_settings.redis.get('host', '127.0.0.1')
            config_obj.redis['port'] = sys_settings.redis.get('port', 6379)
            config_obj.redis['database'] = sys_settings.redis.get('database', 0)
            config_obj.redis['user'] = sys_settings.redis.get('user', None)
            config_obj.redis['password'] = sys_settings.redis.get('password', None)

    return config_obj

def get_http_config():
    """
    Read configuration from multiple places and start an HTTP server.
    Configuration is obtain with the following priority:

    command line > default config path > specified json config > up.headliner.settings
    """

    parser = argparse.ArgumentParser(description="Headliner is a JSON API that returns personalized content obtained from providers")
    parser.add_argument("--host", metavar="host", type=str, help="Hostname to bind to", default=None)
    parser.add_argument("--port", metavar="port", type=int, help="Port to bind to", default=None)
    parser.add_argument("--debug", metavar="debug", type=bool, help="Turn on debug mode", default=None)
    parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)

    options = parser.parse_args()
    config = __read_config_file(options)

    if options.host is not None:
        config.server['host'] = options.host
    if options.port is not None:
        config.server['port'] = options.port
    if options.debug is not None:
        config.server['debug'] = options.debug

    return config

def get_aggregator_config():
    """
    Read configuration from multiple places and start a content aggregator.
    Configuration is obtain with the following priority:

    default config path > specified json config > up.headliner.settings
    """
    parser = argparse.ArgumentParser(description="Headliner Aggregator is a program that fetches content from a number of providers and stores it for later retrieval.")
    parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)
    options = parser.parse_args()
    config = __read_config_file(options)

    return config
