#!/usr/bin/python

import collections as col
import itertools as it
import json
import re
import sys
from optparse import OptionParser

def find_property(page, property_name):
    '''
    Find the value of some property in a wikipedia page
    where the property is listed like so
    | property=xcxc |
    
    @param page: The text of the wikipedia page.
    @param property_name: The name of the property (i.e. latd for latitude degrees)
    @return: The value of the property ('xcxc' in this example)
    '''
    # latitude degrees
    match_lat = re.search(r'\|[ \t]*{}[\t ]*=(.*?)[\|\{{\(&]'.format(property_name), page)
    if match_lat is None:
        return None
    lat_deg_str = match_lat.groups(1)[0].strip()

    return lat_deg_str

def extract_numeric(property_value):
    '''
    Extract a number from a property.

    So we extract 10 from something like '10sdfsd'

    @param property_value: The value to extract the number from.
    @return: The number in property_value. Return None if there's no
    number present.
    '''
    match = re.search(r'([0-9]*)', property_value)
    number = None
    if match is not None:
        number = float(match.groups(1)[0].strip())

    return number

def parse_longitude_latitude(page):
    '''
    Get latitude and longitude values from the text of a page.

    @param page: A string containing the text of page
    @return: (lon, lat) as a tuple. None if they're not found
    '''
    if page.find('latd') >= 0:
        pass

    # latitude degrees
    try:
        latd = float(find_property(page, 'latd'))
        longd = float(find_property(page, 'longd'))
    except (ValueError,TypeError) as ex:
        return (None, None)

    # try for minutes
    try:
        latm = float(find_property(page, 'latm'))
        longm = float(find_property(page, 'longm'))
    except (ValueError, TypeError) as e:
        latm = 0
        longm = 0
        #return (None, None)

    try:
        lats = float(find_property(page, 'lats'))
        longs = float(find_property(page, 'longs'))
    except (ValueError, TypeError) as e:
        lats = 0
        longs = 0

    try:
        latns = find_property(page, 'latNS')
        lonew = find_property(page, 'longEW')
    except:
        return (None, None)

    latd += latm / 60. + lats / 360.
    longd += longm / 60. + longs / 360.

    if latns == 'S':
        latd = -latd
    if lonew == 'W':
        longd = -longd

    print >>sys.stderr, "lat, lon", latd, longd

    '''
    print "latd", latd, 'latm', latm, 'lats', lats
    print "longd", longd, 'longm', longm, 'longs', longs

    print "lat_deg", latd, "longd", longd
    print "---------------------------------"
    '''

    #lat = match_lat.groups(1).strip()
    #print "lat:", lat
    return (longd, latd)

def parse_weather_box(page):
    '''
    Extract the text of a weather box from the page.

    @param page: The page in question.
    @return: A string containing the text of the weather box.
    '''
    match = re.search('(\{\{Weather box.*?\}\})', page)
    if match is None:
        return None

    return match.groups(1)[0].strip()

def parse_weather_stats(weather_box_str):
    '''
    Parse all of the weather stats from the
    weather box.

    @param weather_box_str: The text of the weather box
    @return: A dictionary containing all of the statistics
             in the weather box.
    '''
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    stat_types = ['high C', 'mean C', 'low C', 'rain mm', 'precipitation mm', 
             'snow cm', 'sun']

    stats = col.defaultdict(dict)
    for month, stat_type in it.product(months, stat_types):
        found_stat = find_property(weather_box_str, 
                                   month + " " + stat_type)

        if found_stat is not None:
            #replace weird long dash with a regular one
            found_stat = found_stat.replace('\xe2\x88\x92', '-') 
            try:
                stats[month][stat_type] = float(found_stat)
            except ValueError as ve:
                print >> sys.stderr, "Faulty stat:", found_stat

    return stats

def parse_title(page_text):
    '''
    Get the title of this page.

    @param page_text: The text of this web page.
    @return: The title of the page as enclosed in the <title></title> tags
    '''
    match = re.search('<title>(.*?)</title>', page_text)
    
    if match is None:
        return None

    return match.groups(1)[0].strip()

def wikipedia_to_single_line_pages(f):
    '''
    Parse a wikipedia dump and output pages on single lines.

    We're presuming that the wikipedia page is well formed.

    @param f: An input stream supplying lines of data.
    @return: A generator yielding single line pages.
    '''
    current_text = ""
    search_term = re.compile('(<page>.*?</page>)')

    for line in f:
        current_text += line.strip()

        matches = search_term.finditer(current_text)
        #print >>sys.stderr, "current_text:", current_text, "line:", line
        last_index = 0
        #print >>sys.stderr, "matches:", matches
        for match in matches:
            for i, group in enumerate(match.groups()):
                #print >>sys.stderr, "group:", group
                yield group
                last_index = match.end(i)

        current_text = current_text[last_index:]

def main():
    usage = """
    python wikipedia_to_single_line_pages.py wikipedia_dump.xml

    Parse wikipedia dumps and output each page on a single line.
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    for page in wikipedia_to_single_line_pages(f):
        lon, lat = parse_longitude_latitude(page)
        population = find_property(page, 'population_total')

        if lon is not None and lat is not None:
            weatherbox = parse_weather_box(page)
            if weatherbox is not None:
                name = parse_title(page)
                climate_stats = parse_weather_stats(weatherbox)

                place_weather = {'name': name,
                                 'lon': lon,
                                 'lat': lat,
                                 'climate': climate_stats }

                if population is not None:
                    try:
                        place_weather['population'] = int(extract_numeric(population.replace(',', '').replace(' ', '')))
                    except ValueError as ve:
                        print >>sys.stderr, "faulty population:", population

                print json.dumps(place_weather)
                

    f.close()

if __name__ == '__main__':
    main()

