from osmapi import OsmApi
import xml.dom.minidom


class OsmApiClient(object):

    def __init__(self, session):
        self.__connection = session

    __connection = None

    __api_endpoint = "api.openstreetmap.org"

    __default_comment = "Updated by osmhunter app."

    def update_way(self, id: int, data: dict):
        """Simple method to update ways
        :Parameters:
            - `id` - osm id of way
            - `data` - the new tags/nodes for this way
        :Returns:
            Changeset Id
        """
        # TODO(felix): test this method
        changeset = self.__connection.ChangesetCreate({"comment": self.__default_comment})

        way = self.get_way(id)

        # TODO(felix): support not only tags

        tags = data["tags"]

        for tag, value in tags.items():
            if tag in way["tag"]:
                if value != way["tag"][tag]:
                    way["tag"][tag] = value
            else:
                way["tag"][tag] = value

        self.__connection.WayUpdate(way)

        self.__connection.ChangesetClose()

        return changeset

    def get_user_details(self):
        response = self.__connection.get("user/details.json")   
        data = xml.dom.minidom.parseString(response.text)
        data = data.getElementsByTagName("osm")[0]
        data = data.getElementsByTagName("user")[0]
        location = data.getElementsByTagName("home")[0].attributes
        return {"id": data.attributes["id"].value, "display_name": data.attributes["display_name"].value, "image": data.getElementsByTagName("img")[0].attributes["href"].value,
         "location": {"lat": location["lat"].value, "lon": location["lon"].value }}