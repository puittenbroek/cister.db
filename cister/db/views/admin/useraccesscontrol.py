from sqlalchemy import or_, and_

from cister.db.models.cister import User
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


class UserAccessControlView(BaseCisterView):

    def userlist(self):
        dbsession = DBSession()


        returnvalue = {}
        returnvalue['to_activate'] = dbsession.query(User).filter(and_(User.activated==0,User.banned==0))
        returnvalue['activate'] = dbsession.query(User).filter(and_(User.activated==1,User.banned==0))
        returnvalue['banned'] = dbsession.query(User).filter(User.banned==1)

        returnvalue['message'] = None
        
        return returnvalue


    def submit(self):
        params = self.request.params
        import transaction
        session = DBSession()
        ourvalues = {}
        
        playerid = params.get('playerid')
        player = session.query(User).filter(User.playerid==playerid).one()
        if 'ban' in params:
            player.banned = 1
            player.banned_on = datetime.now()
            transaction.commit()
            ourvalues['message'] = 'Succesfully banned player: %s ' % playerid
        if 'unban' in params:
            player.banned = 0
            player.banned_on = ''
            transaction.commit()
            ourvalues['message'] = 'Succesfully unbanned player: %s ' % playerid

        if 'activate' in params:
            player.activated = 1
            player.activated_on = datetime.now()
            transaction.commit()
            ourvalues['message'] = 'Succesfully activated player: %s ' % playerid

        if 'deactivate' in params:
            player.activated = 0
            player.activated_on = datetime.now()
            transaction.commit()
            ourvalues['message'] = 'Succesfully deactivated player: %s ' % playerid


        if 'delete' in params:
            ourvalues['message'] = 'Succesfully delete player: %s ' % playerid



        returnvalue =  self.userlist()
        returnvalue.update(ourvalues)

        return returnvalue
        
