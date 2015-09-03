#!/usr/bin/python

import json
import sys
from optparse import OptionParser

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def condense_place_climate_json(climate_json):
    '''
    Condense a JSON entry for a particular place to something much more compact:

    i.e.
    {'lat': 10, 'lon': -15, 'name': 'Springfield', 'population': 1000,
    'condensed_climate', [[300, 21, -8, 181],[...],...]

    Where condensed_climate has an array for each month with
    [sunshine, high C, low C, precipitation] in each array.

    @param climate_json: A climate json entry
    @return: A condensed climate json
    '''
    condensed_climate = {'lat': climate_json['lat'],
                         'lon': climate_json['lon'],
                         'name': climate_json['name'],
                         'cclim': []}
    for month in months:
        if 'snow cm' not in climate_json['climate'][month]:
            climate_json['climate'][month]['snow cm'] = 'x'

        condensed_climate['cclim'] += [[climate_json['climate'][month]['sun'],
                                       climate_json['climate'][month]['high C'],
                                       climate_json['climate'][month]['low C'],
                                       climate_json['climate'][month]['precipitation mm'],
                                       climate_json['climate'][month]['snow cm']]]

    return condensed_climate

def addRainToPrecipitation(climate):
    '''
    If a climate entry has rain and no precipitation, add
    the rain to the precipitation column.

    @param climate: A dictionary with month abbreviations as the keys:
    @return: The climate object
    '''
    for month in months:
        if 'precipitation mm' not in climate[month]:
            if 'rain mm' in climate[month]:
                climate[month]['precipitation mm'] = climate[month]['rain mm']

    return climate

def hasAllProperty(climate, prop):
    '''
    Make sure each month of the climate has a property entry.

    @param climate: A dictionary with month abbreviations as the keys
    @param prop: The property to check for.
    @return: If each month has a property entry, false otherwise.
    '''
    for month in months:
        if prop not in climate[month]:
            return False
    return True

def hasAllMonths(climate):
    '''
    Check if this climate objects has all months in it.

    @param climate: A dictionary with month abbreviations as the keys
    @return: True if all months are present, False otherwise
    '''

    for month in months:
        if month not in climate:
            return False

    return True

def main():
    usage = """
    python consolidate_climates.py climates.json

    Create a list out of each individual line in climates.json.

    i.e.
    
    a
    b
    c
    
    becomes

    [a,b,c]
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    parser.add_option('-w', '--weather-coordinates', dest='weather_coordinates', default=None, help='The coordinates for all locations that have weather data.')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    # load the weather coordinates
    weather_coordinates = None

    if options.weather_coordinates is not None:
        weather_coordinates = dict()
        with open(options.weather_coordinates, 'r') as f:
            for line in f:
                location = json.loads(line.strip())
                weather_coordinates[location['title']] = location

    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    to_output = '['

    lines = []
    lats = []

    lat_lons_set = set()
    for line in f:
        climate_json = json.loads(line)

        # check if we have a set of weather coordinates
        if weather_coordinates is not None:
            if climate_json['name'] in weather_coordinates:
                print >>sys.stderr, "found location:", climate_json['name']

                location = weather_coordinates[climate_json['name']]
                climate_json['lat'] = location['coordinates'][0]['lat']
                climate_json['lon'] = location['coordinates'][0]['lon']

        # check if the coordinates of this location are in the weather coordinates
        # based on the title of the page
            # if so, replace the current latitude and latitude with the coordinates
            # in weather_coordinates

        if not hasAllMonths(climate_json['climate']):
            continue


        climate_json['climate'] = addRainToPrecipitation(climate_json['climate'])

        if not hasAllProperty(climate_json['climate'], 'sun'):
            continue
        if not hasAllProperty(climate_json['climate'], 'precipitation mm'):
            continue
        if not hasAllProperty(climate_json['climate'], 'high C'):
            continue
        if not hasAllProperty(climate_json['climate'], 'low C'):
            continue

        #print >>sys.stderr, "climate_json", climate_json["climate"]
        lat_lon = "{:.2f}, {:.2f}".format(climate_json['lat'], climate_json['lon'] )
        if lat_lon in lat_lons_set:
            print >>sys.stderr, "already there:", lat_lon
        else:
            lines += [json.dumps(condense_place_climate_json(climate_json))]

        lat_lons_set.add(lat_lon)

    to_output += ",\n".join([line.strip() for line in lines])

    to_output += ']'
    print to_output

if __name__ == '__main__':
    main()

