from cister.db.models.cister import Base
from cister.db.models.cister import Fleet
from cister.db.models.cister import Location
from cister.db.models.cister import DBSession
from datetime import datetime
from cister.db.views import BaseCisterView

from sqlalchemy.orm import lazyload

class SystemView(BaseCisterView):

    def __call__(self):
        dbsession = DBSession()
        location = "A"
        location = "%s%s" % (location, self.request.matchdict.get("galaxy"))
        location = "%s:%s" % (location, self.request.matchdict.get("region"))
        location = "%s:%s" % (location, self.request.matchdict.get("system"))

        astros = dbsession.query(Location)\
                                .options(lazyload('base.submitter'))\
                                .options(lazyload('fleets.owner'))\
                                .options(lazyload('fleets.updater'))\
                                .options(lazyload('fleets.submitter'))\
                                .filter(Location.location.like("%s%%"%location))
        locationdetail = {}
        fleetlocations = []
#        for base in bases:
            

        astrocolumns = 0
        fleetstrings = {}
        locations = {}
        for astro in astros:

            if astro.base:
                locationdetail[astro.location] = { "owner_id":astro.base.ownerid, "owner_guild_id": astro.base.owner.guild and astro.base.owner.guild.id or -1}

            fleetlocations.append(astro.location)
            if int(astro.location[10]) > astrocolumns:
                astrocolumns = int(astro.location[10])

            fleets = []
            for fleet in astro.fleets:
                locdetail = locationdetail.get(fleet.location, {})
                fleetdetail = fleetstrings.get(fleet.location, {"owner":0, "guild":0, "other":0})
                if fleet.owner.id == locdetail.get("owner_id", -1000):
                    fleetdetail['owner'] = fleetdetail.get('owner',0) + fleet.size
                elif fleet.owner.guild and fleet.owner.guild.id == locdetail.get("owner_guild_id", -1000):
                    fleetdetail['guild'] = fleetdetail.get('guild',0) + fleet.size
                else:
                    fleetdetail['other'] = fleetdetail.get('other',0) + fleet.size
                fleetstrings[fleet.location] = fleetdetail
                fleets.append(fleet)

            locations[astro.location] = {'location':astro.location,
                                         'terrain':astro.terrain.name,
                                         'size': astro.location[11]=='0' and '50' or '30',
                                         'base':astro.base or None,
                                         'fleets': fleets}
            if astro.terrain.name == 'Asteroid':
                locations[astro.location]['size'] = 20;

        
        locations = locations.values()
        locations = sorted(locations, key= lambda k: k['location'])

        returnvalue = {'location':location,
                       'columns':astrocolumns,
                       'locations':locations,
                       'astros':astros,
                       'fleets':fleetstrings,
                       'datetime':datetime}
        returnvalue.update(self.request.matchdict)

        return returnvalue
