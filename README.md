User Personalization - Headliner
================================

Headliner is a service that serves personalized content obtained from various sources via a JSON API.  
It is meant to both serve as a demo to the forthcoming Firefox UP feature and as an example application service.  

It consists of two parts:
 * An aggregation program that fetches data and stores it locally in a redis database
 * An HTTP JSON API Server

Requirements
------------

External programs required for headliner to work:
 * Redis (2.8.1 used in development, but versions > 2.6 could work too)
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

Configuration
-------------

Configuration is read in a number of ways:

 1. by editing the file at up/headliner/settings.py
 1. as a json file located at /etc/up/headliner.json
 1. as a json file specified on the command-line

The configuration is loaded with the first item in the list with the least priority and the last item the most priority.   

New York Times Most Popular API
-------------------------------

The included content source in this package is obtained from the [New York Times Most Popular API](http://developer.nytimes.com/docs/most_popular_api/).  

To obtain content from this source, you will need to provide your API key as configuration. Please refer to the section above.  

Once you have setup the environment, entered your API key, and have redis up and running, you can populate the data store with articles from nytimes by running the script provided for that purpose:  

    $ ./scripts/populate_nytimes_mostpopular.py

**Warning:** This script will flush the redis database prior to filling it with articles.  

Once the data is populated, the data will be available for consumption via the HTTP webservice. Following is a description of those API endpoints. The code being described can be found at [https://github.com/oyiptong/up-headliner/blob/master/up/headliner/content/nytimes/urls.py](https://github.com/oyiptong/up-headliner/blob/master/up/headliner/content/nytimes/urls.py).  

### Interest Index

    http://127.0.0.1:4355/nytimes/mostpopular.json

This lists the interests available and provides a numeric quantity that tells how many articles fall into these interests.

Example output:

    {
      "d": {
        "Android": 10, 
        "Apple": 10, 
        "Arts": 3, 
        "Autos": 7, 
        "Baseball": 5, 
        "Basketball": 2, 
        "Boxing": 3, 
        "Design": 14, 
        "Football": 6, 
        "Health-Men": 25, 
        "Health-Women": 25, 
        "Ideas": 11, 
        "Movies": 21, 
        "Parenting": 6, 
        "Programming": 30, 
        "Science": 26, 
        "Soccer": 2, 
        "Sports": 34, 
        "Technology": 30, 
        "Travel": 23, 
        "Video-Games": 1
      }
    }

### Article Listing service

    http://127.0.0.1:4355/nytimes/mostpopular/<interest_name>.json

 * This returns a list of articles, ordered by publication date for the given interest name
 * A limit may be specified by a query parameter, "limit" that takes a number
 * The API will return no more than 100 articles

Example output:

    {
      "d": [
        {
          "media": [
            {
              "caption": "The 2014 Mazda 3 flaunts Euro-style curves and intriguing shapes.", 
              "copyright": "Mazda North America", 
              "media-metadata": [
                {
                  "format": "Standard Thumbnail", 
                  "height": 75, 
                  "url": "http://graphics8.nytimes.com/images/2013/12/01/automobiles/SUB-WHEEL1/SUB-WHEEL1-thumbStandard.jpg", 
                  "width": 75
                }, 
                {
                  "format": "thumbLarge", 
                  "height": 150, 
                  "url": "http://graphics8.nytimes.com/images/2013/12/01/automobiles/SUB-WHEEL1/SUB-WHEEL1-thumbLarge.jpg", 
                  "width": 150
                }, 
                {
                  "format": "mediumThreeByTwo210", 
                  "height": 140, 
                  "url": "http://graphics8.nytimes.com/images/2013/12/01/automobiles/SUB-WHEEL1/SUB-WHEEL1-mediumThreeByTwo210.jpg", 
                  "width": 210
                }
              ], 
              "subtype": "photo", 
              "type": "image"
            }
          ], 
          "title": "Performer Available for Private Parties", 
          "url": "http://www.nytimes.com/2013/12/01/automobiles/autoreviews/performer-available-for-private-parties.html?src=moz-up"
        }
      ], 
      "num_articles": 1
    }

### Personalization API

    http://127.0.0.1:4355/nytimes/mostpopular/personalize

This will return a list of articles based on a query, which consists of an object describing interest prefereces.  
 * The query parameter needs to be in JSON and included in the request's body
 * A limit may be specified by a query parameter, "limit" that takes a number 
 * The API will return no more than 100 articles
 * This endpoint is called via a POST with an "application/json" MIME content type

Here is an example query:  

    {"Arts":0.9,"Autos":0.5,"Design":0.3} 

You can find an example API call made using curl at [https://github.com/oyiptong/up-headliner/blob/master/scripts/example_request.sh](https://github.com/oyiptong/up-headliner/blob/master/scripts/example_request.sh)

The scores are between 0 and 1 and the resulting articles are chosen in proportion to other interests.  

With a limit of 20, the API will attempt to return a list of articles as follows:

    import math
    article_limit = 20
    total_weights = 0.9 + 0.5 + 0.3
    num_arts_articles = math.floor(0.9 / total_weights * article_limit)

Which makes the number of Arts articles 10, Autos articles 5 and Design articles 3.  

The API returns results in a best-effort manner. If there are less than 10 Arts articles available, the API will return whatever it has.  

The output contains articles in order of importance from the interests they belong in.  

The output looks the same as the article listing API.  

License
-------

All source code here is available under the [MPL 2.0](https://www.mozilla.org/MPL/2.0/) license, unless otherwise indicated.
