#!/usr/bin/env python
from up.headliner import Application
from up.headliner.utils import get_http_config
from up.headliner import http

def main():
    config = get_http_config()
    app = Application.instance(config)
    http.app.run(**config.server)

if __name__ == "__main__":
    main()
