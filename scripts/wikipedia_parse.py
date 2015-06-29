#!/usr/bin/python

import re
import sys
from optparse import OptionParser

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
        print >>sys.stderr, "current_text:", current_text, "line:", line
        last_index = 0
        print >>sys.stderr, "matches:", matches
        for match in matches:
            for i, group in enumerate(match.groups()):
                print >>sys.stderr, "group:", group
                yield group
                last_index = match.end(i)

        current_text = current_text[last_index:]

def main():
    usage = """
    python wikipedia_to_single_line_pages.py wikipedia_dump.xml

    Parse wikipedia dumps and output each page on a single line.
    """
    num_args= 0
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

    f.close()

if __name__ == '__main__':
    main()

