#!/usr/bin/python

import sys
from optparse import OptionParser

def main():
    usage = """
    python extract_sunshine_hours.py wikipedia_dump.xml


    Iterate over a wikipedia dump and extract the climate data boxes.
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)



if __name__ == '__main__':
    main()

