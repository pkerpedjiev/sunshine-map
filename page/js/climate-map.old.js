function drawClimateMap(divName) {
    //var map = L.map('isochroneMap').setView([48.2858, 6.7868], 4);
    var initialLat = 39.74;
    var initialLon = -104.99;

    var map = new L.Map(divName, {
        center: new L.LatLng(initialLat, initialLon),
        zoom: 5
    });

    //var layer = new L.StamenTileLayer("toner");
    //map.addLayer(layer);
    cartoDbBaseLayer = L.tileLayer('http://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png',{
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
    }).addTo(map);

    var topPane = map._createPane('leaflet-top-pane', map.getPanes().mapPane);
    var topLayerLines = new L.StamenTileLayer('toner-lines', {'opacity': 0.6});

    map.addLayer(topLayerLines);
    topPane.appendChild(topLayerLines.getContainer());
    topLayerLines.setZIndex(7);

    var topLayerLabels = new L.tileLayer('http://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}.png', {
        maxZoom: 17
    }).addTo(map);
    topPane.appendChild(topLayerLabels.getContainer());
    topLayerLabels.setZIndex(7);

    var width=550, height=400;
    //var defaultContourColor = 'transparent';
    var defaultContourColor = 'black';
    var defaultContourWidth = 1;

    // Initialize the SVG layer
    map._initPathRoot();

    // We pick up the SVG from the map object
    var svg = d3.select("#" + divName).select("svg");
    var g = svg.append("g").attr("class", "leaflet-zoom-hide").attr('opacity', 0.8);

    queue()
    .defer(d3.json, "/data/us-10m.json")
    .defer(d3.csv, "/data/us-state-capitals.csv")
    .defer(d3.json, "/data/climate_consolidated.json")
    .await(ready);

    var fill = d3.scale.category10();

    var voronoi = d3.geom.voronoi()
    .x(function(d) { return d.x; })
    .y(function(d) { return d.y; });
    //.clipExtent([[0, 0], [width, height]]);

    function ready(error, us, capitals, climate) {
        console.log('error:', error)
        console.log(us, capitals, climate);
        capitals.forEach(function(d) {
            var latlng = new L.LatLng(d.latitude, d.longitude);
            var point = map.latLngToLayerPoint(new L.LatLng(+d.latitude, +d.longitude));
           
            d.x = point.x;
            d.y = point.y;
        });


        g.selectAll(".voronoi-border")
        .data(capitals)
        .enter().append("path")
        .attr("class", "voronoi-border");

        g.selectAll('.voronoi-border')
        .attr("d", buildPathFromPoint);

        var buildPathFromPoint = function(point) {
          return "M" + point.cell.join("L") + "Z";
        };

        function resetView() {
            capitals.forEach(function(d) {
                var latlng = new L.LatLng(d.latitude, d.longitude);
                var point = map.latLngToLayerPoint(new L.LatLng(+d.latitude, +d.longitude));

                d.x = point.x;
                d.y = point.y;
            });

            voronoi(capitals).forEach(function(d) { d.point.cell = d; });

            g.selectAll('.voronoi-border')
            .attr("d", buildPathFromPoint);
        }

        map.on("viewreset", resetView);
        resetView();
    }
}
