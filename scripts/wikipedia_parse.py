#!/usr/bin/python

import collections as col
import itertools as it
import json
import os.path as op
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
    newpage = page.replace('&amp;minus;', '-')
    # latitude degrees
    match_lat = re.search(r'\|[ \t]*{}[\t ]*=(.*?)[\|\{{\(&]'.format(property_name), newpage)
    if match_lat is None:
        return None
    lat_deg_str = match_lat.groups(1)[0].strip()

    return lat_deg_str

def parse_infobox(page):
    """
    Extract the infobox if a page has one.

    """
    pos = page.find('{{Infobox')

    if pos < 0:
        return None

    return extract_double_brackets(page, pos)


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

def parse_coords(coord_string):
    '''
    Parse a coordinate string such as:

        Coord|57|18|22|N|4|27|32|W|display=title

        or

        Coord|44.112|N|87.913|W|display=title

    @param coord_string: The string containing the coordinates
    @return: A (lon, lat) tuple
    '''

    parts = coord_string.split('|')
    denominator = 1
    lat = None
    lon = None

    these_parts = []
    for i in range(0, len(parts)):
        if len(parts[i]) == 0:
            continue

        parts[i] = parts[i].strip()
        try:
            num = float(parts[i])
            these_parts += [num]
            continue
        except ValueError:
            pass

        if parts[i] == 'N' or parts[i] == 'S':
            denominator = 1
            lat = 0
            for j in range(len(these_parts)):
                lat += these_parts[j] / float(denominator)
                denominator *= 60
            if parts[i] == 'S':
                lat = -lat
        elif parts[i] == 'E' or parts[i] == 'W':
            denominator = 1
            lon = 0
            for j in range(len(these_parts)):
                lon += these_parts[j] / float(denominator)
                denominator *= 60
            if parts[i] == 'W':
                lon = -lon 
            return (lon, lat)
        elif lat is None and lon is None:
            if len(these_parts) > 1:
                lat = these_parts[0]
                lon = these_parts[1]

                #print >>sys.stderr, "coord_string:", coord_string, lat, lon
                return (lon, lat)
            else:
                #print >>sys.stderr, "Weird coord string:", coord_string
                pass

            lat,lon = None,None
        else:
            #print >>sys.stderr, "Weird coord string:", coord_string
            pass

        these_parts = []

    return (lon, lat)

def parse_longitude_latitude(page, latd='latd', lond='longd',
                            latm='latm', lonm='longm',
                            lats='lats', lons='longs',
                            latNS='latNS', lonEW='longEW'):
    '''
    Get latitude and longitude values from the text of a page.

    @param page: A string containing the text of page
    @return: (lon, lat) as a tuple. None if they're not found
    '''
    match = re.search('\{\{[C|c]oord\|([^\}]*)\}\}', page)
    lat,lon = None, None
    if match is not None:
        (lon, lat) = parse_coords(match.groups(1)[0])

    if lat is not None and lon is not None:
        return (lon,lat)

    # latitude degrees
    try:
        latd = float(find_property(page, latd))
        longd = float(find_property(page, lond))
    except (ValueError,TypeError) as ex:
        return (None, None)

    # try for minutes
    try:
        latm = float(find_property(page, latm))
        longm = float(find_property(page, lonm))
    except (ValueError, TypeError) as e:
        latm = 0
        longm = 0
        #return (None, None)

    try:
        lats = float(find_property(page, lats))
        longs = float(find_property(page, lons))
    except (ValueError, TypeError) as e:
        lats = 0
        longs = 0

    try:
        latns = find_property(page, latNS)
        lonew = find_property(page, lonEW)
    except:
        return (None, None)

    latd += latm / 60. + lats / 360.
    longd += longm / 60. + longs / 360.

    if latns == 'S':
        latd = -latd
    if lonew == 'W':
        longd = -longd

    #print >>sys.stderr, "lat, lon", latd, longd

    '''
    print "latd", latd, 'latm', latm, 'lats', lats
    print "longd", longd, 'longm', longm, 'longs', longs

    print "lat_deg", latd, "longd", longd
    print "---------------------------------"
    '''

    #lat = match_lat.groups(1).strip()
    #print "lat:", lat
    return (longd, latd)

def parse_longitude_latitude_deg(page):
    '''
    Get latitude and longitude values from the text of a page.

    Where they are encoded as 

    lat_deg, lat_men, lat_sec, lat_hem
    lon_deg, lon_men, lon_sec, lon_hem


    @param page: A string containing the text of page
    @return: (lon, lat) as a tuple. None if they're not found
    '''
    match = re.search('\{\{[Cc]oord\|([^\}]*)\}\}', page)
    lat,lon = None, None
    if match is not None:
        (lon, lat) = parse_coords(match.groups(1)[0])

    if lat is not None and lon is not None:
        return (lon,lat)

    # latitude degrees
    try:
        latd = float(find_property(page, 'lat_deg'))
        longd = float(find_property(page, 'lon_deg'))
    except (ValueError,TypeError) as ex:
        return (None, None)

    # try for minutes
    try:
        latm = float(find_property(page, 'lat_min'))
        longm = float(find_property(page, 'lon_min'))
    except (ValueError, TypeError) as e:
        latm = 0
        longm = 0
        #return (None, None)

    try:
        lats = float(find_property(page, 'lat_sec'))
        longs = float(find_property(page, 'lon_sec'))
    except (ValueError, TypeError) as e:
        lats = 0
        longs = 0

    try:
        latns = find_property(page, 'lat_hem')
        lonew = find_property(page, 'lon_hem')
    except:
        return (None, None)

    latd += latm / 60. + lats / 360.
    longd += longm / 60. + longs / 360.

    if latns == 'S':
        latd = -latd
    if lonew == 'W':
        longd = -longd

    #print >>sys.stderr, "lat, lon", latd, longd

    '''
    print "latd", latd, 'latm', latm, 'lats', lats
    print "longd", longd, 'longm', longm, 'longs', longs

    print "lat_deg", latd, "longd", longd
    print "---------------------------------"
    '''

    #lat = match_lat.groups(1).strip()
    #print "lat:", lat
    return (longd, latd)

def parse_longitude_latitude_d(page):
    '''
    Get latitude and longitude values from the text of a page.

    Where they are encoded as 

    lat_deg, lat_men, lat_sec, lat_hem
    lon_deg, lon_men, lon_sec, lon_hem


    @param page: A string containing the text of page
    @return: (lon, lat) as a tuple. None if they're not found
    '''
    match = re.search('\{\{Coord\|([^\}]*)\}\}', page)
    lat,lon = None, None
    if match is not None:
        (lon, lat) = parse_coords(match.groups(1)[0])

    if lat is not None and lon is not None:
        return (lon,lat)

    # latitude degrees
    try:
        latd = float(find_property(page, 'lat_d'))
        longd = float(find_property(page, 'lon_d'))
    except (ValueError,TypeError) as ex:
        return (None, None)

    # try for minutes
    try:
        latm = float(find_property(page, 'lat_m'))
        longm = float(find_property(page, 'lon_m'))
    except (ValueError, TypeError) as e:
        latm = 0
        longm = 0
        #return (None, None)

    try:
        lats = float(find_property(page, 'lat_s'))
        longs = float(find_property(page, 'lon_s'))
    except (ValueError, TypeError) as e:
        lats = 0
        longs = 0

    try:
        latns = find_property(page, 'lat_h')
        lonew = find_property(page, 'lon_h')
    except:
        return (None, None)

    latd += latm / 60. + lats / 360.
    longd += longm / 60. + longs / 360.

    if latns == 'S':
        latd = -latd
    if lonew == 'W':
        longd = -longd

    #print >>sys.stderr, "lat, lon", latd, longd

    '''
    print "latd", latd, 'latm', latm, 'lats', lats
    print "longd", longd, 'longm', longm, 'longs', longs

    print "lat_deg", latd, "longd", longd
    print "---------------------------------"
    '''

    #lat = match_lat.groups(1).strip()
    #print "lat:", lat
    return (longd, latd)

def extract_double_brackets(page, pos):
    '''
    Extract a section enclosed in double brackets starting
    at position pos

    @param page: The page to extract them from
    @param pos: The starting position of the double brackets
    '''
    start = pos

    count = 0
    for pos in range(pos, len(page) - 1):
        if page[pos:pos+2] == '{{':
            count += 1
        elif page[pos:pos+2] == '}}':
            count -= 1

        if count == 0:
            return page[start:pos+2]

    return None

def parse_weather_box(page):
    '''
    Extract the text of a weather box from the page.

    @param page: The page in question.
    @return: A string containing the text of the weather box.
    '''
    pos = page.find('{{Weather box')

    if pos < 0:
        return None

    return extract_double_brackets(page, pos)

def parse_weather_stats(weather_box_str, page_name=None):
    '''
    Parse all of the weather stats from the
    weather box.

    @param weather_box_str: The text of the weather box
    @param page_name: The page name for debugging purposes
    @return: A dictionary containing all of the statistics
             in the weather box.
    '''
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    stat_types = ['high C', 'mean C', 'low C', 'rain mm', 'precipitation mm', 
             'snow cm', 'high F', 'mean F', 'low F', 'precipitation inch', 'snow inch',  'sun']

    stats = col.defaultdict(dict)
    for month, stat_type in it.product(months, stat_types):
        found_stat = find_property(weather_box_str, 
                                   month + " " + stat_type)

        if found_stat is not None:
            #replace weird long dash with a regular one
            found_stat = found_stat.replace('\xe2\x88\x92', '-') 
            found_stat = found_stat.replace('&amp;&minus;', '-') 
            try:
                stats[month][stat_type] = float(found_stat)
            except ValueError as ve:
                if stat_type == 'snow inch' and found_stat == 'trace':
                    stats[month][stat_type] = 0.01
                else:
                    #print >> sys.stderr, "Faulty stat:", found_stat, " page name: ", page_name
                    continue


            if stat_type == 'high F':
                stats[month]['high C'] = int(10 * (stats[month]['high F'] - 32) * 5 / 9.) / 10.
            if stat_type == 'low F':
                stats[month]['low C'] = int(10 * (stats[month]['low F'] - 32) * 5 / 9.) / 10.
            if stat_type == 'mean F':
                stats[month]['mean C'] = int(10 * (stats[month]['mean F'] - 32) * 5 / 9.) / 10.
            if stat_type == 'precipitation inch':
                stats[month]['precipitation mm'] = int(10 * stats[month]['precipitation inch'] * 25.4) / 10.
            if stat_type == 'snow inch':
                stats[month]['snow cm'] = int(10 * stats[month]['snow inch'] * 2.54) / 10.

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
        if line.find('<page>') >= 0 or line.find('</page>') >= 0:
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

def parse_weather_for_page(page, dump_dir=None, weatherbox_templates = None):
    '''
    Extract the weather box information from a given page.

    @param page: The xml text of a wikipedia page.
    @return: A dictionary containing all of the weather information
    '''
    # try using the latd, latm... encoding for coordinages
    lon, lat = parse_longitude_latitude(page)

    # try using the lat_deg, lat_min... encoding for coordinages
    if lon is None and lat is None:
        lon, lat = parse_longitude_latitude(page, 'lat_deg', 'lon_deg',
                                           'lat_min', 'lon_min',
                                           'lat_sec', 'lon_sec',
                                           'lat_hem', 'lon_hem')

    if lon is None and lat is None:
        lon, lat = parse_longitude_latitude(page, 'lat_d', 'long_d',
                                           'lat_m', 'long_m',
                                           'lat_s', 'long_s',
                                           'lat_NS', 'long_EW')

    population = find_property(page, 'population_total')
        
    name = parse_title(page)

    if lon is not None and lat is not None:
        weatherbox = parse_weather_box(page)

        if weatherbox is None:
            # no explicit weatherbox, maybe we have a template
            if weatherbox_templates is not None:
                match = re.search('\{\{([^}]*?[Ww]eatherbox[^}]*?)\}\}', page)
                
                if match is not None:
                    weatherbox_name = match.groups(1)[0].decode('utf-8')
                    #print >>sys.stderr, "found weatherbox template:", weatherbox_name
                    try:
                        weatherbox = weatherbox_templates[weatherbox_name].encode('utf-8')
                    except KeyError as ke:
                        #print >>sys.stderr, "not found weatherbox:", weatherbox_name
                        pass

        if weatherbox is not None:
            name = parse_title(page)
            #print >>sys.stderr, "name:", name, len(page)
            climate_stats = parse_weather_stats(weatherbox, name)

            place_weather = {'name': name,
                             'lon': lon,
                             'lat': lat,
                             'climate': climate_stats }

            if population is not None:
                try:
                    place_weather['population'] = int(extract_numeric(population.replace(',', '').replace(' ', '')))
                except ValueError:
                    #print >>sys.stderr, "faulty population:", population, " page title: ", name
                    pass

            return place_weather
            
    return None

def main():
    usage = """
    python wikipedia_to_single_line_pages.py wikipedia_dump.xml

    Parse wikipedia dumps and output each page on a single line.
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')
    parser.add_option('-d', '--dump-dir', dest='dump_dir', default=None, help='Dump locations in their own files in this directory')
    parser.add_option('-w', '--weatherbox-templates', dest='weatherbox_templates', default=None, help='Use a set of weatherbox templates')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    weatherbox_templates = None
    if options.weatherbox_templates is not None:
        with open(options.weatherbox_templates, 'r') as f1:
            weatherbox_templates = json.load(f1)

    count = 0
    found = 0
    for page in wikipedia_to_single_line_pages(f):
        count += 1
        weather_box = parse_weather_for_page(page, dump_dir=options.dump_dir,
                                            weatherbox_templates=weatherbox_templates)
        
        if weather_box is not None:
            print json.dumps(weather_box)
            found += 1
            print >>sys.stderr, "found:", found, "count:", count

    f.close()

if __name__ == '__main__':
    main()

