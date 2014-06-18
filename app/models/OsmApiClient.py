from osmapi import OsmApi

class OsmApiClient(object):
	def __init__(self, username, password):
		self.__connection = OsmApi(username=username, password=password, api=self.__api_endpoint)

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
		return self.__connection.WayGet(id)


	def update_way(self, id: int, tags: dict):
		"""Simple method to update ways
		:Parameters:
			- `id` - osm id of way
			- `tags` - the new tags for this way
		:Returns:
			Changeset Id
		"""
		#TODO(felix): test this method
		changeset = self.__connection.ChangesetCreate({"comment": self.default_comment})

		way = self.get_way(id)

		for tag, value in tags.items():
			if tag in way["tag"]:
				if value != way["tag"][tag]:
					way["tag"][tag] = value
			else:
				way["tag"][tag] = value

		self.__connection.WayUpdate(way)

		self.ChangesetClose()

		return changeset


