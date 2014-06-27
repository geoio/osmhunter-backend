import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from helpers.geo_helpers import reverse_geocode


class FormGenerator(object):

    def __init__(self, form_fields: list, way: dict):
        """Generates a JSON representation of the edit form for the clients
                :Properties:
                        - `form_fields` - a `list` with all available form fields and there properties
                        - `way` - a `dict` with the data from the overpass api
        """
        self.__form_fields = form_fields
        self.__tags = way["tags"]
        location = way["centroid"]
        self.__location = {"location": location, "address": reverse_geocode(location["lat"], location["lon"])}
        print(self.__location)

    __form_fields = []
    __tags = {}
    __location = {}

    OSM_TO_NOMINATIM_MAPPING = {
        "addr:street": ["road"],
        "addr:city":  ["village", "town", "city"],
        "addr:postcode": ["postcode"],

    }

    def generate(self):
        """Generates the Form
                :Returns:
                        a `list` of form field dicts
        """

        output = []

        for key, form_field in enumerate(self.__form_fields):

            # set value
            if form_field["name"] in self.__tags:
                form_field["value"] = self.__tags[form_field["name"]]
                form_field["prefilled"] = False
            elif form_field["prefilled"] is True:
                form_field["value"] = self.__get_nominatim_value(form_field["name"])
                if form_field["value"] is None:
                    form_field["prefilled"] = False
            else:
                form_field["value"] = None
                form_field["prefilled"] = False

            if form_field["type"] is "select" and form_field["value"] is not None:
                if not self.__search_options(form_field["options"], form_field["value"]):
                    form_field["options"].append({"value": form_field["value"], "label": form_field["value"]})

            self.__form_fields[key] = form_field

        return self.__form_fields

    def __get_nominatim_value(self, key):
        """GET an attribute from nominatim reverse geocoding
                :Parameters:
                        - `key` - the openstreetmap key
                :Returns:
                        the value or `None`
        """

        if key in self.OSM_TO_NOMINATIM_MAPPING:
            for nominatim_key in self.OSM_TO_NOMINATIM_MAPPING[key]:
                if nominatim_key in self.__location["address"]:
                    return self.__location["address"][nominatim_key]

        return None

    def __search_options(self, options, value):
        """Helper method for search for option in the option list
                :Parameters:
                        - `options` - list of options
                        - `value` - the current value

                :Returns:
                        true if the option is in the list else false
        """
        for option in options:
            if value == option["value"]:
                return True

        return False
