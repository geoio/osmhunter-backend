from bson import json_util
import json

from bottle import request, response, route
from bottle import install, uninstall


class JSONAPIPlugin(object):
    name = 'jsonapi'
    api = 2

    def __init__(self, json_dumps=json.dumps, json_util=json_util.default):
        uninstall('json')
        self.json_dumps = json_dumps
        self.json_util = json_util

    def apply(self, callback, context):
        def wrapper(*a, **ka):
            rv = callback(*a, **ka)
            if isinstance(rv, dict):
                # Attempt to serialize, raises exception on failure
                json_response = self.json_dumps(rv, default=self.json_util)
                # Set content type only if serialization succesful
                response.content_type = 'application/json'

                # Wrap in callback function for JSONP
                callback_function = request.query.get('callback')
                if callback_function:
                    response.content = 'application/javascript'
                    json_response = ''.join([callback_function, '(', json_response, ')'])
                return json_response
            return rv
        return wrapper
        