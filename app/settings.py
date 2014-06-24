import subprocess
import logging

from rauth import OAuth1Service



APP_NAME = "address-suggestion"

GIT_VERSION = 1

LOG_LEVEL = logging.DEBUG
LOG_FILE = "stdout.log"


DEBUG = True


BOTTLE = {

    "host": "localhost",
    "port": 8064,
    "debug": DEBUG,
    "reloader": DEBUG
}


EDIT_FIELDS = [

    {
        "type": "text",
        "name": "name",
        "label": "name",
        "prefilled": False,
        "allow_empty": True
    },

    {
        "type": "text",
        "name": "addr:street",
        "label": "street",
        "prefilled": True,
        "allow_empty": True
    },
    {
        "type": "text",
        "name": "addr:housenumber",
        "label": "housenumber",
        "prefilled": False,
        "allow_empty": True
    },
    {
        "type": "text",
        "name": "addr:city",
        "label": "city",
        "prefilled": True,
        "allow_empty": True
    },
    {
        "type": "text",
        "name": "addr:postcode",
        "label": "postcode",
        "prefilled": True,
        "allow_empty": True
    },
    {
        "type": "url",
        "name": "website",
        "label": "website",
        "prefilled": False,
        "allow_empty": True
    },
    {
        "type": "phone",
        "name": "phone",
        "label": "phone",
        "prefilled": False,
        "allow_empty": True
    },
    {
        "type": "select",
        "name": "wheelchair",
        "label": "wheelchair",
        "options": [
                {
                    "value": "yes",
                    "label": "yes",
                },
            {
                "value": "no",
                "label": "no",
            },
            {
                "value": "limited",
                "label": "limited",
            }
        ],
        "prefilled": False,
        "allow_empty": True
    },
    {
        "type": "select",
        "name": "building",
        "label": "type",
        "allow_empty": True,
        "options": [
            {
                "value": "house",
                "label": "house",
            },
            {
                "value": "apartments",
                "label": "apartments",
            },
            {
                "value": "commercial",
                "label": "commercial",
            },
            {
                "value": "industrial",
                "label": "industrial",
            },
            {
                "value": "residential",
                "label": "residential",
            },
            {
                "value": "yes",
                "label": "building",
            },
            {
                "value": "cafe",
                "label": "cafe",
            },
            {
                "value": "restaurant",
                "label": "restaurant",
            },
            {
                "value": "terrace",
                "label": "terrace",
            },
            {
                "value": "garage",
                "label": "garage"
            }
        ],
        "prefilled": False
    },



]



DB_CONNECTION = "sqlite:///test.db"

def get_osm_auth():
    return OAuth1Service(
        name='osm',
        consumer_key='',
        consumer_secret='',
        request_token_url='http://www.openstreetmap.org/oauth/request_token',
        access_token_url='http://www.openstreetmap.org/oauth/access_token',
        authorize_url='http://www.openstreetmap.org/oauth/authorize',
        base_url='http://api.openstreetmap.org/api/0.6/')