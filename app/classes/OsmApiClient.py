from osmapi import OsmApi
import xml.dom.minidom


class OsmApiClient(object):

    def __init__(self, session):
        self.__connection = session

    __connection = None

    __api_endpoint = "api.openstreetmap.org"

    __default_comment = "Updated by osmhunter app."

    def get_way(self, id: int):
        """GET a way by id
        :Parameters:
            - `id` - osm id of way

        :Return:
            dict with waydata
        """
        osmapi = OsmApi(api=self.__api_endpoint)
        return osmapi.WayGet(id)

    def update_way(self, id: int, data: dict):
        """Simple method to update ways
        :Parameters:
            - `id` - osm id of way
            - `data` - the new tags/nodes for this way
        :Returns:
            Changeset Id
        """
        # TODO(felix): test this method
        # TODO(felix): extend osmapi lib to use it with oauth

        osmapi = OsmApi(api=self.__api_endpoint)

        changeset_create_request = osmapi._XmlBuild("changeset", {"tag": {"comment": str(self.__default_comment)}})
        changeset = self.__connection.put("changeset/create", headers={"Content-Type": "application/xml"}, data=changeset_create_request.decode("utf-8"))
        changeset = int(changeset.text)
        way = self.get_way(id)
        osmapi._CurrentChangesetId = changeset

        # TODO(felix): support not only tags

        tags = data["tags"]

        for tag, value in tags.items():
            if tag in way["tag"]:
                if value != way["tag"][tag] and value is not None:
                    way["tag"][tag] = value
            elif value is not None:
                way["tag"][tag] = value

        way["changeset"] = changeset
        way_change_request = osmapi._XmlBuild("way", way).decode("utf-8")
        self.__connection.put("way/%s" % str(id), headers={"Content-Type": "application/xml"}, data=way_change_request)
        self.__connection.put("changeset/%s/close" % str(id), data={})

        return changeset

    def get_user_details(self):
        """Get details about logged in user
            :Returns:
                A dict with userdata
        
        """
        response = self.__connection.get("user/details")
        data = xml.dom.minidom.parseString(response.text)
        data = data.getElementsByTagName("osm")[0]
        data = data.getElementsByTagName("user")[0]
        location = data.getElementsByTagName("home")
        if len(location) > 0:
            location = {"lat": location[0].attributes["lat"].value, "lon": location[0].attributes["lon"].value}
        else:
            location = {"lat": None, "lon": None}
        return {"id": data.attributes["id"].value, "display_name": data.attributes["display_name"].value, "image": data.getElementsByTagName("img")[0].attributes["href"].value,
                "location": {"lat": location["lat"], "lon": location["lon"]}}
