import json
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

def population_check(filename):
    with open(filename, 'r') as f:
        for page in wp.wikipedia_to_single_line_pages(f):
            population = wp.find_property(page, 'population_total')
            population = int(wp.extract_numeric(population.replace(',', '').replace(' ','')))
            print >>sys.stderr, "population:",  population

def test_find_population():
    population_check('test/data/guatemala.wiki')
    population_check('test/data/gdansk.wiki')
    population_check('test/data/ithaca.wiki')
    population_check('test/data/jerusalem.wiki')
    population_check('test/data/lleida.wiki')
    population_check('test/data/moncton.wiki')

def test_latitude_longidue():
    with open('test/data/ithaca.wiki', 'r') as f:
        for page in wp.wikipedia_to_single_line_pages(f):
            lat, lon = wp.parse_longitude_latitude(page)

            print >>sys.stderr, "lat:", lat, "lon:", lon

def test_astoria():

    with open('test/data/astoria.wiki', 'r') as f:
        for page in wp.wikipedia_to_single_line_pages(f):
            weather_box = wp.parse_weather_for_page(page)
            print >>sys.stderr, json.dumps(weather_box)

def test_parse_weather_box():
    with open('test/data/denver_weatherbox.wiki', 'r') as f:
        for page in wp.wikipedia_to_single_line_pages(f):
            weather_box = wp.parse_weather_box(page)
            print >>sys.stderr, json.dumps(weather_box)

