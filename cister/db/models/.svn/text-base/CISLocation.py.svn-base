from cister import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import join
from sqlalchemy.orm import column_property

class Terrain(BaseModel):
    __tablename__ = 'terrain'
    id = Column(Integer, primary_key=True)
    name =  Column(Unicode(45))
#    locations = relationship("LocationTerrain", backref="terrain")

    def __init__(self, id, name):
        self.id = id
        self.name = name

class Location(BaseModel):
    __tablename__ = 'locationterrain'
    location = Column(Unicode(12),primary_key=True)
    terrainid = Column(Integer, ForeignKey("terrain.id"))
    submitid =  Column(Integer, default=-1)
    loc_gal =  Column(Unicode(3))
    timestamp =  Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    terrain = relationship("Terrain", uselist=False, lazy='joined')

    fleets = relationship("Fleet", lazy='joined')
    base = relationship("Base", uselist=False, lazy='joined')

#
#    def __init__(self, location, terrainid,
#                submitid, loc_gal, timestamp ):
#        self.location = location
#        self.terrainid = terrainid
#        self.submitid =  submitid
#        self.loc_gal =  loc_gal
#        self.timestamp =  timestamp
#
