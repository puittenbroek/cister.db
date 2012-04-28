from cister import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import and_

class Base(BaseModel):
    __tablename__ = 'base'
    id = Column(Integer, primary_key=True)
    location = Column(Unicode(12), ForeignKey("locationterrain.location"), unique=True,)
    name = Column(Unicode(45))
    ownerid =  Column(Integer,ForeignKey("player.id"))
    occupierid =  Column(Integer, ForeignKey("player.id"))
    economy =  Column(Integer, default=-1)
    cc =  Column(Integer, default=-1)
    jg =  Column(Integer, default=-1)
    capital =  Column(Integer, default=-1)
    submitid =  Column(Integer,ForeignKey("player.id"))
    defense =  Column(Unicode(84))
    updateid =  Column(Integer,ForeignKey("player.id"))
    timestamp =  Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    defensetimestamp =  Column(TIMESTAMP, default='0000-00-00 00:00:00')
    loc_gal =  Column(Unicode(3))


    #Relations
    terrain_type = relationship("Location",uselist=False )

    owner = relationship("Player",
        primaryjoin='Base.ownerid==Player.id',
        join_depth=3,
        lazy='joined')
    occupier= relationship("Player",
        primaryjoin='Base.occupierid==Player.id',
        join_depth=3,
        lazy='joined')
    submitter = relationship("Player",
        primaryjoin='Base.submitid== Player.id',
        join_depth=3,
        lazy='joined')
    updater= relationship("Player",
        primaryjoin='Base.updateid== Player.id',
        join_depth=3,
        lazy='joined')

#    def __init__(self, id, location, name, ownerid, occupierid, economy, cc,
#                 jg, capital, submitid, defense, updateid, timestamp,
#                 defenstimestamp, loc_gal ):
#        self.id = id
#        self.location = location
#        self.name = name
#        self.ownerid = ownerid
#        self.occupierid = occupierid
#        self.economy = economy
#        self.cc = cc
#        self.jg =  jg
#        self.capital = capital
#        self.submitid = submitid
#        self.updateid = updateid
#        self.defense = defense
#        self.timestamp =  timestamp
#        self.defenstimestamp =  defenstimestamp
#        self.loc_gal =  loc_gal

