from cister.db.views import BaseCisterView
from cister.db.models.cister import Base
from cister.db.models.cister import Location
from cister.db.models.cister import DBSession
from datetime import datetime
from cister.db.helpers import getAgeColorTimedelta,twodigitNumbers, getAgeLegenda
import time
from sqlalchemy import func, select

class MapView(BaseCisterView):
    pass

    def __call__(self):
        dbsession = DBSession()
        bases = dbsession.query(Base.loc_gal, func.count('*').\
         label('base_count'), select(["FROM_UNIXTIME(AVG(UNIX_TIMESTAMP(base.timestamp)))"]).label("average_age")).\
         group_by(Base.loc_gal)

        astros = dbsession.query(Location.loc_gal,func.count(Location.location).label('astro_count'))
        astros = astros.group_by(Location.loc_gal)

        galaxies = {}

        for row in range(0,80):
            galaxies["A%s"%twodigitNumbers(row)] = {}

        for astro_location,astro_count in astros:
            row = astro_location
            galaxy_info = galaxies[row]
            galaxy_info['astro_count'] = astro_count
            galaxy_info['base_count'] = 0
            galaxy_info['base_age'] = -1

        for base_location, base_count, base_age in bases:
            row = base_location
            if row:
                galaxy_info = galaxies[row]
                galaxy_info['base_count'] = base_count
                galaxy_info['base_age'] = getAgeColorTimedelta(datetime.now() - base_age)
                galaxies[row] = galaxy_info


        legenda = getAgeLegenda()

        return {'galaxies':galaxies,
                'legenda':legenda,
                'datetime':datetime}
