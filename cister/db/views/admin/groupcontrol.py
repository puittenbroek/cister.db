from sqlalchemy import or_, and_

from cister.db.models.cister import Group, GroupMembership, User, Player, GuildInfo
from cister.db.models.cister import DBSession
from datetime import datetime, timedelta
import re
import webhelpers.paginate as paginate
from webhelpers.util import update_params
from cister.db.views.viewbase import BaseCisterView
from datetime import datetime

guild_id_pattern = re.compile("\[([-+]\d+)\]")
guild_tag_pattern = re.compile("\[(.{1,8})\]")
id_pattern = re.compile("(\d+)")


class GroupControlView(BaseCisterView):

    def grouplist(self):
        session = DBSession()


        returnvalue = {}
        returnvalue['current_groups'] = session.query(Group)
        returnvalue['group'] = None
        returnvalue['users'] = None
        groupid = self.request.matchdict.get('groupid',None)
        if groupid:

            ##TODO: members kloppen niet.
            group = session.query(Group).filter(Group.id==groupid).one()
            returnvalue['group'] =  group

            users = session.query(User).filter(~User.groups.any(Group.id==groupid)).order_by(User.playerid)
            returnvalue['optional_users'] =  users

        guilds = session.query(GuildInfo).filter(GuildInfo.alive==1)
        returnvalue['optional_guilds'] =  guilds

        returnvalue['message'] = None

        return returnvalue

    def submit(self):
        params = self.request.params
        import transaction
        session = DBSession()
        ourvalues = {}
        try:
            groupid = params.get('groupid')
            group = session.query(Group).filter(Group.id==groupid).one()
            if 'deletegroup' in params:
                ourvalues['message'] = 'Succesfully removed %s ' % group.name

            if 'addgroup' in params:
                groupname = params.get('groupname')
                guildid = params.get('guildid')
                group = Group(groupname, guildid)
                session.add(group)

                ourvalues['message'] = 'Succesfully added %s ' % groupname
        except:
            pass
        returnvalue =  self.grouplist()
        returnvalue.update(ourvalues)
        return returnvalue

    def membersubmit(self):
        params = self.request.params
        import transaction
        session = DBSession()
        ourvalues = {}
        try:
            userid = params.get('userid')
            groupid = params.get('groupid')
            player = session.query(Player).filter(Player.id==userid).one()
            group = session.query(Group).filter(Group.id==groupid).one()
            if 'removefromgroup' in params:
                membership = session.query(GroupMembership) \
                    .filter(
                        and_(GroupMembership.groupid==groupid,
                             GroupMembership.userid==userid)) \
                    .first()
                session.delete(membership)
                ourvalues['message'] = 'Succesfully removed %s from %s ' % (player.name, group.name)
                transaction.commit()
            if 'addtogroup' in params:

                membership = GroupMembership(userid, groupid)
                session.add(membership)
                ourvalues['message'] = 'Succesfully added %s to %s ' % (player.name, group.name)
                transaction.commit()

        except:
            pass
        returnvalue =  self.grouplist()
        returnvalue.update(ourvalues)
        return returnvalue
        
