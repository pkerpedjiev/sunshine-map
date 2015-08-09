// Copyright 2014 Jason Davies, http://www.jasondavies.com/
(function() {

var π = Math.PI,
    degrees = 180 / π,
    radians = π / 180,
    ε = 1e-15,
    circle = d3.geo.circle().angle(90);

d3.geo.voronoi = function(points, triangles) {
  if (arguments.length < 2) triangles = d3.geo.delaunay(points);
  if (!triangles) triangles = [];

  var n = points.length;

  var edgeByStart = [];
  triangles.forEach(function(t) {
    edgeByStart[t.a.p.i] = t.a;
    edgeByStart[t.b.p.i] = t.b;
  });

  return {
    type: "GeometryCollection",
    geometries: n === 1 ? [{type: "Sphere"}]
      : n === 2 ? hemispheres(points[0], points[1])
      : points.map(function(_, i) {
        var cell = [],
            neighbors = [],
            o = {type: "Polygon", coordinates: [cell], neighbors: neighbors},
            e00 = edgeByStart[i],
            e0 = e00,
            e = e0;
        if (!e) return null;
        var centre0 = e.triangle.centre;
        do {
          var centre = e.triangle.centre;
          if (dot(centre, centre0) < ε - 1) {
            var a = cartesian(points[e.neighbor.p.i]), b = cartesian(points[e.p.i]),
                c = normalise([a[0] + b[0], a[1] + b[1], a[2] + b[2]]);
            if (dot(centre, cross(a, b)) > 0) c[0] = -c[0], c[1] = -c[1], c[2] = -c[2];
            cell.push(spherical(c));
          }
          cell.push(spherical(centre));
          neighbors.push(e.neighbor.p.i);
          centre0 = centre;
          if (e === e00 && e0 !== e00) break;
          e = (e0 = e).next.next.neighbor;
        } while (1);
        return o;
      })
  };
};

d3.geo.voronoi.topology = function(points, triangles) {
  if (arguments.length < 2) triangles = d3.geo.delaunay(points);
  if (!triangles) triangles = [];

  var n = points.length,
      geometries = new Array(n),
      arcs = [],
      arcIndex = -1,
      arcIndexByEdge = {};

  var edgeByStart = [];
  triangles.forEach(function(t) {
    edgeByStart[t.a.p.i] = t.a;
    edgeByStart[t.b.p.i] = t.b;
  });

  // TODO n == 2 (hemispheres)
  points.forEach(function(_, index) {
    var arcIndexes = [],
        neighbors = [],
        e00 = edgeByStart[index],
        e0 = e00,
        e = e0;
    if (!e) return null;
    do {
      // TODO ~180° lines
      if (e !== e0) {
        var l = e0.triangle.index,
            r = e.triangle.index,
            k = l < r ? l + "," + r : r + "," + l,
            i = arcIndexByEdge[k];
        if (i == null) {
          if (l < r) arcs[i = arcIndexByEdge[k] = ++arcIndex] = [spherical(e0.triangle.centre), spherical(e.triangle.centre)];
          else arcs[i = arcIndexByEdge[k] = ++arcIndex] = [spherical(e.triangle.centre), spherical(e0.triangle.centre)];
        }
        arcIndexes.push(l < r ? i : ~i);
        neighbors.push(e.neighbor.p.i);
      }
      if (e === e00 && e0 !== e00) break;
      e = (e0 = e).neighbor.next;
    } while (1);
    geometries[index] = {
      type: "Polygon",
      neighbors: neighbors,
      arcs: [arcIndexes]
    };
  });
  return {
    objects: {
      voronoi: {
        type: "GeometryCollection",
        geometries: geometries
      }
    },
    arcs: arcs
  };
};

d3.geo.delaunay = function(points) {
  var p = points.map(cartesian),
      n = points.length,
      triangles = d3.convexhull3d(p);

  if (triangles.length) return triangles.forEach(function(t) {
    t.coordinates = [points[t.a.p.i], points[t.b.p.i], points[t.c.p.i]];
    t.centre = circumcentre(t);
  }), triangles;
};

function hemispheres(a, b) {
  var c = d3.geo.interpolate(a, b)(.5),
      n = cross(cross(cartesian(a), cartesian(b)), cartesian(c)),
      m = 1 / norm(n);
  n[0] *= m, n[1] *= m, n[2] *= m;
  var ring = circle.origin(spherical(n))().coordinates[0];
  return [
    {type: "Polygon", coordinates: [ring]},
    {type: "Polygon", coordinates: [ring.slice().reverse()]}
  ];
}

d3.convexhull3d = function(points) {
  var n = points.length;

  if (n < 4) return []; // coplanar points

  for (var i = 0; i < n; ++i) points[i].i = i;
  d3.shuffle(points);

  var a = points[0],
      b = points[1],
      c = points[2],
      t = new Triangle(a, b, c);

  // Find non-coplanar fourth point.
  for (var i = 3; i < n && coplanar(t, points[i]); ++i);

  if (i === n) return []; // coplanar points

  // Create a tetrahedron.
  var d = points[i];
  points[i] = points[3], points[3] = d;

  if (visible(t, d)) {
    var tmp = b; b = c; c = tmp;
  }

  var ta = new Triangle(a, b, c, 0),
      tb = new Triangle(d, b, a, 1),
      tc = new Triangle(c, d, a, 2),
      td = new Triangle(b, d, c, 3),
      triangles = [ta, tb, tc, td];

  neighbors(ta.a, tb.b);
  neighbors(ta.b, td.c);
  neighbors(ta.c, tc.c);

  neighbors(tb.a, td.a);
  neighbors(td.b, tc.a);
  neighbors(tc.b, tb.c);

  // Initialise conflict graph.
  for (var i = 4; i < n; ++i) {
    var p = points[i];
    addConflict(ta, p, i);
    addConflict(tb, p, i);
    addConflict(tc, p, i);
    addConflict(td, p, i);
  }

  for (var i = 4; i < n; ++i) {
    var p = points[i], h = p.visible;
    if (!h) continue;

    // Find horizon.
    var horizon = null, a = h;
    do a.t.marked = true; while (a = a.nextF);

    a = h; do {
      var t = a.t;
      if (horizon = findHorizon(t.a) || findHorizon(t.b) || findHorizon(t.c)) break;
    } while (a = a.nextF);

    if (!horizon) continue;

    for (var j = 0, m = horizon.length, prev = null, first = null; j < m; ++j) {
      var e = horizon[j],
          f1 = e.triangle, f2 = e.neighbor.triangle,
          t = new Triangle(p, e.neighbor.p, e.p, triangles.length);
      neighbors(t.b, e);
      if (prev) neighbors(prev.a, t.c);
      else first = t;
      addConflicts(t, f1, f2);
      triangles.push(prev = t);
    }
    neighbors(prev.a, first.c);

    a = h; do {
      var t = a.t;
      for (var j = 0, m = t.visible.length; j < m; ++j) t.visible[j].remove();
      t.visible.length = 0;
      removeElement(triangles, t.index);
    } while (a = a.nextF);
  }
  return triangles;
}

function removeElement(array, i) {
  var x = array.pop();
  if (i < array.length) (array[i] = x).index = i;
}

function circumcentre(t) {
  var p0 = t.a.p,
      p1 = t.b.p,
      p2 = t.c.p,
      n = cross(subtract(t.c.p, t.a.p), subtract(t.b.p, t.a.p)),
      m2 = 1 / norm2(n),
      m = Math.sqrt(m2),
      radius = asin(.5 * m * norm(subtract(p0, p1)) * norm(subtract(p1, p2)) * norm(subtract(p2, p0))),
      α = .5 * m2 * norm2(subtract(p1, p2)) * dot(subtract(p0, p1), subtract(p0, p2)),
      β = .5 * m2 * norm2(subtract(p0, p2)) * dot(subtract(p1, p0), subtract(p1, p2)),
      γ = .5 * m2 * norm2(subtract(p0, p1)) * dot(subtract(p2, p0), subtract(p2, p1)),
      centre = [
        α * p0[0] + β * p1[0] + γ * p2[0],
        α * p0[1] + β * p1[1] + γ * p2[1],
        α * p0[2] + β * p1[2] + γ * p2[2]
      ],
      k = norm2(centre);
  if (k > ε) centre[0] *= (k = 1 / Math.sqrt(k)), centre[1] *= k, centre[2] *= k;
  else centre = t.n;
  if (!visible(t, centre)) centre[0] *= -1, centre[1] *= -1, centre[2] *= -1, radius = π - radius, centre.negative = true;
  centre.radius = radius;
  return centre;
}

function norm2(p) { return dot(p, p); }
function norm(p) { return Math.sqrt(norm2(p)); }

function dot(a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function cross(a, b) {
  return [a[1] * b[2] - a[2] * b[1],
          a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]];
}

function asin(x) {
  return Math.asin(Math.max(-1, Math.min(1, x)));
}

function subtract(a, b) {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}

function visible(t, p) {
  return dot(t.n, p) - dot(t.n, t.a.p) > ε;
}

function coplanar(t, p) {
  return Math.abs(dot(t.n, p) - dot(t.n, t.a.p)) <= ε;
}

function normalise(d) {
  var m = 1 / norm(d);
  d[0] *= m, d[1] *= m, d[2] *= m;
  return d;
}

function angle(a, b) {
  return Math.acos(dot(a, b) / (norm(a) * norm(b)));
}

function spherical(cartesian) {
  return [
    Math.atan2(cartesian[1], cartesian[0]) * degrees,
    asin(cartesian[2]) * degrees
  ];
}

function cartesian(spherical) {
  var λ = spherical[0] * radians,
      φ = spherical[1] * radians,
      cosφ = Math.cos(φ);
  return [
    cosφ * Math.cos(λ),
    cosφ * Math.sin(λ),
    Math.sin(φ)
  ];
}

function Arc(t, v, i) {
  var head;
  this.t = t;
  this.v = v;
  this.i = i;
  this.prevF = null;
  if (head = this.nextF = v.visible) head.prevF = this;
  v.visible = this;
}

Arc.prototype.remove = function() {
  if (this.prevF) this.prevF.nextF = this.nextF;
  else this.v.visible = this.nextF;
  if (this.nextF) this.nextF.prevF = this.prevF;
};

function addConflict(t, p, i) {
  if (visible(t, p)) t.visible.push(new Arc(t, p, i));
}

// Maintain order of vertices in facet conflict lists when merging.
function addConflicts(t, a, b) {
  var av = a.visible,
      bv = b.visible,
      an = av.length,
      bn = bv.length,
      ai = 0,
      bi = 0;
  while (ai < an || bi < bn) {
    if (ai < an) {
      var ax = av[ai];
      if (bi < bn) {
        var bx = bv[bi];
        if (ax.i > bx.i) {
          addConflict(t, bx.v, bx.i), ++bi;
          continue;
        }
        if (ax.i === bx.i) ++bi;
      }
      addConflict(t, ax.v, ax.i), ++ai;
    } else {
      var bx = bv[bi];
      addConflict(t, bx.v, bx.i), ++bi;
    }
  }
}

function Triangle(a, b, c, index) {
  this.visible = [];
  this.marked = false;
  this.n = normalise(cross(subtract(c, a), subtract(b, a)));
  (((this.a = new Edge(this, a)).next = this.b = new Edge(this, b)).next = this.c = new Edge(this, c)).next = this.a;
  this.index = index;
}

function Edge(triangle, p) {
  this.triangle = triangle;
  this.p = p;
  this.neighbor = this.next = null;
}

function onHorizon(e) {
  return !e.triangle.marked && e.neighbor.triangle.marked;
}

// Assume e is marked.
function findHorizon(e) {
  if ((e = e.neighbor).triangle.marked) return;
  var horizon = [e], h0 = e;
  do {
    if (onHorizon(e = e.next)) {
      if (e === h0) return horizon;
      horizon.push(e);
    } else {
      e = e.neighbor;
    }
  } while (1);
}

function neighbors(a, b) {
  (a.neighbor = b).neighbor = a;
}

})();
