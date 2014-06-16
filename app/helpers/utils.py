import json

from bottle import route, run, template, Bottle
import bottle



class APIError(bottle.HTTPResponse):
    def __init__(self, body="", status=400, **kwargs):
        bottle.BaseResponse.__init__(self, status=status, **kwargs)
        self.content_type = "application/json"
        self.body = json.dumps({
            "status": "ERROR",
            "message": body
        })