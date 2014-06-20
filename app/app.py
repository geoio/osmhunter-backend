import logging
import json
import settings

from bottle import route, run, template, Bottle, request, static_file

from classes.FormGenerator import FormGenerator
from helpers.geo_helpers import reverse_geocode
from helpers.json_serializer import JSONAPIPlugin
from helpers.utils import APIError
from models.OsmApiClient import OsmApiClient
from models.OverpassApi import OverpassApi



#Logging stuff
if settings.DEBUG:
    logging.basicConfig(level=settings.LOG_LEVEL)
else:
    logging.basicConfig(filename=settings.LOG_FILE,level=settings.LOG_LEVEL)

logger = logging.getLogger(name=settings.APP_NAME)

logger.info("run %s on version %s" % (settings.APP_NAME, settings.GIT_VERSION))


#application routes
app = Bottle()
app.catchall = False
app.install(JSONAPIPlugin())

overpass = OverpassApi()


@app.route('/')
def show_version():
    """GET version informations"""
    return {"status": "OK", "results": {"version": settings.GIT_VERSION, "debug": settings.DEBUG}}


@app.route('/buildings/')
def get_buildings():
    """GET building in specific bbox
        :Parameters:
        - `north` - bbox 
        - `south` - bbox 
        - `east` - bbox 
        - `west` - bbox 
        - `limit` - max of shapes in this bbox

    """

    bbox = {"north": request.query.getunicode("north"), "south": request.query.getunicode("south"), "east": request.query.getunicode("east"), "west": request.query.getunicode("west")}

    if bbox["north"] and bbox["south"] and bbox["east"] and bbox["west"]:
        pass
    else:
        return APIError(body="need bbox (params north, south, east, west)")

    bbox["north"] = float(bbox["north"])
    bbox["south"] = float(bbox["south"])
    bbox["east"] = float(bbox["east"])
    bbox["west"] = float(bbox["west"])

    limit = request.query.getunicode("limit")

    if limit is None:
        limit = 100
    else:
        limit = int(limit)

    if limit > 999:
        limit = 999



    results = overpass.get_buildings_without_housenumber_bbox(bbox)
    return {"status": "OK", "results": results[:limit]}





@app.route('/buildings/nearby/')
def get_buildings_nearby():
    """GET building in specific bbox
        :Parameters:
        - `lat` - latitude 
        - `lon` - longitude 
        - `radius` - the searchradius in meters
        - `limit` - max of shapes
        - `offset` - offset to skip

    """

    latitude =  request.query.getunicode("lat")
    longitude =  request.query.getunicode("lon")
    radius =  request.query.getunicode("radius")
    offset = request.query.getunicode("offset")


    if not latitude:
        return APIError(body="need param lat")

    if not longitude:
        return APIError(body="need param lon")

    if not offset:
        offset = 0

    offset = int(offset)

    latitude = float(latitude)
    longitude = float(longitude)

    if not radius:
        radius = 300
    else:
        radius = int(radius)

    if radius > 2500:
        radius = 2500

    limit = request.query.getunicode("limit")

    if limit is None:
        limit = 100
    else:
        limit = int(limit)

    if limit > 999:
        limit = 999

    results = overpass.get_buildings_without_housenumber_nearby(latitude, longitude, radius)
    results = results[offset:limit + offset]
    if len(results) < 1:
        return {"status": "ZERO_RESULTS", "results": []}
    else:
        return {"status": "OK", "results": results}



@app.route('/buildings/<id>/', ['GET'])
def get_building(id: int):
    """GET a building by id
        :Parameters:
        - `id` - the osm id of the building
    """

    way = overpass.get_by_osm_id(id)
    return {"status": "OK", "result": way }


@app.route('/buildings/<id>/edit-form/', ['GET'])
def get_building_form(id: int):
    """GET the edit form for a building
        :Parameters:
        - `id` - the osm id of the building
    """
    
    way = overpass.get_by_osm_id(id)
    form = FormGenerator(settings.EDIT_FIELDS, way)
    
    return {"status": "OK", "result": form.generate()}
    

@app.route('/buildings/<id>/', ['PUT'])
def update_building(id: int):
    """GET a building by id
        :Parameters:
        - `id` - the osm id of the building
        - `username` - openstreetmap.org username
        - `password` - openstreetmap.org password
        - `data_payload`- the changed way data as payload
    """

    #TODO(felix): implement a serious authentication like oauth
    username = request.query.getunicode("username")
    password = request.query.getunicode("password")

    if not username or not password:
        return APIError(body="Need params username and password")

    api = OsmApiClient(username, password)

    way = overpass.get_by_osm_id(id)
    
    data = request.body.read().decode("utf-8")

    if not data:
        raise APIError("No data received")

    try:
        request_body = json.loads(data)
    except TypeError:
        raise APIError("Cant parse JSON")

    if type(request_body) is not dict:
        raise APIError("Invalid request")


    try:
        result = api.update_way(id, request_body)
    except e:
        raise APIError("Unknown error while saving: %s" % e.message) 


    return {"status": "OK", "result": result}


@app.route('/reverse-geocode/')
def reverse_geocode_api():
    """Reverse Geocode a shape, to prefill fields like street and city
        :Parameters:
            - `lat` - Latitude
            - `lon` - Longitude
    """
    latitude =  request.query.getunicode("lat")
    longitude =  request.query.getunicode("lon")
    if not latitude:
        return APIError(body="need param lat")

    if not longitude:
        return APIError(body="need param lon")
    latitude = float(latitude)
    longitude = float(longitude)
    return {"status": "OK", "result": reverse_geocode(latitude, longitude)}
    





if __name__ == "__main__":
    run(app=app, host=settings.BOTTLE["host"], port=settings.BOTTLE["port"], reloader=settings.BOTTLE["reloader"], debug=settings.BOTTLE["debug"])
