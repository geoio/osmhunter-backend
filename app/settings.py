import subprocess
import logging


APP_NAME = "address-suggestion"

GIT_VERSION = 1

LOG_LEVEL = logging.DEBUG
LOG_FILE = "stdout.log"


DEBUG = True


BOTTLE = {

    "host": "localhost",
    "port": 8060,
    "debug": DEBUG,
    "reloader": DEBUG
}


EDIT_FIELDS = [

	{
		"type": "text",
		"name": "name",
		"label": "name",
		"prefilled": False
	},

	{
		"type": "text",
		"name": "addr:street",
		"label": "street",
		"prefilled": True
	},
	{
		"type": "text",
		"name": "addr:housenumber",
		"label": "housenumber",
		"prefilled": False
	},	
	{
		"type": "text",
		"name": "addr:city",
		"label": "city",
		"prefilled": True
	},
	{
		"type": "text",
		"name": "addr:postcode",
		"label": "postcode",
		"prefilled": True
	},
	{
		"type": "url",
		"name": "website",
		"label": "website",
		"prefilled": False
	},
	{
		"type": "phone",
		"name": "phone",
		"label": "phone",
		"prefilled": False
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
		"prefilled": False
	},
	{
		"type": "select",
		"name": "building",
		"label": "type",
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
				"label": "yes",
			},
			{
				"value": "cafe",
				"label": "cafe",
			},
			{
				"value": "restaurant",
				"label": "restaurant",
			}
		],
		"prefilled": False
	},



]
