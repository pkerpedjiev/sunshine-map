import sys
import wikipedia_parse as wp

def test_wikipedia_to_single_line_pages():
    lines = ["sdfds <page>line</page>"]

    pages = list(wp.wikipedia_to_single_line_pages(lines))

    assert pages == ["<page>line</page>"]

    lines = ["sdfds <page>line</page> dsfd <page>line2</page>"]

    pages = list(wp.wikipedia_to_single_line_pages(lines))
    print >>sys.stderr, "pages:", pages
    assert pages == ["<page>line</page>", "<page>line2</page>"]

    lines = """sdfds <page>line
            </page> dsfd <page>line2</page>""".split('\n')
    pages = list(wp.wikipedia_to_single_line_pages(lines))
    print >>sys.stderr, "lines:", lines
    print >>sys.stderr, "pages:", pages
    assert pages == ["<page>line</page>", "<page>line2</page>"]

    lines = ["xsdfs <page>line", "line2</page><page>hi</page><page>", "there</page>"]
    pages = list(wp.wikipedia_to_single_line_pages(lines))
    print >>sys.stderr, "lines:", lines
    print >>sys.stderr, "pages:", pages
    assert pages == ["<page>lineline2</page>", "<page>hi</page>", "<page>there</page>"]

def test_find_property():
    wikipedia_exerpt = """
| country leader name               = 
| population       = 31,572
| population as of = Jan 1, 2009
"""
    text = "".join(wikipedia_exerpt.split('\n'))
    print >>sys.stderr, "text:", text
    
    population = wp.find_property(text, 'population')
    print >>sys.stderr, "population:", population
