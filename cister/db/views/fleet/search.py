from sqlalchemy import or_,func, select
from sqlalchemy import asc, desc
from cister.db.models.cister import Base, Player, GuildInfo
from cister.db.models.cister import Fleet
from cister.db.models.cister import DBSession
from datetime import datetime, timedelta
import re
import webhelpers.paginate as paginate
from webhelpers.util import update_params
from cister.db.views.viewbase import BaseCisterView


from pyramid.security import authenticated_userid


guild_id_pattern = re.compile("\[([-+]\d+)\]")
guild_tag_pattern = re.compile("\[(\D+)\]")
id_pattern = re.compile("(\d+)")


class FleetSearchView(BaseCisterView):


    def __init__(self, request):
        self.request = request
        self.filters = getFleetFilters()
        self.fieldfilters = getFieldFilters()

    def __call__(self):
        dbsession = DBSession()
        fleets = []
        locationlength = 12
        grouper = ''
        params = None
        params = self.request.params
        if "form.submitted" in self.request.params:
            def url_generator(**kw):
                new_url = update_params(self.request.url, page=kw['page'])
                return new_url
            params = self.request.params
#            if 'group_by' in self.request.params and self.request.params.get('group_by') != '':
            fleets = dbsession.query(Fleet,
                                    func.sum(Fleet.size).label("fleet_sum"),
                                    select(["FROM_UNIXTIME(UNIX_TIMESTAMP(fleet.timestamp))"]).label("average_age"),
                                    select(["FROM_UNIXTIME(UNIX_TIMESTAMP(fleet.detailstimestamp))"]).label("average_detail_age"),
                                    select(["fleet.arrival-(unix_timestamp(now())-unix_timestamp(fleet.timestamp))"]).label("absolute_arrival"),
                                    )
#            else:
#                fleets = dbsession.query(Fleet)

           
            if 'location' in self.request.params and self.request.params.get('location') != '':
                locations = self.request.params.get('location').strip().split(',')
                qrs = []
                for location in locations:
                    qrs.append(Fleet.location.like("%s%%" % location))
                fleets = fleets.filter(or_(*qrs))
            fleets = performFleetFilter(fleets, params)
            ##Grouping
            if 'group_by' in self.request.params and self.request.params.get('group_by') != '':
                grouper = self.request.params.get('group_by')
        #                ('owner-01','Location, Owner'),
        #                ('owner-01','Galaxy, Owner'),
        #                ('owner-02','Galaxy-Group, Owner')
        #                ('blob-01','Location, Guild'),
        #                ('blob-02','Galaxy, Guild'),
        #                ('blob-03','Galaxy-Group, Guild'),
                fleets = fleets.join(Fleet.owner)
                fleets = fleets.join(Player.guild)
                if grouper == 'owner-01':
                    fleets = fleets.group_by(Fleet.location, Fleet.ownerid)
                if grouper == 'owner-02':
                    fleets = fleets.group_by(func.substring(Fleet.location,1,3), Fleet.ownerid)
                    locationlength = 3
                if grouper == 'owner-03':
                    fleets = fleets.group_by(func.substring(Fleet.location,1,2), Fleet.ownerid)
                    locationlength = 2
                if grouper == 'blob-01':
                    fleets = fleets.group_by(Fleet.location, GuildInfo.id)
                if grouper == 'blob-02':
                    fleets = fleets.group_by(func.substring(Fleet.location,1,3), GuildInfo.id)
                    locationlength = 3
                if grouper == 'blob-03':
                    fleets = fleets.group_by(func.substring(Fleet.location,1,2), GuildInfo.id)
                    locationlength = 2
            else:
                fleets = fleets.group_by(Fleet.id)
                
            ##Sorting
            if 'sort_field' in self.request.params and self.request.params.get('sort_field') != '':
                fleets = performFleetSort(fleets, self.request.params)

            ##Limits and such
            per_page = int(self.request.params.get('per_page') or 100)
            fleets = paginate.Page(fleets, page=int(self.request.params.get('page', 1)), items_per_page=per_page, url=url_generator, item_count=fleets.count())
#            import pdb; pdb.set_trace()


        return {"datetime":datetime,
                "grouper":grouper,
                "filters": self.filters,
                "fieldfilters":self.fieldfilters,
                "fleets": fleets,
                "params": params,
                "locationlength":locationlength}


def performFleetFilter(fleets, params):
    if 'size' in params and params.get('size') != '':
        size = params.get('size')
        fleets = fleets.having("fleet_sum > %s " % size)

    if 'owner' in params and params.get('owner') != '':
        owners = params.get('owner').split(',')
        qrs = []
        for owner in owners:
            if guild_id_pattern.match(owner):
                id_match = guild_id_pattern.match(owner).groups()[0]
                qrs.append(
                    Fleet.owner.has(
                        Player.guild.has(
                            GuildInfo.id==id_match
                        )
                    )
                )
            elif guild_tag_pattern.match(owner):
                guild_match=guild_tag_pattern.match(owner).groups()[0]
                qrs.append(
                    Fleet.owner.has(
                        Player.guild.has(
                            GuildInfo.tag==guild_match
                        )
                    )
                )
            elif id_pattern.match(owner):
                qrs.append(Fleet.ownerid==owner)
            else: ##Must be name
                qrs.append(Fleet.owner.has(Player.name.like("%%%s%%"% owner)))

        fleets = fleets.filter(or_(*qrs))
    if 'flying' in params and params.get('flying') != '':
        onlyflying = int(params.get('flying'))
        if onlyflying:
            fleets = fleets.filter("arrival-(unix_timestamp(now())-unix_timestamp(fleet.timestamp)) > 0")
        else:
            fleets = fleets.filter("arrival-(unix_timestamp(now())-unix_timestamp(fleet.timestamp)) <= 0")

    if 'agevalue' in params and params.get('agevalue') != '':
        if 'maxagefield' in params and params.get('maxagefield') != '':
            days = int(params.get('agevalue'))
            maxagefield = params.get('maxagefield')
            multiplier = {'day':1, 'week':7, 'month':30}
            days = int(days * multiplier[maxagefield])
            maxAge= datetime.now() - timedelta(days=days)
            fleets = fleets.filter(Fleet.timestamp >= maxAge)
    return fleets


def performFleetSort(fleets, params):
    sort_field = params.get('sort_field')
    sort_order = params.get('sort_order')
    order = desc
    if sort_order =='asc':
        order = asc

    if sort_field == 'fleets.timestamp':
        ##Timestamp needs it's order reverted to make sense..
        fixer = {'asc':desc, 'desc':asc}
        order = fixer.get(sort_order)
        
    if 'fleet.location' in sort_field:
        fleets = fleets.order_by(order(Fleet.location))

    elif 'fleet.timestamp' in sort_field:
        fleets = fleets.order_by(order(Fleet.timestamp))

    elif 'fleet.ownerid' in sort_field:
        fleets = fleets.order_by(order(Fleet.ownerid))

    elif "fleet.size" in sort_field:
        fleets = fleets.order_by(order(Fleet.size))

    elif "arrival" in sort_field:
        fleets = fleets.order_by(order("absolute_arrival"))

    elif "fleet_sum" in sort_field:
        fleets = fleets.order_by(order("fleet_sum"))
        pass
    
    elif "guild.id" in sort_field or "guild.tag" in sort_field:

        order = desc
        if sort_order =='asc':
            order = asc

        fleets = fleets.join(Fleet.owner)
        fleets = fleets.join(Player.guild)

        if "guild.tag" in sort_field:
            fleets = fleets.order_by(order(GuildInfo.tag))
        else:
            fleets = fleets.order_by(order(GuildInfo.id))

    elif "fleet.owner.name" in sort_field: ##Owner
        fleets = fleets.join(Base.owner)
        fleets = fleets.order_by(order(Player.name))
    else: ##No sort
        pass
    return fleets


def getFleetFilters(map=False):
    filters = []
    if not map:
        filters.append({'name':'location','label':"Location", 'type':'text', 'size':12})
    filters.append({'name':'owner','label':"Owner", 'type':'text'})
    filters.append({'name':'size','label':"Size", 'type':'text'})
    filters.append({'name':'flying','label':"Flying", 'type':'select',
                        'options':[('',"Flying&Landed")]+[('1','Flying fleets only'),('0',"Landed fleets only")]})

    filters.append({'label':"Maximum Age", "type":'multi',
                        'multi':[{'name':'agevalue','label':'Maximum Age', 'type':'text', 'size':2},
                        {'name':'maxagefield', 'type':'select',
                        'options':[('','-')]+[('day','day(s)'),('week','week(s)'),('month','month(s)')]}]})

    if not map:
        filters.append({'label':"Sort On", "type":'multi',
                            'multi':[
                            {'name':'sort_field','type':'select',
                            'options':[('','-')]+
                                [('fleet.location','Location'),
#                                 ('fleet.size','Minimal Size'),
                                  ('fleet_sum','Fleet Size/Sum'),
                                 ('arrival','Arrival'),
                                ('fleet.timestamp','Age'),
                                ('fleet.ownerid','Owner ID'),
                                ('fleet.owner.name','Owner Name'),
                                ('guild.id','Owner Guild ID'),
                                ('guild.tag','Owner Guild Tag'),
                                ]},
                            {'name':'sort_order', 'type':'select',
                            'options':[('asc','Ascending')]+[('desc','Descending'),]}

                            ]})
    if not map:
        filters.append({'name':'group_by','label':"Group By", "type":'select',
                            'options':[('','Normal')]+
                                [
                                ('owner-01','Location, Owner'),
                                ('owner-02','Galaxy, Owner'),
                                ('owner-03','Galaxy-Group, Owner'),
                                ('blob-01','Location, Guild'),
                                ('blob-02','Galaxy, Guild'),
                                ('blob-03','Galaxy-Group, Guild'),
                                ]})
    if not map:
        filters.append({'name':'per_page','label':"Results per Page", 'type':'select',
                        'options':[((x*100),"%s"%(x*100)) for x in range(1,6)]})

    return filters
def getFieldFilters():
    fieldfilters = []
    fieldfilters.append({'name':'show_lsd','label':"(Average) Age of Fleet Location"})
    fieldfilters.append({'name':'show_lsdd','label':"(Average) Age of Fleet Details"})
    fieldfilters.append({'name':'show_lsp','label':"Last Scouter"})
    return fieldfilters
