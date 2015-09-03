### Get weatherbox coordinates

bzcat wikipedia_dumps/*.bz2 | python scripts/query_coordinates.py - -w | tee jsons/location_coordinates_weather.json

### Parse Weather Box Templates

bzcat wikipedia_dumps/*.bz2 | python scripts/parse_weatherbox_templates.py  - > jsons/weatherbox_templates.json

### Get location using the API

https://en.wikipedia.org/w/api.php?action=query&titles=Alice%20Springs&prop=coordinates&format=json

### Parse Climate Boxes

bzcat wikipedia_dumps/*.bz2 | python scripts/wikipedia_parse.py -w jsons/weatherbox_templates.json - > jsons/climate.json

### Consolidate into one

python scripts/consolidate_climates.py -w jsons/weather_location_coordinates.json jsons/climate.json > jsons/climate_consolidated.json

### Tests

cd scripts
nosetest test

Missing Cities:

Seattle
Pittsburgh
