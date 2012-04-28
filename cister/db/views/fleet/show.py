from cister.db.views import BaseCisterView
from cister.db.models.cister import DBSession, Fleet

class FleetView(BaseCisterView):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        dbsession = DBSession()
        returnvalue = {}
        returnvalue.update(self.request.matchdict)
        fleetid = returnvalue.get('fleetid')

        fleet = dbsession.query(Fleet).filter(Fleet.id==fleetid).one()

        returnvalue['fleet'] = fleet

        return returnvalue
