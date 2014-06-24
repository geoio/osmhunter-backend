import datetime
import hashlib
import os
import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import backref, relationship

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from helpers.utils import generate_apikey

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    osm_id = Column(Integer)
    oauth_access_token = Column(String)
    oauth_access_token_secret = Column(String)
    apikey = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def points_sum(self):
        c = 0
        for point in self.points:
            c += point.count
        return c


class Points(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    count = Column(Integer)
    changeset = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref=backref("points", order_by=id))



class OAuthCache(Base):
    __tablename__ = "oauth_cache"

    id = Column(Integer, primary_key=True)
    request_token = Column(String)
    request_token_secret = Column(String)
    uuid = Column(String)
