/* =====================================================================
   Wise-Teck v3 — live wave art (hero, section dividers, footer)
   - Drawn in the browser as SVG, at the element's real pixel width (never stretched)
   - 2D style: layered flat ribbons (no fine lines), lavender / periwinkle / violet + gold & navy
   - Slow continuous motion: each layer ripples at its own speed; pauses off-screen / hidden tab;
     visitors who prefer reduced motion get a still drawing
   Targets (already in the page as static fallbacks): svg.wv-hero-art, svg.wv-div-art, svg.wv-foot-art
   ===================================================================== */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var REDUCE = (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) || /[?&]static/.test(location.search);   // ?static = still frame (testing/screenshots)
  var uid = 0;

  /* ---------- maths ---------- */
  function s01(t) { t = t < 0 ? 0 : t > 1 ? 1 : t; return t * t * t * (t * (6 * t - 15) + 10); }
  function crEval(A, u) {                      // Catmull-Rom through anchors [[u, y], ...] (u sorted 0..1)
    var n = A.length, i = 0;
    while (i < n - 2 && u > A[i + 1][0]) i++;
    var p1 = A[i], p2 = A[i + 1];
    var p0 = i > 0 ? A[i - 1] : [2 * p1[0] - p2[0], 2 * p1[1] - p2[1]];
    var p3 = i + 2 < n ? A[i + 2] : [2 * p2[0] - p1[0], 2 * p2[1] - p1[1]];
    var t = (u - p1[0]) / Math.max(1e-6, p2[0] - p1[0]);
    return 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t * t +
      (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t * t * t);
  }
  function seg(P) {                            // smooth cubic segments through points (Catmull-Rom -> Bezier)
    var d = "";
    for (var i = 0; i < P.length - 1; i++) {
      var p0 = P[i - 1] || P[i], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2] || p2;
      d += "C" + (p1[0] + (p2[0] - p0[0]) / 6).toFixed(1) + " " + (p1[1] + (p2[1] - p0[1]) / 6).toFixed(1) + " " +
        (p2[0] - (p3[0] - p1[0]) / 6).toFixed(1) + " " + (p2[1] - (p3[1] - p1[1]) / 6).toFixed(1) + " " +
        p2[0].toFixed(1) + " " + p2[1].toFixed(1);
    }
    return d;
  }
  function band(xs, top, bot) {                // closed ribbon between two curves sampled at xs
    var T = [], B = [];
    for (var i = 0; i < xs.length; i++) { T.push([xs[i], top[i]]); B.push([xs[i], bot[i]]); }
    B.reverse();
    return "M" + T[0][0].toFixed(1) + " " + T[0][1].toFixed(1) + seg(T) +
      "L" + B[0][0].toFixed(1) + " " + B[0][1].toFixed(1) + seg(B) + "Z";
  }
  function samples(x0, x1, step) { var a = [], n = Math.max(3, Math.round((x1 - x0) / step)); for (var i = 0; i <= n; i++) a.push(x0 + (x1 - x0) * i / n); return a; }

  /* ---------- svg helpers ---------- */
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  function grad(defs, stops, dir) {           // dir: "h" left->right, "v" top->bottom, "hr" right->left
    var id = "wvg" + (++uid);
    var g = el("linearGradient", dir === "v" ? { id: id, x1: 0, y1: 0, x2: 0, y2: 1 } : dir === "hr" ? { id: id, x1: 1, y1: 0, x2: 0, y2: 0 } : { id: id, x1: 0, y1: 0, x2: 1, y2: 0 }, defs);
    stops.forEach(function (s) { el("stop", { offset: s[0], "stop-color": s[1], "stop-opacity": s[2] == null ? 1 : s[2] }, g); });
    return "url(#" + id + ")";
  }

  /* palette — flat 2D lavender family (no white) */
  var C = { wash: "#dfe3fb", a: "#cbd2f7", sheen: "#e6e2fd", b: "#b7c0f1", c: "#a3adeb", v: "#8c79ef", gold1: "#f0d27a", gold2: "#d4af37", gold3: "#8a6a1f", navy1: "#1c3d92", navy2: "#0d2158" };

  /* ======================= HERO (height 320) ======================= */
  function hero(svg) {
    var H = 320, defs = el("defs", {}, svg), P = {};
    var F = [[0, 150], [0.333, 186], [0.639, 160], [0.833, 118], [1, 66]];   // the shared flow path
    var fills = {
      wash: grad(defs, [[0, C.wash, .9], [.6, C.wash, .5], [1, C.wash, 0]], "v"),
      a: grad(defs, [[0, "#d3d9f8", .95], [1, "#bdc5f2", .75]], "v"),
      sheen: grad(defs, [[0, C.sheen, .95], [1, C.sheen, .55]]),
      b: grad(defs, [[0, "#c4ccf4"], [1, C.b]]),
      c: grad(defs, [[0, C.c, .85], [.6, C.c, .45], [1, C.c, 0]], "v"),          // lowest ribbon melts away at its bottom edge
      v: grad(defs, [[0, C.v, .25], [.5, C.v, .55], [1, C.v, .3]]),
      gold: grad(defs, [[0, C.gold1], [.5, C.gold2], [1, C.gold3]]),
      goldHi: grad(defs, [[0, "#fff6d8", .85], [1, "#fff6d8", 0]], "v"),
      navy: grad(defs, [[0, C.navy2], [1, C.navy1]])
    };
    ["wash", "a", "b", "sheen", "v", "c"].forEach(function (k) { P[k] = el("path", { fill: fills[k], opacity: k === "wash" ? 1 : k === "v" ? 1 : .92, "class": "wv-soft" }, svg); });
    P.page = el("path", { fill: "#f7f8fe", "class": "wv-page" }, svg);   // page colour under the silk (inner pages only)
    P.gold = el("path", { fill: fills.gold, "class": "wv-gold" }, svg);
    P.goldHi = el("path", { fill: fills.goldHi, "class": "wv-gold" }, svg);
    P.navy = el("path", { fill: fills.navy, "class": "wv-navy" }, svg);
    P.navyHi = el("path", { fill: "#6f8fd8", opacity: .28, "class": "wv-navy" }, svg);
    return function draw(W, t) {
      // UNIFORM + SYMMETRIC: every layer (silk, gold, navy) rides ONE shared curve Y(u) with fixed
      // offsets and fixed widths, so all bends match exactly. The curve = a gentle bowl (lowest in the
      // middle, rising evenly to both edges) + two evenly spaced bends, symmetric about the centre.
      // The whole stack breathes together (shared amplitude), so it stays uniform while moving.
      var xs = samples(0, W, 10), n = xs.length, breathe = .88 + .12 * Math.sin(.45 * t);
      var Y = [];
      for (var i = 0; i < n; i++) {
        var u = xs[i] / W, e = Math.abs(2 * u - 1);
        // one clean symmetric wave: crests at both edges and in the middle, two even dips between
        Y.push(226 - 36 * breathe * Math.cos(4 * Math.PI * (u - .5)) - 0 * e);
      }
      function L(top, bottom) {                     // band between two fixed offsets from the shared curve
        return band(xs, Y.map(function (y) { return y + top; }), Y.map(function (y) { return y + bottom; }));
      }
      P.wash.setAttribute("d", L(-100, -8));        // soft wash behind the stripes (fades downward)
      P.a.setAttribute("d", L(-84, -52));           // stripes, top to bottom - equal spacing, constant widths
      P.sheen.setAttribute("d", L(-84, -77));
      P.b.setAttribute("d", L(-46, -26));
      P.v.setAttribute("d", L(-21, -17));
      P.c.setAttribute("d", L(-13, -2));
      P.page.setAttribute("d", L(-3, H - 160));
      P.gold.setAttribute("d", L(0, 18));           // gold ribbon (tucks under the navy)
      P.goldHi.setAttribute("d", L(0, 6));
      P.navy.setAttribute("d", L(14, 44));          // navy band directly beneath
      P.navyHi.setAttribute("d", L(14, 20));
    };
  }

  /* ======================= DIVIDER (height 130) ======================= */
  function divider(svg, flip) {
    var H = 130, defs = el("defs", {}, svg), P = [];
    var sides = [1, -1];
    sides.forEach(function (sd) {
      var dir = sd === 1 ? "h" : "hr";
      P.push({ sd: sd, a: el("path", { fill: grad(defs, [[0, C.a, .95], [.65, C.a, .55], [1, C.a, 0]], dir), "class": "wv-soft" }, svg),
        b: el("path", { fill: grad(defs, [[0, C.b, .9], [.7, C.b, .45], [1, C.b, 0]], dir), "class": "wv-soft" }, svg),
        v: el("path", { fill: grad(defs, [[0, C.v, .5], [1, C.v, 0]], dir), "class": "wv-soft" }, svg) });
    });
    var base = flip ? H * .40 : H * .62, rise = flip ? -44 : 44;
    return function draw(W, t) {
      var reach = W * .46, xs = samples(0, reach, 14);
      function curve(off, th, ripA, sp, ph) {
        var top = [], bot = [];
        for (var i = 0; i < xs.length; i++) {
          var u = xs[i] / reach, taper = 1 - s01(u), c = base - rise * Math.pow(1 - Math.min(u, 1), 2);
          var rip = ripA * taper * Math.sin(2 * Math.PI * 1.3 * u - sp * t + ph);
          top.push(c + off + rip - th * taper / 2); bot.push(c + off + rip + th * taper / 2);
        }
        return [top, bot];
      }
      var A = curve(0, 44, 5, .35, 0), B = curve(14, 22, 6, .5, 1.6), V = curve(26, 6, 4, .6, 2.6);
      P.forEach(function (p) {
        var xx = p.sd === 1 ? xs : xs.map(function (x) { return W - x; });
        p.a.setAttribute("d", band(xx, A[0], A[1]));
        p.b.setAttribute("d", band(xx, B[0], B[1]));
        p.v.setAttribute("d", band(xx, V[0], V[1]));
      });
    };
  }

  /* ======================= FOOTER TOP (height 170) ======================= */
  function footer(svg) {
    var H = 170, defs = el("defs", {}, svg);
    var l2 = el("path", { fill: grad(defs, [[0, C.b, .55], [.5, C.a, .35], [1, C.b, .55]]), "class": "wv-soft" }, svg);
    var l1 = el("path", { fill: grad(defs, [[0, C.c, .75], [.5, C.b, .5], [1, C.c, .75]]), "class": "wv-soft" }, svg);
    var gold = el("path", { fill: grad(defs, [[0, "#e2c25a"], [.15, C.gold3], [.5, C.gold1], [.85, C.gold3], [1, "#e2c25a"]]) }, svg);
    var goldHi = el("path", { fill: grad(defs, [[0, "#fff6d8", .8], [1, "#fff6d8", 0]], "v") }, svg);
    // brand navy, matching the footer body colour where the wave ends (see wise-teck.css)
    var navy = el("path", { fill: "#0d2158" }, svg);   // flat; the footer body continues the same colour
    var navyHi = el("path", { fill: "#6f8fd8", opacity: .22 }, svg);
    return function draw(W, t) {
      // three clean, even, symmetric waves (+ a gentle overall dip); breathes in place
      var xs = samples(0, W, 10), breathe = .86 + .14 * Math.sin(.5 * t);
      var ny = [], gt = [], gb = [], gh = [], a1 = [], b1 = [], a2 = [], b2 = [], nb = [], nh = [];
      for (var i = 0; i < xs.length; i++) {
        var T = 2 * Math.PI * (xs[i] - W / 2) / W, e = Math.abs(2 * xs[i] / W - 1);
        var y = 104 + 8 * Math.cos(T) + 18 * breathe * Math.cos(3 * T);
        var thick = 9 + 9 * Math.pow(e, 2);                     // slim gold, slightly fuller at the edges
        ny.push(y); gt.push(y - thick); gb.push(y + 14); gh.push(y - thick * .5);
        a1.push(y - thick - 24); b1.push(y - thick - 4);         // lavender layer right above the gold
        a2.push(y - thick - 48); b2.push(y - thick - 30);        // lighter lavender layer above that
        nb.push(H + 1); nh.push(y + 7);
      }
      l2.setAttribute("d", band(xs, a2, b2));
      l1.setAttribute("d", band(xs, a1, b1));
      gold.setAttribute("d", band(xs, gt, gb));
      goldHi.setAttribute("d", band(xs, gt, gh));
      navy.setAttribute("d", band(xs, ny, nb));
      navyHi.setAttribute("d", band(xs, ny, nh));
    };
  }

  /* ======================= wiring ======================= */
  var items = [];
  function add(svg, H, make) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);          // replace the static fallback
    svg.setAttribute("preserveAspectRatio", "none");
    var it = { svg: svg, H: H, draw: make(svg), visible: true, W: 0 };
    items.push(it);
    return it;
  }
  [].forEach.call(document.querySelectorAll("svg.wv-hero-art"), function (s) { add(s, 320, hero); });
  [].forEach.call(document.querySelectorAll("svg.wv-div-art"), function (s) {
    var flip = s.getAttribute("data-wave") === "wv-div-b";
    add(s, 130, function (svg) { return divider(svg, flip); });
  });
  [].forEach.call(document.querySelectorAll("svg.wv-foot-art"), function (s) { add(s, 170, footer); });
  if (!items.length) return;

  function size(it) {
    var W = Math.max(320, Math.round(it.svg.getBoundingClientRect().width || 1440));
    if (W !== it.W) { it.W = W; it.svg.setAttribute("viewBox", "0 0 " + W + " " + it.H); }
  }
  var t0 = performance.now();
  function frame(now, force) {
    var t = REDUCE ? 0 : (now - t0) / 1000;
    items.forEach(function (it) { if (force || it.visible) { size(it); it.draw(it.W, t); } });
  }
  frame(t0, true);
  addEventListener("resize", function () { frame(performance.now(), true); });
  if (REDUCE) return;

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { items.forEach(function (it) { if (it.svg === e.target) it.visible = e.isIntersecting; }); }); }, { rootMargin: "120px" });
    items.forEach(function (it) { io.observe(it.svg); });
  }
  var last = 0;
  (function loop(now) {
    if (!document.hidden && now - last > 33) { last = now; frame(now); }   // ~30 fps is plenty for slow silk
    requestAnimationFrame(loop);
  })(performance.now());
})();
