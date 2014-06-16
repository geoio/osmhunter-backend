import json

import requests


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
            <!-- query part for: “building=*” -->
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

        return self.__format_api_result(requests.post(self.__overpass_api_url, data={"data": query}).json()["elements"])


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
            <!-- query part for: “building=*” -->
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

        return self.__format_api_result(requests.post(self.__overpass_api_url, data={"data": query}).json()["elements"])


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
            result.append(way)

        return result


