#!/usr/bin/python

import json
import sys
import time
import urllib2
import wikipedia_parse as wp
from optparse import OptionParser

def main():
    usage = """
    python scripts/query_coordinates.py dump.wiki

    Iterate over all pages with an infobox and query the Wikipedia API
    for the coordinates of this page.
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')
    parser.add_option('-e', '--existing', dest='existing', default=None, help='Use an existing set of locations')
    parser.add_option('-w', '--weatherbox', dest='weatherbox', default=False, 
                      action='store_true', help='Use only entries with an weatherbox')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    existing = set()

    if options.existing is not None:
        with open(options.existing, 'r') as f:
            for line in f:
                print >>sys.stderr, "line:", line
                js = json.loads(line)
                existing.add(js.title)
                print line.strip()

    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    counter = 0
    visited = 0

    for page in wp.wikipedia_to_single_line_pages(f):
        title = wp.parse_title(page)
        counter += 1

        if page.find('{{coord') >= 0 or page.find('latd') >= 0 or page.find('lat_deg') >= 0 or page.find('lat_d') >= 0:
            if options.weatherbox:
                if page.find('weatherbox') < 0 and page.find("{{Weather") < 0:
                    continue

            visited += 1
            wait = 1
            found = False

            while not found:
                try:
                    url = "https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=coordinates&format=json".format(title.replace(' ', '%20'))
                    print >>sys.stderr, "pages:", (visited, counter), "url:", url
                    f = urllib2.urlopen(url)
                    found = True
                except urllib2.HTTPError as he:
                    print >>sys.stderr, "Waiting..."
                    time.sleep(wait)
                    wait *= 2

                    if wait > 16:
                        break

            if not found:
                continue

            if f is not None:
                text = f.read()
                result = json.loads(text)

                if 'query' in result:
                    if 'pages' in result['query']:
                        for key in result['query']['pages']:
                            if 'coordinates' in result['query']['pages'][key]:
                                result['query']['pages'][key]['length'] = len(page)
                                print json.dumps(result['query']['pages'][key])
            else:
                print >>sys.stderr, "Failed to open the url"



if __name__ == '__main__':
    main()

