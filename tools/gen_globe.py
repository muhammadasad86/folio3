"""Globe data for the contact-section 3D globe: Fibonacci-sphere land dots + coastline rings (Natural Earth land-110m via
world-atlas@2.0.2), packed as base64 Int16 (lat*100, lon*100). Offices verified on https://www.folio3.com/contact-us (21 Oct 2026)."""
import json, sys, math, base64
from pathlib import Path
import numpy as np
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parent.parent
topo = json.load(open(sys.argv[1]))
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
arcs = []
for a in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in a: x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
arc = lambda i: arcs[i] if i >= 0 else arcs[~i][::-1]
def ring(idx):
    pts = []
    for i in idx: a = arc(i); pts.extend(a if not pts else a[1:])
    return pts
polys = []
for g in topo["objects"]["land"]["geometries"]:
    polys += [[ring(r) for r in g["arcs"]]] if g["type"] == "Polygon" else [[ring(r) for r in p] for p in g["arcs"]]

N = int(sys.argv[2]) if len(sys.argv) > 2 else 26000
i = np.arange(N) + .5
lat = np.degrees(np.arcsin(1 - 2 * i / N)); lon = (np.degrees(np.pi * (1 + 5 ** .5) * i) % 360) - 180
P = np.c_[lon, lat]; land = np.zeros(N, bool)
for poly in polys:
    m = MPath(poly[0]).contains_points(P)
    for h in poly[1:]: m &= ~MPath(h).contains_points(P)
    land |= m
land &= lat > -60
pack = lambda a: base64.b64encode(np.round(np.asarray(a) * 100).astype("<i2").tobytes()).decode()
dots = np.c_[lat[land], lon[land]].ravel()
coast = []
for poly in polys:
    r = poly[0]
    if max(p[1] for p in r) < -60 or len(r) < 4: continue
    coast.append(pack(np.array([(p[1], p[0]) for p in r]).ravel()))
OFFICES = [  # country, cities, lat, lon, label direction
    ("United States", "San Mateo · Pleasanton, CA", 37.60, -122.10, "w"), ("Canada", "Toronto", 43.65, -79.38, "e"),
    ("Mexico", "Zapopan, Jalisco", 20.72, -103.39, "w"), ("United Kingdom", "Woking", 51.32, -0.56, "w"),
    ("Bulgaria", "Sofia", 42.70, 23.32, "e"), ("Saudi Arabia", "Riyadh", 24.71, 46.68, "sw"),
    ("UAE", "Dubai", 25.10, 55.17, "s"), ("Pakistan", "Karachi · Lahore · Islamabad", 33.69, 73.05, "ne"),
    ("Australia", "North Sydney", -33.84, 151.21, "e")]
EXTRA = [(24.86, 67.01), (31.52, 74.36)]  # Karachi, Lahore (Pakistan marker sits on Islamabad)
ROUTES = [("United States", "Canada"), ("United States", "Mexico"), ("Canada", "United Kingdom"), ("United Kingdom", "Bulgaria"),
          ("United Kingdom", "UAE"), ("Bulgaria", "Saudi Arabia"), ("UAE", "Pakistan"), ("Saudi Arabia", "UAE"), ("Pakistan", "Australia"), ("UAE", "Australia")]
out = {"dots": pack(dots), "coast": coast,
       "offices": [{"c": c, "city": city, "lat": la, "lon": lo, "dir": d} for c, city, la, lo, d in OFFICES],
       "extra": [{"lat": a, "lon": b} for a, b in EXTRA], "routes": ROUTES}
(ROOT / "assets/map").mkdir(parents=True, exist_ok=True)
json.dump(out, open(ROOT / "assets/map/globe.json", "w"), separators=(",", ":"))
print("dots", int(land.sum()), "coast rings", len(coast), "coast pts", sum(len(base64.b64decode(c)) // 4 for c in coast),
      "bytes", (ROOT / "assets/map/globe.json").stat().st_size)
