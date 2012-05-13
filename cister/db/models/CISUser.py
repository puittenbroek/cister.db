from cister import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, DECIMAL
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

##Own models
from CISGuild import GuildInfo
from CISGuild import GuildMembership
#from CISGroup import Group
#from CISGroup import GroupMembership
GuildInfoTable = GuildInfo.__table__
GuildMembershipTable = GuildMembership.__table__
#GroupTable = Group.__table__
#GroupMembershipTable = GroupMembership.__table__

class User(BaseModel):
    __tablename__ = 'cis_users'
    playerid        = Column(Integer, ForeignKey("player.id"), primary_key=True, )
    playervalue     = Column(Unicode(32))
    password        = Column(Unicode(32))
    code            = Column(Unicode(32))
    creation        = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    activated       = Column(Boolean, default=0)
    activated_on    = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    activated_by    = Column(Unicode(10))
    deactivated_on  = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    deactivated_by  = Column(Unicode(10))
    banned          = Column(Boolean, default=0)
    banned_on       = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    banned_by       = Column(Unicode(10))
    last_activity   = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    last_script     = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    last_web        = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')
    alias 	    = Column(Unicode(45))

    player = relationship("Player",
        primaryjoin='User.playerid==Player.id',
        join_depth=3,
        lazy='joined')

    guild = relationship("GuildInfo",
        secondary=GuildMembershipTable,
        primaryjoin=playerid==GuildMembershipTable.c.playerid,
        secondaryjoin=GuildMembershipTable.c.guildid==GuildInfoTable.c.id,
        innerjoin=False,
        join_depth=3,
        lazy='joined',
        uselist=False,)
    
    #Bases
    submittedbases = relationship("Base", primaryjoin='Base.submitid==User.playerid', lazy='select')
    updatedbases = relationship("Base", primaryjoin='Base.updateid==User.playerid', lazy='select')

    #Fleets
    submittedfleets = relationship("Fleet", primaryjoin='Fleet.submitid==User.playerid',lazy='select')
    updatedfleets = relationship("Fleet", primaryjoin='Fleet.updateid==User.playerid',lazy='select')
#    groups = relationship("Group",
#        secondary=GroupMembershipTable,
#        primaryjoin=playerid==GroupMembershipTable.c.userid,
#        secondaryjoin=GroupMembershipTable.c.groupid==GroupTable.c.id,
#        innerjoin=False,
#        join_depth=3,
#        lazy='joined',
#        uselist=True,)
#
#    membership = relationship("GroupMembership",
#        primaryjoin=playerid==GroupMembershipTable.c.userid,
#        innerjoin=False,
#        join_depth=3,
#        uselist=False,
#        lazy='joined',)

class Player(BaseModel):
    __tablename__ = 'player'
    id = Column(Integer, ForeignKey("guildmember.playerid"), primary_key=True)
    name =  Column(Unicode(45))
    level = Column('lvl',DECIMAL(6,2))
    timestamp =  Column(TIMESTAMP, default='CURRENT_TIMESTAMP')

    ##Fleets
    fleets = relationship("Fleet", primaryjoin='Fleet.ownerid==Player.id',lazy='select')

    ##Bases
    ownedbases = relationship("Base", primaryjoin='Base.ownerid==Player.id',lazy='select')
    occupiedbases = relationship("Base", primaryjoin='Base.occupierid==Player.id', lazy='select')


    guild = relationship("GuildInfo",
        secondary=GuildMembershipTable,
        primaryjoin=id==GuildMembershipTable.c.playerid,
        secondaryjoin=GuildMembershipTable.c.guildid==GuildInfoTable.c.id,
        innerjoin=False,
        join_depth=3,
        lazy='joined',
        uselist=False,
        backref=backref("members", uselist=False))


def addUserMapping():
    from sqlalchemy.orm import mapper
    from sqlalchemy.orm import relationship

    from CISGroup import Group
    from CISGroup import GroupMembership
    UserTable = User.__table__
    GroupTable = Group.__table__
    GroupMembershipTable = GroupMembership.__table__
    UserTable = User.__table__

    User.groups =  relationship("Group",
        secondary=GroupMembershipTable,
        primaryjoin=UserTable.c.playerid==GroupMembershipTable.c.userid,
        secondaryjoin=GroupMembershipTable.c.groupid==GroupTable.c.id,
        innerjoin=False,
        join_depth=3,
        lazy='joined',
        uselist=True,)

