from cister import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, DECIMAL
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from datetime import datetime

##Own models
from CISGuild import GuildInfo
from CISGuild import GuildMembership
GuildInfoTable = GuildInfo.__table__
GuildMembershipTable = GuildMembership.__table__

from CISUser import User
UserTable = User.__table__

class GroupMembership(BaseModel):
    __tablename__ = 'cis_groups_users'
    userid = Column('user_id',Integer, ForeignKey("cis_users.playerid"), key='userid',  primary_key=True)
    groupid= Column('group_id',Integer, ForeignKey("cis_groups.id"),key='groupid',primary_key=True)
    added_on =  Column(TIMESTAMP, default='CURRENT_TIMESTAMP')

    def __init__(self, userid, groupid):
        self.userid = userid
        self.groupid = groupid
        self.added_on = datetime.now()

    user = relationship("User",
        primaryjoin=userid==UserTable.c.playerid,
        innerjoin=True,
        join_depth=3,
        lazy='joined',
        uselist=False,)

GroupMembershipTable = GroupMembership.__table__

class Group(BaseModel):
    __tablename__ = 'cis_groups'
    id = Column(Integer, autoincrement=True,primary_key=True)
    name =  Column(Unicode(45))
    guild_id= Column(Integer, ForeignKey("guildinfo.id"), primary_key=True)

    def __init__(self, name, guild_id):
        self.name = name
        self.guild_id = guild_id

        
    guild = relationship("GuildInfo",
        primaryjoin=guild_id==GuildInfoTable.c.id,
        innerjoin=False,
        lazy='joined',
        uselist=False,)

    members = relationship("User",
        secondary=GroupMembershipTable,
        primaryjoin=id==GroupMembershipTable.c.groupid,
        secondaryjoin=GroupMembershipTable.c.userid==UserTable.c.playerid,
        innerjoin=False,
#        lazy='joined',
        uselist=True,)

    memberships = relationship("GroupMembership",
        primaryjoin=id==GroupMembershipTable.c.groupid,
        innerjoin=False,
#        lazy='joined',
        uselist=True,)


#    group = relationship("Group",
#        primaryjoin=groupid==Group.__table__.c.id,
#        innerjoin=False,
#        lazy='joined',
#        uselist=False,
#        backref=backref("memberships"))

