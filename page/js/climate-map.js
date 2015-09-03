var colorScales =  {
sun: d3.scale.linear()
.domain([0,400])
.range(['#252525', '#FFFF42']),

'rain mm':  d3.scale.linear()
.domain([0,149, 242, 330])
.range(['#FFFFFF', '#18FF18', '#008800', '#006600']),

'precipitation mm':  d3.scale.linear()
.domain([0,149, 242, 330])
.range(['#FFFFFF', '#18FF18', '#008800', '#006600']),

'mean C':  d3.scale.linear()
.domain([-88.3, -42, 4.5, 48])
.range(['#000009', '#0202FF', '#FFFFFF', '#A50000']),

'low C':  d3.scale.linear()
.domain([-88.3, -42, 4.5, 48])
.range(['#000009', '#0202FF', '#FFFFFF', '#A50000']),

'high C':  d3.scale.linear()
.domain([-88.3, -42, 4.5, 48])
.range(['#000009', '#0202FF', '#FFFFFF', '#A50000']),

'snow cm':  d3.scale.linear()
.domain([0,17.8,86.4])
.range(['#FFFFFF', '#0000F4', '#000030'])
};


var currentColorScale = colorScales['sun'];
var currentWeatherType = 'sun';

var ClimateDataTypeModel = Backbone.Model.extend( {
    defaults: {
        "months": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                   // the months for which to display the weather data
                   // can be changed by the ciruclar brush
        "data": "sun",
                // The type of data to display (e.g. sun, precipitation, etc..)
                // can be changed using a series of selection boxes
        "compareTo": null
                // if we click on a city, we should be able to see how its
                // weather compares to that of every other city on the globe
    }
});

var WeatherMapTypeView = Backbone.View.extend( {
    el: ".weather-type",
    events: {
       'change input[type=radio]': 'changedRadio' 
    },

    changedRadio: function(d) {
        console.log('val:', $('input[type=radio]:checked').val());
        currentWeatherType = $('input[type=radio]:checked').val();
        currentColorScale = colorScales[currentWeatherType];
        updateMonthFilter(myMonthSelectorChart.monthFilterPrev());
    }
});


$(function() {
    var weatherMapTypeView = new WeatherMapTypeView();
});


var updateMonthFilter = function(monthFilter) {
    var monthFilteredFill = function(point) {
        var total = 0;

        for (var i = 0; i < monthFilter.length; i++) {
            total += point.climate[monthFilter[i]][currentWeatherType];
        }

        if (monthFilter.length === 0)
            return currentColorScale(0);
        else {
            return currentColorScale(total / monthFilter.length);
        }
    };

    d3.selectAll('.voronoi-border')
    .attr('fill',  monthFilteredFill);
};

function monthSelectorChart(selection) {
    var innerWidth = 20;
    var outerWidth = 35;
    var monthFilterPrev = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var monthFilterChanged = updateMonthFilter;

    function render(selection) {
        piebrush = d3.svg.circularbrush();
        var months = [[1,'J', 'Jan'],[2,'F', 'Feb'],[3,'M', 'Mar'],[4,'A','Apr'],
            [5,'M','Mar'],[6,'J', 'Jun'], [7,'J', 'Jul'],[8,'A', 'Aug'],
            [9,'S','Sep'], [10,'O','Oct'],[11,'N','Nov'],[12,'D','Dec']];
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
                    .classed('selected', piebrushIntersect);

                    var _m = d3.mouse(d3.select("g.piebrush").node());

                    d3.selectAll(".brushhandle")
                    .attr("cx", _m[0])
                    .attr("cy", _m[1])
                    .attr("x2", _m[0])
                    .attr("y2", _m[1]);

                    var monthFilter = d3.selectAll("path.piemonths.selected")
                    .data()
                    .map(function(d) { return d.data[2]; });

                    monthFilterChanged(monthFilter);

                    monthFilter.sort()
                    if (monthFilter.length != monthFilterPrev.length) {
                        monthFilterChanged(monthFilter);
                        monthFilterPrev = monthFilter;
                    } else {
                        for (var i = 0; i < monthFilter.length; i++) {
                            if (monthFilter[i] != monthFilterPrev[i]) {
                                monthFilterChanged(monthFilter);
                                monthFilterPrev = monthFilter;
                            }
                        }
                    }

                }

                function piebrushIntersect(d,i) {
                    var _e = piebrush.extent();

                    if (_e[0] < _e[1]) {
                        var intersect = (d.data[0] >= _e[0] && d.data[0] <= _e[1]);
                    }
                    else {
                        var intersect = (d.data[0] >= _e[0]) || (d.data[0] <= _e[1]);      
                    }

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

    render.innerWidth = function(_) {
        if (!arguments.length) return innerWidth;
        innerWidth = _;
        return chart;
    };

    render.outerWidth = function(_) {
        if (!arguments.length) return outerWidth;
        outerWidth = _;
        return chart;
    };

    render.monthFilterChanged = function(_) {
        if (!arguments.length) return monthFilterChanged;
        monthFilterChanged = _;
        return chart;
    };

    render.monthFilterPrev = function(_) {
        if (!arguments.length) return monthFilterPrev;
        monthFilterPrev = _;
        return chart;
    };

    return render;
}

var weatherTypeControl = L.control({
    position: 'topright',
});

weatherTypeControl.onAdd = function( map ) {
    var div = L.DomUtil.create('div', 'weather-type');
    var form = L.DomUtil.create('form', 'form', div);
    var group = L.DomUtil.create('div', 'form-group', form);

    var weatherTypes = ['sun', 'precipitation mm', 'high C', 'mean C', 'low C', 'rain mm', 'snow cm'];
    radioHtml = '';
    for (var i = 0; i < weatherTypes.length; i++) {
	    radioHtml += '<label style="display: block;"><input type="radio" style="position: relative" name="weatherTypeRadio" value="' + weatherTypes[i] + '"><span>' + weatherTypes[i] + '</span></label>';
    }

    group.innerHTML += radioHtml;

    return div;
};

weatherTypeControl._initLayout = function() {
	var form = this._form = L.DomUtil.create('form', className + '-list');
};

var myMonthSelectorChart = monthSelectorChart();

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

    weatherTypeControl.addTo(map);
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

    var otherSvg = d3.select("#" + divName).append('svg').attr('width', width).attr('height', height).style('position', 'relative').style('z-index', 7).attr('pointer-events', 'none');


    otherSvg.append('g')
    .attr('transform', 'translate(500,320)')
    .attr('pointer-events', 'all')
    .call(myMonthSelectorChart);

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
        .attr("d", buildPathFromPoint)
        .on('click', function(d) { console.log('d', d); }); 

        var buildPathFromPoint = function(point) {
            if (typeof(point.cell) != 'undefined')
                return "M" + point.cell.join("L") + "Z";
            else
                return "";
        };


        var cellPathFill = function(point) {
            return currentColorScale(point.climate.Jan.sun);
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
            .attr("d", buildPathFromPoint);
            //.attr('fill',  cellPathFill)
            //
            updateMonthFilter(myMonthSelectorChart.monthFilterPrev());

            g.selectAll('.city-point')
            .attr('cx', function(d) { return d.x; })
            .attr('cy', function(d) { return d.y; })
            .attr('r', 5);
        }

        map.on("viewreset", resetView);
        resetView();
    }
}
