from math import floor, trunc
import time
import random
from sqlalchemy import func, select
from datetime import datetime
from cister.db.models.cister import Base
from cister.db.models.cister import Location
from cister.db.helpers import getAgeColorTimedelta, getAgeColor


def makeLocationDict(dbsession, location, group1, group2, row_index, col_index, do_base=True):
    if do_base:
        bases = dbsession.query(func.substring(Base.location,group1,group2).label('location'), func.count('*').\
         label('base_count'), select(["FROM_UNIXTIME(AVG(UNIX_TIMESTAMP(base.timestamp)))"]).label("average_age")).\
         group_by(func.substring(Base.location,group1,group2)).filter(Base.location.like("%s%%"%location))


    astros = dbsession.query(Location.location,func.count(Location.location).label('astro_count'))
    astros = astros.filter(Location.location.like("%s%%"%location))
    astros = astros.group_by(func.substring(Location.location,group1,group2))

    locations = {}
    for row in range(0,10):
        locations[row] = {}
        for col in range(0,10):
            locations[row][col]={'astro_count':0, 'base_count':0, 'base_age':{}}

    for astro,astro_count in astros:
        row = int(astro[row_index])
        col = int(astro[col_index])
        location_info = locations[row][col]
        location_info['astro_count'] = astro_count
        if do_base:
            location_info['base_count'] = 0
            location_info['base_age'] = {}
        locations[row][col] = location_info

    if do_base:
        for base_location,base_count,base_age in bases:
            row = int(base_location[-2])
            col = int(base_location[-1])
            location_info = locations[row][col]
            location_info['base_count'] = base_count
            location_info['base_age'] = getAgeColorTimedelta(datetime.now() - base_age)
            locations[row][col] = location_info

    return locations

