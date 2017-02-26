"""
Mapping functions
"""

#pylint: disable=invalid-name, missing-docstring, no-member

from __future__ import print_function
from mpl_toolkits.basemap import Basemap
import pandas
import math

def create_map(lon, lat):
    """
    Create a map projection.
    """
    #to avoid nan values    
    index1 = 0
    for d in lon:
      if math.isnan(d):
          index1 = index1 + 1

    index2 = 0
    for d in lat:
      if math.isnan(d):
          index2 = index2 + 1

    index = 0 
    if index2 >= index1:
        index = index2
    else:
        index = index1
        
    lon_center = lon[index]
    lat_center = lat[index]
    return Basemap(
        lon_0=lon_center,
        lat_0=lat_center, projection='tmerc',
        width=1e-5, height=1e-5)


def project_lat_lon(df):

    #to avoid nan values  
    index1 = 0
    for d in df.GPS_Lat.values:
      if math.isnan(d):
          index1 = index1 + 1

    index2 = 0
    for d in df.GPS_Lon.values:
      if math.isnan(d):
          index2 = index2 + 1

    index = 0 
    if index2 >= index1:
        index = index2
    else:
        index = index1
        
    gps_map = Basemap(lat_0=df.GPS_Lat.values[index],
            lon_0=df.GPS_Lon.values[index],
            width=11e-5, height=1e-5, projection='tmerc')
    gps_y, gps_x = gps_map(df.GPS_Lon.values, df.GPS_Lat.values)
    gps_z = df.GPS_Alt - df.GPS_Alt.values[index]
    df_new = pandas.DataFrame(pandas.DataFrame({
        'GPS_X': gps_x, 'GPS_Y': gps_y, 'GPS_Z': gps_z}, index=df.index))
    return pandas.concat([df, df_new], axis=1)

# vim: set et fenc= ff=unix sts=0 sw=4 ts=4 :
