from cister.db.models.cister import Base
from cister.db.models.cister import Fleet
from cister.db.models.cister import Location
from cister.db.models.cister import DBSession
from datetime import datetime
from cister.db.views import BaseCisterView
from cister.db.helpers import createBlobDetails


class AstroView(BaseCisterView):

    def __call__(self):
        dbsession = DBSession()
        location = "A"
        location = "%s%s" % (location, self.request.matchdict.get("galaxy"))
        location = "%s:%s" % (location, self.request.matchdict.get("region"))
        location = "%s:%s" % (location, self.request.matchdict.get("system"))
        location = "%s:%s" % (location, self.request.matchdict.get("astro"))

        astro = dbsession.query(Location).filter(Location.location==location).one()
        base = astro.base
        fleets = dbsession.query(Fleet).filter(Fleet.location==location)
        fleets = fleets.order_by("arrival-(unix_timestamp(now())-unix_timestamp(fleet.timestamp)) > 0 ASC, arrival ASC, size DESC")
        fleets_count = fleets.count()
        if fleets_count == 0:
            fleets = []


        blobdetails = createBlobDetails(location, fleets)
        blobdetails = blobdetails.values()
        def blobsize_compare(x, y):
            xsum = x['sum']
            ysum = y['sum']
            return int(ysum - xsum)
        blobdetails = sorted(blobdetails, cmp=blobsize_compare)

        returnvalue = { 'location':location,
                        'astrolocation':astro,
                        'base':base,
                        'fleets':fleets,
                        'fleets_count':fleets_count,
                        'datetime':datetime,
                        'blobdetails':blobdetails
        }
        returnvalue.update(self.request.matchdict)
        return returnvalue

