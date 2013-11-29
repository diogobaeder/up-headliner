User Personalization - Headliner
================================

Headliner is a service that serves personalized content obtained from various sources via a JSON API.  
It is meant to both serve as a demo to the forthcoming Firefox UP feature and as an example application service.  

It consists of two parts:
 * An aggregation program that fetches data and stores it locally
 * An HTTP JSON API Server

Requirements
------------

External programs required for headliner to work:
 * Redis (2.8.1 used in development, but earlier versions could work too)
 * Python 2.7
 * virtualenv, setuptools

The rest of the dependencies will be installed by an included setup process.  

This program has only been run on Mac OS X and Linux.  

Development Setup
-----------------

You can setup a development environment by running the provided setup script:

    $ ./setup-project.sh

Before you can run the HTTP server, you will have to activate the environment, by running the command:

    $ . ./up-headliner-env/bin/activate

You can then read about options about running the server by typing:

    $ ./scripts/up-headliner-server --help

Or run the above line without the argument to start an http server with the default configuration.

License
-------

All source code here is available under the [MPL 2.0](https://www.mozilla.org/MPL/2.0/) license, unless otherwise indicated.
