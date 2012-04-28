from cister.db.models.cister import DBSession, Base, Fleet
from cister.db.views import BaseCisterView
from cister.db.views.base.search import getBaseFilters, performBaseFilter
from cister.db.views.fleet.search import getFleetFilters, performFleetFilter
from datetime import datetime
from cister.db.helpers import getAgeLegenda, getCountColor, getCountLegenda
import time
import math 
from sqlalchemy import or_,func, select
import webhelpers.paginate as paginate
from webhelpers.util import update_params
from datetime import timedelta
from cister.db.views.map.generic import makeLocationDict

class GalaxyView(BaseCisterView):

    def __init__(self, request):
        self.request = request
        self.basefilters = getBaseFilters(map=True)
        self.fleetfilters = getFleetFilters(map=True)

    def __call__(self):
        dbsession = DBSession()
        returnvalue = {'location':None}
        location = "A"
        location = "%s%s" % (location, self.request.matchdict.get("galaxy"))

        regions = {}
        legenda = None
        bases = None
        params = {}

        base_search = False
        fleet_search = False
        
        if "form.base_submitted" in self.request.params:
            base_search = True
            params = self.request.params
        elif "form.fleet_submitted" in self.request.params:
            fleet_search = True
            params = self.request.params
        elif self.request.cookies.get('search','') == 'base':
            base_search = True
            params = self.request.cookies
        elif self.request.cookies.get('search','') == 'fleet':
            fleet_search = True
            params = self.request.cookies

        # .outerjoin(Base).filter(Location.location.like("%s%%"%location))
        if base_search:
            regions = makeLocationDict(dbsession, location, 1, 6, 4, 5, do_base=False)
            bases, legenda, regions = self.processBase(dbsession, params, regions, location,  1, 6)
            label = ''
            cookie_key = ['owner','occupier','jumpgate','agevalue', 'maxagefield']
            cookie_set= False

            if "form.base_submitted" in self.request.params:
                for key in cookie_key:
                    if self.request.params.get(key,''):
                        cookie_set = True
                        self.request.response.set_cookie(key, self.request.params.get(key), max_age=timedelta(days=1), path='/')
                    else:
                        self.request.response.delete_cookie(key)

                    if cookie_set:
                        self.request.response.set_cookie('search', 'base', max_age=timedelta(days=1), path='/')
        elif fleet_search:
            fleets = dbsession.query(func.substring(Fleet.location,1,6).label('location'),\
                    func.count('*').label('fleet_count'), \
                    func.sum(Fleet.size).label("fleet_sum"), \
                    select(["FROM_UNIXTIME(AVG(UNIX_TIMESTAMP(fleet.timestamp)))"]).label("average_age")).\
                    group_by(func.substring(Fleet.location,1,6)).filter(Fleet.location.like("%s%%"%location))
            fleets = performFleetFilter(fleets, self.request.params)
            regions = makeLocationDict(dbsession, location, 1, 6, 4, 5, do_base=False)

            cookie_key = ['owner','size','flying','agevalue', 'maxagefield']
            cookie_set= False

            if "form.fleet_submitted" in self.request.params:
                for key in cookie_key:
                    if self.request.params.get(key,''):
                        cookie_set = True
                        self.request.response.set_cookie(key, self.request.params.get(key), max_age=timedelta(days=1), path='/')
                    else:
                        self.request.response.delete_cookie(key)

                    if cookie_set:
                        self.request.response.set_cookie('search', 'fleet', max_age=timedelta(days=1), path='/')

            min_count = 1
            max_count = 1000000
            for fleet_location, fleet_count, fleet_sum, fleet_age in fleets:
                fleet_sum = fleet_sum / 1000
                row = int(fleet_location[4])
                col = int(fleet_location[5])
                location_info = regions[row][col]
                location_info['fleet_count'] = fleet_count
                location_info['fleet_sum'] = fleet_sum
#                if fleet_sum > max_count:
#                    max_count = fleet_sum
#                if fleet_sum < min_count or min_count == None:
#                    min_count = fleet_sum
#                location_info['base_age'] = getCountColor(base_count)
                regions[row][col] = location_info
            legenda = getCountLegenda(min=min_count,max=max_count, single='fleet', plural='fleets')

            for fleet_location, fleet_count, fleet_sum, fleet_age in fleets:
                row = int(fleet_location[4])
                col = int(fleet_location[5])
                location_info = regions[row][col]
                location_info['base_age'] = getCountColor(math.trunc(fleet_sum), min=min_count,max=max_count, single='fleet', plural='fleets')
            label = 'Fleet sum:'
        else:
            regions = makeLocationDict(dbsession, location, 1, 6, 4, 5)
            label = 'Avg. age'
            legenda = getAgeLegenda()


        returnvalue = {'base_filters': self.basefilters,
                       'fleet_filters': self.fleetfilters,
                       'label': label,
                       'params': params,
                       'bases':bases,
                       'location':location,
                       'regions': regions,
                       'legenda': legenda,
                       'datetime':datetime}
        returnvalue.update(self.request.matchdict)
        return returnvalue


    def processBase(self, dbsession, params, thedict, location,  group1, group2):
        bases = dbsession.query(func.substring(Base.location,group1,group2).label('location'), func.count('*').\
         label('base_count'), select(["FROM_UNIXTIME(AVG(UNIX_TIMESTAMP(base.timestamp)))"]).label("average_age")).\
         group_by(func.substring(Base.location,group1, group2)).filter(Base.location.like("%s%%"%location))

        bases = performBaseFilter(bases, params)
        max_count = 0
        min_count = 99999999999

        for base_location,base_count,base_age in bases:
            row = int(base_location[-2])
            col = int(base_location[-1])
            thedict[row][col]['base_count'] = base_count
            if base_count > max_count:
                max_count = base_count
            if base_count < min_count:
                min_count = base_count
#                location_info['base_age'] = getCountColor(base_count)
        legenda = getCountLegenda(min=min_count,max=max_count, single='base', plural='bases')

        for base_location,base_count,base_age in bases:
            row = int(base_location[-2])
            col = int(base_location[-1])
            thedict[row][col]['base_age'] = getCountColor(base_count, min=min_count,max=max_count, single='base', plural='bases')
        def url_generator(**kw):
            new_url = update_params(self.request.url, page=kw['page'])
            return new_url
        bases = dbsession.query(Base).filter(Base.location.like("%s%%"%location))
        bases = performBaseFilter(bases, params)
        bases = paginate.Page(bases, page=int(self.request.params.get('page', 1)), items_per_page=200, url=url_generator, item_count=bases.count())
        return bases, legenda, thedict
