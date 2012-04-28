from cister import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, DECIMAL
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.sql import join

class GuildInfo(BaseModel):
    __tablename__ = 'guildinfo'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(45))
    tag = Column(Unicode(45))
    submitid =  Column(Integer, default=-1)
    timestamp =  Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    updateid =  Column(Integer, default=-1)
    alive =  Column(Boolean, default=0)
    guildmembers =  relationship("GuildMembership", backref="guild")

    def __init__(self, id, name, tag, submitid,
                updateid, timestamp, alive ):
        self.id = id
        self.name = name
        self.tag = tag
        self.submitid = submitid
        self.updateid = updateid
        self.timestamp =  timestamp
        self.alive =  alive

class GuildMembership(BaseModel):
    __tablename__ = 'guildmember'
    guildid = Column(Integer, ForeignKey("guildinfo.id"))
    playerid = Column(Integer, primary_key=True)
    timestamp =  Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    valid =  Column(Boolean, default=0)

#    guild = relationship("Guild",
#        primaryjoin='GuildMembership.playerid== Player.id',
#        innerjoin=True,
#        join_depth=3,
#        lazy='joined',
#        backref=backref("players", uselist=False))



    def __init__(self, guildid, playerid,
                timestamp, alive ):
        self.guildid = guildid
        self.playerid = playerid
        self.timestamp =  timestamp
        self.valid =  valid

#guildinfo_table = GuildInfo.__table__
#guildmember_table = GuildMembership.__table__
#guild_join = join(guildinfo_table, guildmember_table) #, onclause=guildinfo_table.c.id==guildmember_table.c.guildid)
#
#class Guild(BaseModel):
#    __table__ = guild_join
#    guild_updatetimstamp = guildinfo_table.c.timestamp