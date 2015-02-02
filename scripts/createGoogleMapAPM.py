#!/usr/bin/env python

'''
example program to extract GPS data from a mavlink log, and create a GPX
file, for loading into google earth
'''

import sys, struct, time, os
import math
import pygmaps 

from argparse import ArgumentParser
parser = ArgumentParser(description=__doc__)
parser.add_argument("--condition", default=None, help="select packets by a condition")
parser.add_argument("--nofixcheck", default=False, action='store_true', help="don't check for GPS fix")
parser.add_argument("logs", metavar="LOG", nargs="+")
args = parser.parse_args()

from pymavlink import mavutil


def mav_to_gpx(infilename, outfilename):
    '''convert a mavlink log file to a GPX file'''

    mlog = mavutil.mavlink_connection(infilename)
    outf = open(outfilename, mode='w')

    def process_packet(timestamp, lat, lon, alt, hdg, v):
        t = time.localtime(timestamp)
        outf.write('''<trkpt lat="%s" lon="%s">
  <ele>%s</ele>
  <time>%s</time>
  <course>%s</course>
  <speed>%s</speed>
  <fix>3d</fix>
</trkpt>
''' % (lat, lon, alt,
       time.strftime("%Y-%m-%dT%H:%M:%SZ", t),
       hdg, v))

    def add_header():
        outf.write('''<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.0"
  creator="pymavlink"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/0"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<trk>
<trkseg>
''')

    def add_footer():
        outf.write('''</trkseg>
</trk>
</gpx>
''')

    add_header()
    global mymap
    global prevSatCount
    path = []
    count=0
    while True:
        m = mlog.recv_match(type=['GPS', 'GPS_RAW_INT'], condition=args.condition)
        if m is None:
            break
        if m.get_type() == 'GPS_RAW_INT':
            lat = m.lat/1.0e7
            lon = m.lon/1.0e7
            alt = m.alt/1.0e3
            v = m.vel/100.0
            hdg = m.cog/100.0
            timestamp = m._timestamp
        else:
            lat = m.Lat
            lon = m.Lng
            alt = m.Alt
            v   = m.Spd#math.sqrt(m.VelN*m.VelN + m.VelE*m.VelE)**0.5
            hdg = m.HDop
            timestamp = m._timestamp
            if count == 0:
              mymap = pygmaps.maps(lat, lon, 18)
              prevSatCount = m.NSats
            if m.NSats <= 8:
              color = "#FF0000"
            if m.NSats == 9:
              color = "#0000FF"
            if m.NSats == 10:
              color = "#FFFF00"
            if m.NSats >= 11:
              color = "#00FF00"              
            #mymap.addpoint(lat, lon, "#0000FF")  
            path.append((lat,lon))
            if m.NSats != prevSatCount:
              mymap.addpath(path,color)
              path = []
            prevSatCount = m.NSats
            
        if m.Status < 2 and not args.nofixcheck:
            continue
        if m.Lat == 0.0 or m.Lng == 0.0:
            continue
        process_packet(timestamp, lat, lon, alt, hdg, v)
        count += 1
        #if count == 10000:
        #  break
    add_footer()
    print("Created %s with %u points" % (outfilename, count))
    mymap.addpath(path,"#00FF00")
    mymap.draw('./mymap.html')

for infilename in args.logs:
    outfilename = infilename + '.gpx'
    mav_to_gpx(infilename, outfilename)
