import transaction
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.security import Allow, Deny
from pyramid.security import Everyone

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
BaseModel = declarative_base()

class RootFactory(object):
    __acl__ = [
            (Allow, 'group:user', 'view'),
            (Allow, 'group:admin', 'admin_view'),
            (Allow, 'group:editor', 'edit_news')
            ]

    def __init__(self, request):
        pass
    
from CISBase import Base
from CISFleet import Fleet
from CISGuild import GuildInfo
from CISGuild import GuildMembership
from CISLocation import Terrain
from CISLocation import Location
from CISUser import User
from CISUser import Player
from CISGroup import Group
from CISGroup import GroupMembership

from CISUser import addUserMapping
addUserMapping()


##Cister
from CISNews import News


def populate():
    session = DBSession()
    session.flush()
    transaction.commit()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
#    try:
#        populate()
#    except IntegrityError:
#        transaction.abort()
