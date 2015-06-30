#!/usr/bin/python

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
    match_lat = re.search('\|[ ]*{}[ ]*=(.*?)\|'.format(property_name), page)
    if match_lat is None:
        return (None, None)
    lat_deg_str = match_lat.groups(1)[0].strip()

    return lat_deg_str

def parse_longitude_latitude(page):
    '''
    Get latitude and longitude values from the text of a page.

    @param page: A string containing the text of page
    @return: (lon, lat) as a tuple. None if they're not found
    '''
    if page.find('latd') >= 0:
        #print page
        pass

    # latitude degrees
    try:
        latd = float(find_property(page, 'latd'))
        longd = float(find_property(page, 'longd'))
    except ValueError:
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

    latd += latm / 60. + lats / 360.
    longd += longm / 60. + longs / 360.

    print "latd", latd, 'latm', latm, 'lats', lats
    print "longd", longd, 'longm', longm, 'longs', longs

    print "lat_deg", latd, "longd", longd
    print "---------------------------------"

    #lat = match_lat.groups(1).strip()
    #print "lat:", lat
    return (None, None)

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

    f.close()

if __name__ == '__main__':
    main()

