from cister import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship

##Own models
from CISGuild import GuildInfo
from CISGuild import GuildMembership
from CISUser import Player

class Fleet(BaseModel):
    __tablename__ = 'fleet'
    id = Column(Integer, primary_key=True)
    location = Column(Unicode(12), ForeignKey("locationterrain.location"), ForeignKey("base.location"))
    ownerid =  Column(Integer, ForeignKey("player.id"), ForeignKey("base.ownerid"))
    arrival =  Column(Integer, default=-1)
    size =  Column(Integer, default=-1)
    timestamp =  Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    submitid =  Column(Integer,ForeignKey("cis_users.playerid"))
    details =  Column(Unicode(400))
    updateid =  Column(Integer,ForeignKey("cis_users.playerid"))
    detailstimestamp =  Column(TIMESTAMP, default='0000-00-00 00:00:00')

    owner = relationship("Player",
        primaryjoin='Fleet.ownerid==Player.id',
        join_depth=10,
        lazy='joined')
    submitter = relationship("User",
        primaryjoin='Fleet.submitid== cis_users.c.playerid',
        join_depth=10,
        lazy='joined')
    updater= relationship("User",
        primaryjoin='Fleet.updateid== cis_users.c.playerid',
        join_depth=10,
        lazy='joined')
#    def __init__(self, id, location, ownerid, arrival, size,
#                 submitid, details, updateid, timestamp,
#                 detailstimestamp ):
#        self.id = id
#        self.location = location
#        self.ownerid = ownerid
#        self.arrival = arrival
#        self.size = size
#        self.timestamp =  timestamp
#        self.submitid = submitid
#        self.details = details
#        self.updateid = updateid
#        self.detailstimestamp =  detailstimestamp
