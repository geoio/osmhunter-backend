import json
import sys
import os

import requests

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from helpers.geo_helpers import calculate_centroid, geo_distance



class OverpassApi(object):
    def __init__(self):
        """OverpassAPI connector, tot retrieve buildings, without housenumber, …"""
        pass



    __overpass_api_url = "http://www.overpass-api.de/api/interpreter"

    def get_buildings_without_housenumber_bbox(self, bbox: dict) -> list:
        """GET `list` of shapefiles (mostly buildings) without housenumbers in area
            
            :Properties:
                - `bbox` - the searcharea


            :Returns:
                GeoJson as `Dict`

        """


        query = """
        <osm-script output="json" timeout="25">
          <union>
            <query type="way">
              <has-kv k="building"/>
              <has-kv k="addr:housenumber" modv="not" regv="."/>
              <has-kv k="building" modv="not" regv="garage|transformer_tower|sty|stable|shed|roof|hut|hangar|greenhouse|garages|farm_auxiliary|cowshed|cabin|bunker|bridge|barn|static_caravan|houseboat|terrace"/>
              <bbox-query  s="%s" w="%s" n="%s" e="%s"/>
            </query>
          </union>
          <print mode="body"/>
          <recurse type="down"/>
          <print mode="skeleton" order="quadtile"/>
        </osm-script>
        """ % (bbox["south"], bbox["west"], bbox["north"], bbox["east"])

        #calculate centroid of boundingbox for result sorting
        location = calculate_centroid([{"lat": bbox["south"],"lon": bbox["west"]}, {"lat": bbox["south"], "lon": bbox["east"]}, {"lat": bbox["north"], "lon": bbox["east"]}, {"lat": bbox["north"], "lon": bbox["west"]}])

        results = self.__format_api_result(requests.post(self.__overpass_api_url, data={"data": query}).json()["elements"])
        results = self.__calculate_distance(results, location)
        return self.__sort_by_distance(results)




    def get_buildings_without_housenumber_nearby(self, lat: float, lon: float, radius: int) -> list:
        """GET `list` of shapefiles (mostly buildings) without housenumbers arround the point
            
            :Properties:
                - `lat` - latitude
                - `lon` - longitude
                - `radius` - searchradius


            :Returns:
                GeoJson as `Dict`

        """


        query = """
            <osm-script output="json" timeout="25" >
          <union>
            <query type="way">
              <has-kv k="building"/>
              <has-kv k="addr:housenumber" modv="not" regv="."/>
              <has-kv k="building" modv="not" regv="garage|transformer_tower|sty|stable|shed|roof|hut|hangar|greenhouse|garages|farm_auxiliary|cowshed|cabin|bunker|bridge|barn|static_caravan|houseboat|terrace"/>
              <around lat="%s" lon="%s" radius="%s"/>
            </query>
          </union>
          <print mode="body"/>
          <recurse type="down"/>
          <print mode="skeleton" order="quadtile"/>
        </osm-script>
        """ % (lat, lon, radius)

        results = self.__format_api_result(requests.post(self.__overpass_api_url, data={"data": query}).json()["elements"])

        results = self.__calculate_distance(results, {"lat": lat , "lon": lon})

        return self.__sort_by_distance(results)



    def get_by_osm_id(self, osm_id):
        query = """
        <osm-script output="json" timeout="25">
          <id-query ref="%s" type="way"/>
          <print/>
          <print mode="body"/>
          <recurse type="down"/>
          <print mode="skeleton" order="quadtile"/>
        </osm-script>
        """ % (osm_id)

        return self.__format_api_result(requests.post(self.__overpass_api_url, data={"data": query}).json()["elements"])[0]



    def __format_api_result(self, data: list) -> list:
        """Reformats the result `list` from the overpass api (aggregates th shape data)
        :Parameters:
            - `data` - original overpass api result

        :Returns:
            the reformated result

        """

        nodes = {}
        ways = []

        for item in data:
            if item["type"] == "node":
                nodes[item["id"]] = item

            elif item["type"] == "way":
                ways.append(item)

        result = []
        for way in ways:
            temp_nodes = []
            for node in way["nodes"]:
                temp_nodes.append({"lat": nodes[node]["lat"], "lon": nodes[node]["lon"], "id": node})


            way["nodes"] = temp_nodes
            way["centroid"] = calculate_centroid(temp_nodes)
            result.append(way)

        return result


    def __calculate_distance(self, results: list, location: dict) -> list:
        """Adds the distance to the resultset
            :Parameters:
                - `results` - a resultlist
                - `location` - the location for distance calculation

            :Returns:
                A `list` of results with a distance parameter
        """
        for key,value in enumerate(results):
            results[key]["distance"] = geo_distance(location["lat"],location["lon"],value["centroid"]["lat"],value["centroid"]["lon"])

        return results


    def __sort_by_distance(self, results: list) -> list:
        """Sorts the resultsset by distance
            :Parameters:
                - `results` - A resultlist
            :Returns:
                A sorted `list` of results
        """

        return sorted(results, key=lambda k: k['distance']) 

