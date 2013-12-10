#!/usr/bin/env python
import argparse
from up.headliner import Application
from up.headliner.utils import __read_config_file
from up.headliner import http

def get_http_config():
    """
    Read configuration from multiple places and start an HTTP server.
    Configuration is obtain with the following priority:

    command line > default config path > specified json config > up.headliner.settings
    """

    parser = argparse.ArgumentParser(description="Headliner is a JSON API that returns personalized content obtained from providers")
    parser.add_argument("--host", metavar="host", type=str, help="Hostname to bind to", default=None)
    parser.add_argument("--port", metavar="port", type=int, help="Port to bind to", default=None)
    parser.add_argument("--no-debug", action="store_true", help="Turn off debug mode", default=False)
    parser.add_argument("--config", metavar="config", type=str, help="Specify a json configuration file", default=None)

    options = parser.parse_args()
    config = __read_config_file(options)

    if options.host is not None:
        config.server['host'] = options.host
    if options.port is not None:
        config.server['port'] = options.port
    if options.no_debug is not None:
        config.server['debug'] = not options.no_debug

    return config

def main():
    config = get_http_config()
    app = Application.instance(config)
    http.load_routes(config.server["routes"])
    http.webapp.run(**config.server["http"])

if __name__ == "__main__":
    main()
