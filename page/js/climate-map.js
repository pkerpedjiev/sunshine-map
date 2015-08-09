function drawMonthSelector(selection) {

    var innerWidth = 20;
    var outerWidth = 35;

  piebrush = d3.svg.circularbrush();
  /*
  var months = [[1,'Jan'],[2,'Feb'],[3,'Mar'],[4,'Apr'],[5,'May'],[6,'Jun'],
                [7, 'Jul'],[8,'Aug'],[9,'Sep'],[10,'Oct'],[11,'Nov'],[12,'Dec']];
                */
  var months = [[1,'J'],[2,'F'],[3,'M'],[4,'A'],[5,'M'],[6,'J'],
                [7, 'J'],[8,'A'],[9,'S'],[10,'O'],[11,'N'],[12,'D']];
  piebrush
  .range([0, months.length])
  .innerRadius(innerWidth)
  .outerRadius(outerWidth)
  .on("brushstart", pieBrushStart)
  .on("brushend", pieBrushEnd)
  .on("brush", pieBrush)
  .extent([0.3,0.22]);

  var startBrushData = [{class: "extent",
      endAngle: 6.3538161040516234,
      startAngle: 0.132537999873459,},
      {
        class: "resize e",
      endAngle: 0.132537999873459,
      startAngle: -0.06746200012654102
      },
      {
      class: "resize w",
      endAngle: 6.553816104051624,
      startAngle: 6.3538161040516234,
      }];



  var pie = d3.layout.pie().value(function(d) {return 1}).sort(function(a,b) { return a[0] - b[0]; });

  var pieArc = d3.svg.arc().innerRadius(innerWidth).outerRadius(outerWidth);
  
  var gCircularSelector = selection.append("g")
  .attr("class", "piebrush")

  gCircularSelector.selectAll("path")
  .data(pie(months))
  .enter()
  .append("path")
  .attr("class", "piemonths")
  .classed('selected', true)
  .attr("d", pieArc)
  .attr('id', function(d) { return 'arc' + d.data; })
  .on("click", function(d) {console.log(d)})

  gCircularSelector.selectAll('text')
  .data(months)
  .enter()
  .append('text')
  .attr('x', 4)
  .attr('dy', 12)
  .append("textPath")
  .attr('xlink:href', function(d) { return '#arc' + d; })
  .text(function(d) { return d[1]; })
  .classed('month-label', true);

  selection
  .append("g")
  .call(piebrush);

  gCircularSelector.selectAll('path.circularbrush')
  .each(function(d) { console.log('x', d); })
  .data(startBrushData);

  function pieBrush() {
      d3.event.stopPropagation();

    d3.selectAll("path.piemonths")
    //.style("fill", piebrushIntersect);
    .classed('selected', piebrushIntersect)

    var _m = d3.mouse(d3.select("g.piebrush").node());

    console.log(_m);

    d3.selectAll(".brushhandle")
    .attr("cx", _m[0])
    .attr("cy", _m[1])
    .attr("x2", _m[0])
    .attr("y2", _m[1]);

  }

  function piebrushIntersect(d,i) {
    var _e = piebrush.extent();

    if (_e[0] < _e[1]) {
      var intersect = (d.data[0] >= _e[0] && d.data[0] <= _e[1]);
    }
    else {
      var intersect = (d.data[0] >= _e[0]) || (d.data[0] <= _e[1]);      
    }

    console.log('_e:', _e);
    return intersect; // ? "rgb(241,90,64)" : "rgb(231,231,231)";
  }


  function pieBrushStart() {
      d3.event.stopPropagation();

    d3.select("g.piebrush")
    .append("line")
    .attr("class", "brushhandle")
    .style("stroke", "brown")
    .style("stroke-width", "2px");

    d3.select("g.piebrush").append("circle")
    .attr("class", "brushhandle")
    .style("fill", "brown")
    .attr("r", 5);

  }

  function pieBrushEnd() {

    d3.selectAll(".brushhandle").remove();
  }


}
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
    var topLayerLines = new L.StamenTileLayer('toner-lines', {'opacity': 0.8});

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
    var gMain = svg.append("g").attr("class", "leaflet-zoom-hide").attr('opacity', 0.8);

    var otherSvg = d3.select("#" + divName).append('svg').attr('width', width).attr('height', height).style('position', 'relative').style('z-index', 7);

    otherSvg.append('g')
    .attr('transform', 'translate(500,320)')
    .call(drawMonthSelector);

    var g = gMain.append('g');

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

        climate.forEach(function(d) {
            var latlng = new L.LatLng(d.lat, d.lon);
            var point = map.latLngToLayerPoint(new L.LatLng(+d.lat, +d.lon));
           
            d.x = point.x;
            d.y = point.y;
        });


        g.selectAll(".voronoi-border")
        .data(climate)
        .enter().append("path")
        .attr("class", "voronoi-border");

        g.selectAll('.city-point')
        .data(climate)
        .enter().append('circle')
        .classed('city-point', true);

        g.selectAll('.voronoi-border')
        .attr("d", buildPathFromPoint);

        var buildPathFromPoint = function(point) {
            if (typeof(point.cell) != 'undefined')
                return "M" + point.cell.join("L") + "Z";
            else
                return "";
        };

        sunColorScale = d3.scale.linear()
        .domain([0,400])
        .range(['#252525', '#FFFF42'])

        var cellPathFill = function(point) {
            return sunColorScale(point.climate.Jan.sun);
        };

        function resetView() {
            climate.forEach(function(d) {
                var latlng = new L.LatLng(d.lat, d.lon);
                var point = map.latLngToLayerPoint(new L.LatLng(+d.lat, +d.lon));

                d.x = point.x;
                d.y = point.y;
            });

            var counter = 0;
            voronoi(climate).forEach(function(d) {  
                d.point.cell = d; 
                counter += 1;
            });

            g.selectAll('.voronoi-border')
            .attr("d", buildPathFromPoint)
            .attr('fill',  cellPathFill)

            g.selectAll('.city-point')
            .attr('cx', function(d) { return d.x; })
            .attr('cy', function(d) { return d.y; })
            .attr('r', 5);
        }

        map.on("viewreset", resetView);
        resetView();
    }
}
