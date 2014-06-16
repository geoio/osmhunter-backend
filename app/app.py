import logging
import settings

from bottle import route, run, template, Bottle, request, static_file

from helpers.json_serializer import JSONAPIPlugin
from helpers.utils import APIError
from models.OverpassApi import OverpassApi
from models.OsmApiClient import OsmApiClient




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

    """

    latitude =  float(request.query.getunicode("lat"))
    longitude =  float(request.query.getunicode("lon"))
    radius =  request.query.getunicode("radius")


    if not latitude:
        return APIError(body="need param lat")

    if not longitude:
        return APIError(body="need param lon")


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
    return {"status": "OK", "results": results[:limit]}



@app.route('/building/<id>', ['GET'])
def get_building(id: int):
    """GET a building by id
        :Parameters:
        - `id` - the osm id of the building
        - `username` - openstreetmap.org username
        - `password` - openstreetmap.org password
    """

    #TODO(felix): implement a serious authentication like oauth
    api = OsmApiClient(request.query.getunicode("username"), request.query.getunicode("password"))
    return {"status": "OK", "result": api.get_way(id)}
    

@app.route('/building/<id>', ['PUT'])
def update_building(id: int):
    """GET a building by id
        :Parameters:
        - `id` - the osm id of the building
        - `username` - openstreetmap.org username
        - `password` - openstreetmap.org password
        - `data_payload`- the changed way data as payload
    """

    #TODO(felix): implement a serious authentication like oauth
    api = OsmApiClient(request.query.getunicode("username"), request.query.getunicode("password"))
    
    data = request.body.read()

    if not data:
        raise APIError("No data received")

    try:
        request_body = json.loads(data)
    except TypeError:
        raise APIError("Cant parse JSON")

    if type(request_body) is not dict:
        raise APIError("Invalid request")

    return {"status": "OK", "result": api.update_building(id, request_body)}
    





if __name__ == "__main__":
    run(app=app, host=settings.BOTTLE["host"], port=settings.BOTTLE["port"], reloader=settings.BOTTLE["reloader"], debug=settings.BOTTLE["debug"])
