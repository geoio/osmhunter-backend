from datetime import datetime
import json
import logging
import settings
import uuid

from bottle import route, run, template, Bottle, request, static_file
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.sql import func

from classes.FormGenerator import FormGenerator
from helpers.geo_helpers import reverse_geocode
from helpers.json_serializer import JSONAPIPlugin
from helpers.utils import APIError, with_db_session, generate_apikey, StripPathMiddleware
from classes.OsmApiClient import OsmApiClient
from classes.OverpassApi import OverpassApi
from classes.Database import Base as database, OAuthCache, User, Points

# Logging stuff
if settings.DEBUG:
    logging.basicConfig(level=settings.LOG_LEVEL)
else:
    logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL)

logger = logging.getLogger(name=settings.APP_NAME)

logger.info("run %s on version %s" % (settings.APP_NAME, settings.GIT_VERSION))


# application routes
app = Bottle()
app.catchall = False
app.install(JSONAPIPlugin())


sqlalchemy_engine = sqlalchemy.create_engine(settings.DB_CONNECTION, echo=settings.DEBUG)
database.metadata.create_all(sqlalchemy_engine)
PgSession = sqlalchemy.orm.sessionmaker(bind=sqlalchemy_engine)


overpass = OverpassApi()


@app.route('/')
def show_version():
    """GET version informations"""
    return {"status": "OK", "results": {"version": settings.GIT_VERSION, "debug": settings.DEBUG}}


@app.route('/buildings')
def get_buildings():
    """GET building in specific bbox
        :Parameters:
        - `north` - bbox 
        - `south` - bbox 
        - `east` - bbox 
        - `west` - bbox 
        - `lat` - latitude - user position (if not center of bunding box)
        - `lon` - longitude - user position (if not center of bunding box)
        - `limit` - max of shapes in this bbox

    """

    bbox = {"north": request.query.getunicode("north"), "south": request.query.getunicode(
        "south"), "east": request.query.getunicode("east"), "west": request.query.getunicode("west")}

    if bbox["north"] and bbox["south"] and bbox["east"] and bbox["west"]:
        pass
    else:
        return APIError(body="need bbox (params north, south, east, west)")

    user_location["lat"] = request.query.getunicode("lat")
    user_location["lon"] = request.query.getunicode("lon")

    if user_location["lat"] and user_location["lon"]:
        user_location["lat"] = float(user_location["lat"])
        user_location["lon"] = float(user_location["lon"])

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

    results = overpass.get_buildings_without_housenumber_bbox(bbox, user_location=user_location)
    return {"status": "OK", "results": results[:limit]}


@app.route('/buildings/nearby')
def get_buildings_nearby():
    """GET building in specific bbox
        :Parameters:
        - `lat` - latitude 
        - `lon` - longitude 
        - `radius` - the searchradius in meters
        - `limit` - max of shapes
        - `offset` - offset to skip

    """

    latitude = request.query.getunicode("lat")
    longitude = request.query.getunicode("lon")
    radius = request.query.getunicode("radius")
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


@app.route('/buildings/<id>', ['GET'])
def get_building(id: int):
    """GET a building by id
        :Parameters:
        - `id` - the osm id of the building
    """

    way = overpass.get_by_osm_id(id)
    return {"status": "OK", "result": way}


@app.route('/buildings/<id>/edit-form', ['GET'])
def get_building_form(id: int):
    """GET the edit form for a building
        :Parameters:
        - `id` - the osm id of the building
    """
    try:
        way = overpass.get_by_osm_id(id)
    except Exception as e:
        raise APIError("Building not found", status=404)
    form = FormGenerator(settings.EDIT_FIELDS, way)

    return {"status": "OK", "result": form.generate()}


@app.route('/buildings/<id>', ['PUT'])
def update_building(id: int):
    """GET a building by id
        :Parameters:
        - `id` - the osm id of the building
        - `username` - openstreetmap.org username
        - `password` - openstreetmap.org password
        - `data_payload`- the changed way data as payload
    """

    apikey = request.query.getunicode("apikey")
    if not apikey:
        raise APIError("Need param apikey", status=401)
    session = PgSession()

    user = session.query(User).filter(User.apikey == apikey).first()
    if user is None:
        raise APIError("Wrong/unknown apikey")

    try:
        osm_auth_client = settings.get_osm_auth()
        oauth_session = osm_auth_client.get_session((user.oauth_access_token, user.oauth_access_token_secret))
    except Exception as e:
        raise APIError("Authentication failed", status=401)

    api = OsmApiClient(oauth_session)

    try:
        way = overpass.get_by_osm_id(id)
    except Exception as e:
        raise APIError("Building not found", status=404)

    data = request.body.read().decode("utf-8")

    if not data:
        raise APIError("No data received")

    try:
        request_body = json.loads(data)
    except TypeError:
        raise APIError("Cant parse JSON")

    if type(request_body) is not dict:
        raise APIError("Invalid request")


    result = api.update_way(id, request_body)
    try:
        result = api.update_way(id, request_body)
    except Exception:
        raise APIError("Unknown error while saving")


    point = Points()
    point.user_id = user.id
    point.count = 1
    point.changeset = result
    session.add(point)
    session.commit()

    return {"status": "OK", "result": {"changeset_id": result}}


@app.route('/reverse-geocode')
def reverse_geocode_api():
    """Reverse Geocode a shape, to prefill fields like street and city
        :Parameters:
            - `lat` - Latitude
            - `lon` - Longitude
    """
    latitude = request.query.getunicode("lat")
    longitude = request.query.getunicode("lon")
    if not latitude:
        return APIError(body="need param lat")

    if not longitude:
        return APIError(body="need param lon")
    latitude = float(latitude)
    longitude = float(longitude)
    return {"status": "OK", "result": reverse_geocode(latitude, longitude)}



# Authentication Stuff


@app.route('/user/signup', ["GET"])
def get_oauth_redirect_url():
    """Open an authetication session and get a redirect url"""
    
    session = PgSession()
    osm_auth_client = settings.get_osm_auth()
    request_token, request_token_secret  = osm_auth_client.get_request_token()
    authorize_url = osm_auth_client.get_authorize_url(request_token)
    auth = OAuthCache()
    auth.request_token = request_token
    auth.request_token_secret = request_token_secret
    auth.uuid = str(uuid.uuid4())
    session.add(auth)
    session.commit()

    return {"status": "OK", "result": { "redirect_url": authorize_url, "session_id": auth.uuid}}


@app.route('/user/signup', ["POST"])
def signup_user():
    """Creates an User (needs an oauth_token)
        - `session_id` - the authentication session id retrieved from /user/signup/
        - `oauth_token` - the oauth token
    """

    data = request.body.read().decode("utf-8")
    osm_auth_client = settings.get_osm_auth()

    if not data:
        raise APIError("No data received")

    try:
        request_body = json.loads(data)
    except TypeError:
        raise APIError("Cant parse JSON")

    if type(request_body) is not dict:
        raise APIError("Invalid request")


    if "session_id" in request_body:
        session_id = request_body["session_id"]
    else:
        raise APIError("Need param session_id")

    if "oauth_token" in request_body:
        oauth_token = request_body["oauth_token"]

    else:
        raise APIError("Need param oauth_token")


    try:
        
        session = PgSession()    
        oauth_session = session.query(OAuthCache).filter(OAuthCache.uuid == session_id).first()
        access_token, access_token_secret = osm_auth_client.get_access_token(oauth_session.request_token,
                                   oauth_session.request_token_secret,
                                   method='POST',
                                   data={'oauth_verifier': str(oauth_token)})
    except Exception as e:
        raise APIError("Authentication failed", status=401)


    oauth_session = osm_auth_client.get_session((access_token, access_token_secret))
    osm_api = OsmApiClient(oauth_session)
    osm_user_data = osm_api.get_user_details()

    user = session.query(User).filter(User.osm_id == osm_user_data["id"]).first()
    if not user:
        user = User()
        user.osm_id = osm_user_data["id"]
        user.name = osm_user_data["display_name"]
        user.oauth_access_token = access_token
        user.oauth_access_token_secret = access_token_secret
        user.apikey = generate_apikey()

    else:
        user.name = osm_user_data["display_name"]
        user.oauth_access_token = access_token
        user.oauth_access_token_secret = access_token_secret

    session.add(user)
    session.commit()    
    
    return {"status": "OK", "result": { "apikey": user.apikey, "name": user.name, "osm_id": user.osm_id, "id": user.id, "session_id": session_id}} 


@app.route('/user')
def user_details():
    """Get Details about the logged in user
            :Parameters:
                - `apikey` - apikey
    """
    apikey = request.query.getunicode("apikey")
    if not apikey:
        raise APIError("Need param apikey", status=401)
    session = PgSession()
    osm_auth_client = settings.get_osm_auth()

    user = session.query(User).filter(User.apikey == apikey).first()
    if user is None:
        raise APIError("Wrong/unknown apikey")

    try:
        oauth_session = osm_auth_client.get_session((user.oauth_access_token, user.oauth_access_token_secret))
        osm_api = OsmApiClient(oauth_session)
        osm_user_data = osm_api.get_user_details()
    except Exception as e:
        raise APIError("Authentication failed", status=401)
    osm_user_data["points"] = user.points_sum

    return {"status": "OK", "result": osm_user_data}



@app.route('/user/leaderboard')
def leaderboard():
    """Get the top X users 
        :Parameters:
            - `limit` - max users (default 100)

       :Returns:
            a `list` of users
    """

    apikey = request.query.getunicode("apikey")
    if not apikey:
        raise APIError("Need param apikey", status=401)
    session = PgSession()
    osm_auth_client = settings.get_osm_auth()

    user_session = session.query(User).filter(User.apikey == apikey).first()
    if user_session is None:
        raise APIError("Wrong/unknown apikey")


    limit = request.query.getunicode("limit")
    if limit:
        limit = int(limit)
        if limit > 500 or limit < 1:
            limit = 100
    else:
        limit = 100



    session = PgSession()
    users = session.query(User, func.sum(Points.count).label("total_score")).join(Points).group_by(Points.user_id).order_by(sqlalchemy.desc("total_score")).limit(limit).all()

    
    leaderboard = []
    for user in users:
        myself = False
        if user[0].id == user_session.id:
            myself = True
        leaderboard.append({"username": user[0].name, "user_id": user[0].id, "points": user[1], "myself": myself })
         


    return {"status": "OK", "result": leaderboard}





    
app = StripPathMiddleware(app)
    
    
    








if __name__ == "__main__":
    run(app=app, host=settings.BOTTLE["host"], port=settings.BOTTLE["port"], reloader=settings.BOTTLE["reloader"], debug=settings.BOTTLE["debug"])
