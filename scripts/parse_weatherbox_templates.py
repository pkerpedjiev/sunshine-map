#!/usr/bin/python

import json
import re
import sys
import wikipedia_parse as wp
from optparse import OptionParser

def main():
    usage = """
    python parse_weathrebox_templates wikipedia_dump.xml

    Create and output a table of weatherbox templates
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

    weatherbox_re = re.compile('Template:(.*[wW]eatherbox.*)')
    boxes = {}
    counter = 0
    wb_counter = 0

    for page in wp.wikipedia_to_single_line_pages(f):
        counter += 1
        title = wp.parse_title(page)

        match = weatherbox_re.match(title) 
        if match is not None:
            wb_counter += 1
            template_title = match.groups(1)[0]

            weather_box = wp.parse_weather_box(page)

            if weather_box is not None:
                boxes[template_title] = weather_box

            print >>sys.stderr, "Weatherbox counter:", counter, wb_counter, title

    print json.dumps(boxes, indent=2)

if __name__ == '__main__':
    main()

