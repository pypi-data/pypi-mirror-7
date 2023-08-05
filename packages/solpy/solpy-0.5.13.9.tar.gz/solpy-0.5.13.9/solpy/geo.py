# Copyright (C) 2013 Nathan Charles
#
# This program is free software. See terms in LICENSE file.
"""helper functions for geographical information"""

import csv
import math
import os
from tools import memoized
SPATH = os.path.dirname(os.path.abspath(__file__))

def stationInfo(usaf):
    index = open(SPATH + '/StationsMeta.csv')
    index_data = csv.DictReader(index)
    for i in index_data:
        if usaf == i['USAF']:
            index.close()
            return i
    raise Exception('Station not found')

def closestUSAF(place, stationClass=3):
    """Find closest USAF code of a given station class"""
    latitude,longitude = place
    index = open(SPATH + '/StationsMeta.csv')
    index_data = csv.DictReader(index)
    d1 = 9999
    name = ''
    usaf = ''
    for i in index_data:
        d2 = math.sqrt(math.pow((float(i['Latitude']) - latitude),2) + \
                math.pow((float(i['Longitude']) - longitude),2))
        uncertainty = len(i['Class'])
        if d2 < d1 and uncertainty <= stationClass:
            d1 = d2
            name = i['Site Name']
            usaf = i['USAF']
    index.close()
    return name, usaf

@memoized
def zipToCoordinates(zipcode):
    """zipcode to latitude and longitude, takes a string because some zipcodes
    start with 0"""
    index = open(SPATH + '/zipcode.csv')
    #read over license
    headerLen = 31
    for i in range(headerLen):
        index.readline()
    index_data = csv.DictReader(index)
    for i in index_data:
        if i['zip'] == zipcode:
            return float(i['latitude']),float( i['longitude'])

@memoized
def zipToTZ(zipcode):
    """find TZ for zipcode"""
    index = open(SPATH + '/zipcode.csv')
    #read over license
    headerLen = 31
    for i in range(headerLen):
        index.readline()
    index_data = csv.DictReader(index)
    for i in index_data:
        if i['zip'] == zipcode:
            return int(i['timezone'])
