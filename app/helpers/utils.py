import hashlib
import json
import os

from bottle import route, run, template, Bottle
import bottle
from sqlalchemy.exc import SQLAlchemyError, DBAPIError

def with_db_session(func=None, argument="db"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            app = kwargs["app"]
            kwargs[argument] = session = app.sqlalchemy_session(bind=app.sqlalchemy_engine)
            try:
                rv = func(*args, **kwargs)
            except (SQLAlchemyError, bottle.HTTPError, DBAPIError):
                session.rollback()
                raise
            finally:
                session.close()
            return rv
        return wrapper
    if callable(func):
        return decorator(func)
    return decorator


class APIError(bottle.HTTPResponse):

    def __init__(self, body="", status=400, **kwargs):
        bottle.BaseResponse.__init__(self, status=status, **kwargs)
        self.content_type = "application/json"
        self.body = json.dumps({
            "status": "ERROR",
            "message": body
        })


def generate_apikey():
    return hashlib.sha1(os.urandom(32)).hexdigest()

class StripPathMiddleware(object):
  def __init__(self, app):
    self.app = app
  def __call__(self, e, h):
    e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
    return self.app(e,h)