#!/usr/bin/env python

'''
work out total flight time for a mavlink log
'''

import sys, time, os, glob
import os, sys
from math import *

from argparse import ArgumentParser
parser = ArgumentParser(description=__doc__)
parser.add_argument("--condition", default=None, help="condition for packets")
parser.add_argument("--groundspeed", type=float, default=3.0, help="groundspeed threshold")
parser.add_argument("logs", metavar="LOG", nargs="+")

args = parser.parse_args()

from pymavlink import mavutil


def distance_two(GPS_RAW1, GPS_RAW2):
    '''distance between two points'''
    if hasattr(GPS_RAW1, 'Lat'):
      lat1 = radians(GPS_RAW1.Lat)
      lat2 = radians(GPS_RAW2.Lat)
      lon1 = radians(GPS_RAW1.Lon)
      lon2 = radians(GPS_RAW2.Lon)
    elif hasattr(GPS_RAW1, 'cog'):
      lat1 = radians(GPS_RAW1.Lat)*1.0e-7
      lat2 = radians(GPS_RAW2.Lat)*1.0e-7
      lon1 = radians(GPS_RAW1.Lon)*1.0e-7
      lon2 = radians(GPS_RAW2.Lon)*1.0e-7
    else:
      lat1 = radians(GPS_RAW1.lat)
      lat2 = radians(GPS_RAW2.lat)
      lon1 = radians(GPS_RAW1.lon)
      lon2 = radians(GPS_RAW2.lon)
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    a = sin(0.5*dLat)**2 + sin(0.5*dLon)**2 * cos(lat1) * cos(lat2)
    c = 2.0 * atan2(sqrt(a), sqrt(1.0-a))
    return 6371 * 1000 * c

def flight_time(logfile):
    '''work out flight time for a log file'''
    print("Processing log %s" % filename)
    mlog = mavutil.mavlink_connection(filename)

    in_air = False
    start_time = 0.0
    total_time = 0.0
    total_dist = 0.0
    t = None
    last_msg = None

    while True:
        m = mlog.recv_match(type=['GPS','GPS_RAW_INT'], condition=args.condition)
        if m is None:
	    print "I am empty !"
            if in_air:
                total_time += time.mktime(t) - start_time
            if total_time > 0:
                print("Flight time : %u:%02u" % (int(total_time)/60, int(total_time)%60))
            return (total_time, total_dist)
        if m.get_type() == 'GPS_RAW_INT':
            groundspeed = m.vel*0.01
            status = m.fix_type
            print "Status:" + status
        else:
            groundspeed = m.VelE
            status = m.Fix            
        if status < 3:
            continue
        t = time.localtime(m._timestamp)
        if groundspeed > args.groundspeed and not in_air:
            print("In air at %s (percent %.0f%% groundspeed %.1f)" % (time.asctime(t), mlog.percent, groundspeed))
            in_air = True
            start_time = time.mktime(t)
        elif groundspeed < args.groundspeed and in_air:
            print("On ground at %s (percent %.1f%% groundspeed %.1f  time=%.1f seconds)" % (
                time.asctime(t), mlog.percent, groundspeed, time.mktime(t) - start_time))
            in_air = False
            total_time += time.mktime(t) - start_time

        if last_msg is not None:
            total_dist += distance_two(last_msg, m)
        last_msg = m
    return (total_time, total_dist)

total_time = 0.0
total_dist = 0.0
for filename in args.logs:
    for f in glob.glob(filename):
        (ftime, fdist) = flight_time(f)
        total_time += ftime
        total_dist += fdist

print("Total time in air: %u:%02u" % (int(total_time)/60, int(total_time)%60))
print("Total distance trevelled: %.1f meters" % total_dist)
