from sqlalchemy import or_, asc, desc

from cister.db.models.cister import Base, Player, GuildInfo
from cister.db.models.cister import Fleet
from cister.db.models.cister import DBSession
from datetime import datetime, timedelta
import re
import webhelpers.paginate as paginate
from webhelpers.util import update_params
from cister.db.views.viewbase import BaseCisterView

guild_id_pattern = re.compile("\[([-+]\d+)\]")
guild_tag_pattern = re.compile("\[(.{1,8})\]")
id_pattern = re.compile("(\d+)")

BaseTable = Base.__table__

class BaseSearchView(BaseCisterView):


    def __init__(self, request):
        self.request = request
        self.filters = getBaseFilters()
        self.fieldfilters = getFieldFilters()

    def __call__(self):
        dbsession = DBSession()
        bases=None
        fleetstrings = {}
        params = self.request.params


        if "form.submitted" in self.request.params:
            def url_generator(**kw):
                new_url = update_params(self.request.url, page=kw['page'])
                return new_url

            params = self.request.params

            bases = dbsession.query(Base)

            bases = performBaseFilter(bases, params)

            ##Sorting

            if 'sort_field' in self.request.params and self.request.params.get('sort_field') != '':
                bases = performBaseSort(bases, self.request.params)
                
#

                
            ##Limits and such
            per_page = int(self.request.params.get('per_page') or 100)
            bases = paginate.Page(bases, page=int(self.request.params.get('page', 1)), items_per_page=per_page, url=url_generator, item_count=bases.count())

            if 'show_ofs' in self.request.params:
                locationdetail = {}
                fleetlocations = []
                for base in bases:
                    locationdetail[base.location] = { "owner_id":base.ownerid, "owner_guild_id":(base.owner and base.owner.guild) and base.owner.guild.id or -1}
                    fleetlocations.append(base.location)

                fleets = dbsession.query(Fleet).filter(Fleet.location.in_(fleetlocations)).all()

                fleetstrings = {}

                for fleet in fleets:
                    locdetail = locationdetail.get(fleet.location)
                    fleetdetail = fleetstrings.get(fleet.location, {})
                    if fleet.ownerid == locdetail.get("owner_id"):
                        fleetdetail['owner'] = fleetdetail.get('owner',0) + fleet.size
                    elif (fleet.owner and fleet.owner.guild) and fleet.owner.guild.id == locdetail.get("owner_guild_id"):
                        fleetdetail['guild'] = fleetdetail.get('guild',0) + fleet.size
                    else:
                        fleetdetail['other'] = fleetdetail.get('other',0) + fleet.size
                    fleetstrings[fleet.location] = fleetdetail

        return {"filters": self.filters,
                "fieldfilters" : self.fieldfilters,
                "bases":bases,
                "params":params,
                "fleetstrings":fleetstrings,
                "datetime":datetime}

def performBaseFilter(bases, params):
    """Assumptions: Base is a query object.
    Already filtered, or just the base query.
    Params is params
    """
    if 'location' in params and params.get('location') != '':
        locations = params.get('location').strip().split(',')
        qrs = []
        for location in locations:
            qrs.append(Base.location.like("%s%%" % location))
        bases = bases.filter(or_(*qrs))

    if 'owner' in params and params.get('owner') != '':
        owners = params.get('owner').split(',')
        qrs = []
        for owner in owners:
            if guild_id_pattern.match(owner):
                id_match = guild_id_pattern.match(owner).groups()[0]
                qrs.append(
                    Base.owner.has(
                        Player.guild.has(
                            GuildInfo.id==id_match
                        )
                    )
                )
            elif guild_tag_pattern.match(owner):
                guild_match=guild_tag_pattern.match(owner).groups()[0]
                qrs.append(
                    Base.owner.has(
                        Player.guild.has(
                            GuildInfo.tag==guild_match
                        )
                    )
                )
            elif id_pattern.match(owner):
                qrs.append(Base.ownerid==owner)
            else: ##Must be name
                qrs.append(Base.owner.has(Player.name.like("%%%s%%"% owner)))
        

        bases = bases.filter(or_(*qrs))
    if 'occupier' in params and params.get('occupier') != '':
        occupiers = params.get('occupier').split(',')
        qrs = []
        for occupier in occupiers:
            if guild_id_pattern.match(occupier):
                id_match = guild_id_pattern.match(occupier).groups()[0]
                qrs.append(
                    Base.occupier.has(
                        Player.guild.has(
                            GuildInfo.id==id_match
                        )
                    )
                )
            elif guild_tag_pattern.match(occupier):
                guild_match=guild_tag_pattern.match(occupier).groups()[0]
                qrs.append(
                    Base.occupier.has(
                        Player.guild.has(
                            GuildInfo.tag==guild_match
                        )
                    )
                )
            elif id_pattern.match(occupier):
                qrs.append(Base.occupierid==occupier)
            else: ##Must be name
                qrs.append(Base.occupier.has(Player.name.like("%%%s%%"% occupier)))
                
        bases = bases.filter(or_(*qrs))

    if 'jumpgate' in params and params.get('jumpgate') != '':
        jumpgate = params.get('jumpgate')
        bases = bases.filter(Base.jg >= jumpgate)

    if 'agevalue' in params and params.get('agevalue') != '':
        if 'maxagefield' in params and params.get('maxagefield') != '':
            days = int(params.get('agevalue'))
            maxagefield = params.get('maxagefield')
            multiplier = {'day':1, 'week':7, 'month':30}
            days = int(days * multiplier[maxagefield])
            maxAge= datetime.now() - timedelta(days=days)
            bases = bases.filter(Base.timestamp >= maxAge)
    return bases

def performBaseSort(bases, params):
    sort_field = params.get('sort_field')
    sort_order = params.get('sort_order')
    order = desc
    if sort_order =='asc':
        order = asc

    if sort_field == 'base.timestamp':
        ##Timestamp needs it's order reverted to make sense..
        fixer = {'asc':desc, 'desc':asc}
        order = fixer.get(sort_order)

    if 'base.location' in sort_field:
        bases = bases.order_by(order(Base.location))

    elif 'base.timestamp' in sort_field:
        bases = bases.order_by(order(Base.timestamp))
    elif 'base.ownerid' in sort_field:
        bases = bases.order_by(order(Base.ownerid))
    elif 'base.occupierid' in sort_field:
        bases = bases.order_by(order(Base.occupierid))

    elif "guild.id" in sort_field or "guild.tag" in sort_field:

        order = desc
        if sort_order =='asc':
            order = asc

        if 'occupier' in sort_field:
            bases = bases.join(Base.occupier)
        else:
            bases = bases.join(Base.owner)
        bases = bases.join(Player.guild)

        if "guild.tag" in sort_field:
            bases = bases.order_by(order(GuildInfo.tag))
        else:
            bases = bases.order_by(order(GuildInfo.id))

    else: ##Owner or Occupier name
        if 'occupier' in sort_field:
            bases = bases.join(Base.occupier)
        else:
            bases = bases.join(Base.owner)
        bases = bases.order_by(order(Player.name))
    return bases

def getBaseFilters(map=False):
    filters = []
    if not map:
        filters.append({'name':'location','label':"Location", 'type':'text', 'size':12})
    filters.append({'name':'owner','label':"Owner", 'type':'text'})
    filters.append({'name':'occupier','label':"Occupier", 'type':'text'})
    filters.append({'name':'jumpgate','label':"Jump Gate", 'type':'select',
                        'options':[('','-')]+[(x,"Level %s +"%x) for x in range(1,15)]})

    filters.append({'label':"Maximum Age", "type":'multi',
                        'multi':[{'name':'agevalue','label':'Maximum Age', 'type':'text', 'size':2},
                        {'name':'maxagefield', 'type':'select',
                        'options':[('','-')]+[('day','day(s)'),('week','week(s)'),('month','month(s)')]}]})

    if not map:
        filters.append({'label':"Sort On", "type":'multi',
                        'multi':[
                        {'name':'sort_field','type':'select',
                        'options':[('','-')]+
                            [("base.location",'Location'),
                            ("base.timestamp",'Age'),
                            ("base.ownerid",'Owner ID'),
                            ("base_owner.name",'Owner Name'),
                            ("base_owner.guild.id",'Owner Guild ID'),
                            ("base_owner.guild.tag",'Owner Guild Tag'),
                             ("base.occupierid",'Occupier ID'),
                            ("base_occupier.name",'Occupier Name'),
                            ("base_occupier_guild.id",'Occupier Guild ID'),
                            ("base_occupier_guild.tag",'Occupier Guild Tag'),
                            ]},
                        {'name':'sort_order', 'type':'select',
                        'options':[('asc','Ascending')]+[('desc','Descending'),]}

                        ]})
    if not map:
        filters.append({'name':'per_page','label':"Results per Page", 'type':'select',
                        'options':[((x*100),"%s"%(x*100)) for x in range(1,6)]})

    return filters


def getFieldFilters():
    fieldfilters = []
    fieldfilters.append({'name':'show_occ','label':"Occupier"})
    fieldfilters.append({'name':'show_eco','label':"Economy"})
    fieldfilters.append({'name':'show_ofs','label':"Fleet Sums"})
    fieldfilters.append({'name':'show_cc','label':"Command Center"})
    fieldfilters.append({'name':'show_jg','label':"Jump gate"})
    fieldfilters.append({'name':'show_def','label':"Defenses"})
    fieldfilters.append({'name':'show_cap','label':"Capital"})
    fieldfilters.append({'name':'show_lsd','label':"Age of Base"})
#        fieldfilters.append({'name':'show_lsfd','label':"Last Fleet Scouted"})
    fieldfilters.append({'name':'show_lsdd','label':"Age of Base Details"})
    fieldfilters.append({'name':'show_lsp','label':"Last Scouter"})


    return fieldfilters


    pass
