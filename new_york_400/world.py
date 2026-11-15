"""Procedural 3D world of lower Manhattan and the harbour, 1600-2026.

Units are metres. x = east, y = up, z = south (north is -z). The Battery tip is at (0, 0).
Everything that changes over time carries birth/death years; the renderer shows the state for
any given year.
"""
import math
import random

import cairo
import numpy as np
from PIL import Image, ImageFilter

X0, X1, Z0, Z1 = -3600.0, 4600.0, -9000.0, 3200.0
CELL = 20.0
NX = int((X1 - X0) / CELL) + 1
NZ = int((Z1 - Z0) / CELL) + 1
WATER_Y = -7.0
INF = 1e6

# ------------------------------------------------------------------ coastlines (x, z)
MAN_W = [(0, 30), (-70, -40), (-130, -250), (-230, -700), (-290, -1400), (-340, -2400), (-380, -3500), (-420, -5000),
         (-480, -7000), (-520, -9400)]
MAN_E = [(0, 30), (90, 10), (200, -120), (420, -380), (640, -700), (900, -1150), (1150, -1700), (1450, -2400),
         (1750, -3100), (2050, -3900), (2200, -4400), (1950, -4900), (1900, -6000), (2000, -7500), (2100, -9400)]
MAN_W_FILL = [(-20, 160), (-170, 60), (-240, -220), (-360, -700), (-420, -1400), (-460, -2400), (-470, -3500),
              (-480, -5000), (-500, -7000), (-520, -9400)]
MAN_E_FILL = [(-20, 160), (200, 100), (330, -60), (560, -330), (800, -680), (1060, -1140), (1290, -1700),
              (1560, -2400), (1830, -3100), (2100, -3900), (2240, -4400), (2000, -4900), (1950, -6000),
              (2040, -7500), (2100, -9400)]
BROOKLYN = [(1450, 3400), (1500, 2000), (1420, 1250), (1080, 450), (1200, 0), (1400, -500), (1650, -1100),
            (1900, -1700), (2200, -2400), (2500, -3100), (2850, -3900), (3000, -4400), (2750, -4900), (2700, -6000),
            (2800, -7500), (2900, -9400), (4800, -9400), (4800, 3400)]
NEW_JERSEY = [(-1500, 3400), (-1450, 1600), (-1350, 800), (-1400, 0), (-1500, -1000), (-1600, -2500),
              (-1700, -4000), (-1800, -6000), (-1900, -9400), (-3800, -9400), (-3800, 3400)]
GOVERNORS = ((900, 1000), (380, 260))
LIBERTY = ((-1150, 1500), (110, 90))
COLLECT = ((420, -2100), (220, 150))

# ------------------------------------------------------------------ growth of the city
URBAN_FRONT = [(1624, 60), (1625, -120), (1640, -330), (1653, -560), (1680, -700), (1700, -850), (1730, -1150),
               (1760, -1500), (1776, -1800), (1800, -2500), (1820, -3500), (1840, -5200), (1860, -8000),
               (1880, -9400)]


def urban_year_at(z, x=0.0):
    """Year the built-up city reaches a point (east side along the East River slightly earlier)."""
    ys = [y for y, _ in URBAN_FRONT]
    zs = [zz for _, zz in URBAN_FRONT]
    if z >= zs[0]:
        return 1600.0
    if z <= zs[-1]:
        return ys[-1]
    for (y0, z0), (y1, z1) in zip(URBAN_FRONT, URBAN_FRONT[1:]):
        if z1 <= z <= z0:
            yr = y0 + (y1 - y0) * (z0 - z) / (z0 - z1)
            return yr - 6.0 * math.tanh(x / 600.0)  # east side a little earlier
    return 1900.0


def _rng(seed):
    return np.random.default_rng(seed)


def fbm(h, w, seed, octaves=6, base=4):
    rng = _rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        small = rng.random((n + 1, n + 1)).astype(np.float32)
        big = np.asarray(Image.fromarray(small).resize((w, h), Image.BICUBIC), np.float32)
        out += big * amp
        tot += amp
        amp *= 0.5
    return out / tot


def raster_mask(polys=(), ellipses=(), scale=1.0, w=NX, h=NZ):
    """Rasterise polygons/ellipses (world coords) onto the terrain grid. Returns float mask 0..1."""
    s = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
    c = cairo.Context(s)
    c.scale(1 / CELL, 1 / CELL)
    c.translate(-X0, -Z0)
    for p in polys:
        c.move_to(*p[0])
        for q in p[1:]:
            c.line_to(*q)
        c.close_path()
        c.fill()
    for (cx, cz), (rx, rz) in ellipses:
        c.save()
        c.translate(cx, cz)
        c.scale(rx, rz)
        c.arc(0, 0, 1, 0, 2 * math.pi)
        c.restore()
        c.fill()
    s.flush()
    a = np.frombuffer(s.get_data(), np.uint8).reshape(h, s.get_stride())[:, :w]
    return a.astype(np.float32) / 255.0


def blur(a, px):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(px)), np.float32) / 255.0


def man_poly(fill=False):
    w = MAN_W_FILL if fill else MAN_W
    e = MAN_E_FILL if fill else MAN_E
    return w + e[::-1][:-1]


class World:
    def __init__(self):
        self.rng = random.Random(7)
        self._terrain()
        self._roads()
        self._instances()

    # ---------------------------------------------------------------- terrain
    def _terrain(self):
        xs = X0 + np.arange(NX) * CELL
        zs = Z0 + np.arange(NZ) * CELL
        GX, GZ = np.meshgrid(xs, zs)
        self.gx, self.gz = GX, GZ
        man0 = raster_mask([man_poly()])
        manF = raster_mask([man_poly(True)])
        other = raster_mask([BROOKLYN, NEW_JERSEY], [GOVERNORS, LIBERTY])
        collect = raster_mask((), [COLLECT])
        n1 = fbm(NZ, NX, 1)
        n2 = fbm(NZ, NX, 2, base=16)
        north = np.clip(-GZ / 6000.0, 0, 1)
        bk = raster_mask([BROOKLYN])
        nj = raster_mask([NEW_JERSEY])

        def heights(land):
            sm = blur(land, 3)
            coast = np.clip((sm - 0.35) / 0.3, 0, 1)
            h = 2.0 + coast * (3 + 16 * n1 * (0.5 + north) + 6 * n2)
            h += blur(bk, 6) * 14 * np.clip((GZ + 3000) / 2000, 0, 1) * np.clip((-GZ + 400) / 600, 0, 1)
            pal = np.clip((-GZ - 3200) / 600, 0, 1) * blur(nj, 2)
            h += pal * 55 * np.clip((sm - 0.5) / 0.2, 0, 1)
            h = np.where(sm > 0.5, h, WATER_Y + (h - WATER_Y) * np.clip(sm / 0.5, 0, 1) ** 2)
            return h.astype(np.float32), sm, pal

        hA, smA, _ = heights(np.clip(man0 + other, 0, 1))
        hB, sm, pal = heights(np.clip(manF + other, 0, 1))
        cb = blur(collect, 2)
        self.h_a, self.h_b = hA, hB
        self.h_land = hB
        orig = blur(man0, 4)
        frac = np.clip(1 - orig / 0.5, 0, 1)
        west = np.clip((-GX + 150) / 300, 0, 1)
        batt = np.clip((GZ + 200) / 260, 0, 1)
        fy = 1695 + 135 * frac + 35 * west
        fy = fy * (1 - batt) + (1800 + 50 * frac) * batt
        for _ in range(3):
            k = 5
            fy = np.cumsum(np.pad(fy, ((0, 0), (k, k)), mode="edge"), 1)
            fy = (fy[:, 2 * k:] - fy[:, :-2 * k]) / (2 * k)
            fy = np.cumsum(np.pad(fy, ((k, k), (0, 0)), mode="edge"), 0)
            fy = (fy[2 * k:, :] - fy[:-2 * k, :]) / (2 * k)
        self.fill_year = fy.astype(np.float32)
        wet_from = np.full_like(hB, -INF)
        wet_to = np.full_like(hB, -INF)
        wet_to = np.where(cb > 0.5, 1811.0, wet_to)
        wet_from = np.where(cb > 0.5, -INF, wet_from)
        self.wet_from, self.wet_to = wet_from.astype(np.float32), wet_to.astype(np.float32)
        self.fill_zone = (hB > 0.5) & (hA <= 0.5)
        # land use years
        uz = np.vectorize(urban_year_at)(GZ, GX).astype(np.float32)
        on_man = blur(manF, 1) > 0.5
        urban = np.where(on_man, uz + 6 * n2, INF)
        # Brooklyn / NJ shores urbanise in the 19th century
        dist_shore_bk = 1 - blur(bk, 20)
        urban = np.where(bk > 0.5, 1830 + 160 * np.clip(dist_shore_bk * 1.5, 0, 1) + 10 * n1, urban)
        urban = np.where(nj > 0.5, 1850 + 170 * np.clip((1 - blur(nj, 20)) * 1.5, 0, 1) + 10 * n1, urban)
        urban = np.where(pal > 0.4, INF, urban)
        farm = np.where(on_man & (n1 > 0.42), np.maximum(1632, urban - 45 - 20 * n2), INF)
        farm = np.where((bk > 0.5) & (n1 > 0.5), 1650 + 90 * n2, farm)
        farm = np.where((nj > 0.5) & (n1 > 0.55), 1670 + 100 * n2, farm)
        farm = np.where(pal > 0.4, INF, farm)
        # parks never built on
        park = raster_mask([[(-90, -1300), (230, -1300), (250, -1650), (-110, -1650)]], [((40, -230), (35, 25))])
        urban = np.where(park > 0.5, INF, urban)
        self.park = park
        forest = np.clip((n1 - 0.12) * 4, 0, 1) * (sm > 0.55)
        forest = np.where(cb > 0.2, 0, forest)
        self.forest = forest.astype(np.float32)
        self.farm_year = farm.astype(np.float32)
        self.urban_year = urban.astype(np.float32)
        # Lenape fields around villages
        fields = raster_mask((), [((640, -2180), (260, 170)), ((-330, -3600), (200, 220)), ((1300, -3300), (250, 200))])
        self.lenape_field = blur(fields, 4)
        self.on_manhattan = on_man
        self.land_now = sm

    def _line_mask(self, pts, width):
        s = cairo.ImageSurface(cairo.FORMAT_A8, NX, NZ)
        c = cairo.Context(s)
        c.scale(1 / CELL, 1 / CELL)
        c.translate(-X0, -Z0)
        c.set_line_width(width)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.stroke()
        s.flush()
        return np.frombuffer(s.get_data(), np.uint8).reshape(NZ, s.get_stride())[:, :NX].astype(np.float32) / 255.0

    def _ij(self, x, z):
        return int(np.clip((z - Z0) / CELL, 0, NZ - 1)), int(np.clip((x - X0) / CELL, 0, NX - 1))

    def height_at(self, x, z, year):
        i, j = self._ij(x, z)
        f = min(1.0, max(0.0, (year - self.fill_year[i, j] + 3) / 3))
        h = self.h_a[i, j] + (self.h_b[i, j] - self.h_a[i, j]) * f
        if self.wet_from[i, j] <= year < self.wet_to[i, j]:
            return WATER_Y
        return float(h)

    def land_ok(self, x, z, year):
        return self.height_at(x, z, year) > 0.5

    def wet_until(self, x, z):
        i, j = self._ij(x, z)
        if self.h_b[i, j] <= 0.5:
            return INF
        w = -INF
        if self.h_a[i, j] <= 0.5:
            w = float(self.fill_year[i, j])
        if self.wet_to[i, j] > -INF / 2 and self.wet_to[i, j] < INF / 2:
            w = max(w, float(self.wet_to[i, j]))
        return w

    # ---------------------------------------------------------------- roads (data texture)
    RX0, RX1, RZ0, RZ1, RRES = -800.0, 2600.0, -9000.0, 600.0, 2.5

    def _roads(self):
        streets = []

        def S(pts, year, w=11.0):
            streets.append((pts, year, w))

        S([(30, -200), (-20, -450), (-60, -700), (-90, -1100), (-110, -1500), (-100, -2000), (-60, -2600),
           (60, -3300), (250, -4200), (500, -5200), (800, -6200), (1050, -7200), (1250, -8200)], 1625, 15)  # Broadway
        S([(150, -1450), (450, -1900), (700, -2400), (950, -3000), (1200, -3600), (1350, -4200)], 1640, 13)  # Bowery
        S([(120, -120), (300, -300), (450, -500), (560, -650), (700, -900), (800, -1100)], 1625)  # Pearl
        S([(60, -160), (200, -260)], 1630)
        S([(0, -60), (120, -120)], 1625)
        S([(30, -260), (320, -320)], 1640)
        S([(300, -235), (230, -350), (170, -470), (150, -640)], 1676, 16)  # Broad St (after canal filled)
        S([(-240, -650), (150, -660), (620, -680)], 1660, 10)  # Wall St (path along the wall)
        S([(250, -300), (300, -650), (350, -1000)], 1660)
        S([(80, -660), (90, -1050), (120, -1400)], 1690)
        S([(-80, -900), (700, -950)], 1690)
        S([(-90, -1100), (850, -1150)], 1715)
        S([(-100, -1250), (950, -1300)], 1720)
        S([(220, -90), (400, -280), (560, -470), (720, -700), (880, -950)], 1705)
        S([(300, -40), (480, -230), (650, -430), (820, -700), (980, -950)], 1735)
        S([(380, 10), (560, -180), (730, -390), (900, -680), (1060, -950), (1200, -1300)], 1800)
        S([(-200, -200), (-270, -700), (-330, -1400), (-360, -2200)], 1760)
        S([(-350, -1650), (600, -1650)], 1760)
        self.streets = list(streets)
        # filler grids (pre-1811) west and east of Broadway
        rng = random.Random(3)
        for z in np.arange(-780, -2500, -95):
            y = urban_year_at(z, -200) + 2
            S([(-330, z), (-90, z + 8)], y, 9)
        for x in np.arange(-280, -100, 110):
            S([(x, -700), (x - 20, -2400)], urban_year_at(-1500, -200), 9)
        ang = math.radians(28)
        ca, sa = math.cos(ang), math.sin(ang)
        for i in range(-6, 14):
            ox, oz = 300 + i * 95 * ca, -1200 - i * 95 * sa
            p0 = (ox - 900 * sa, oz - 900 * ca)
            p1 = (ox + 900 * sa, oz + 900 * ca)
            S([p0, p1], urban_year_at(oz, ox) + 2, 9)
        for j in range(-6, 8):
            ox, oz = 300 - j * 110 * sa, -1200 - j * 110 * ca
            S([(ox - 1100 * ca, oz + 1100 * sa), (ox + 1100 * ca, oz - 1100 * sa)], urban_year_at(oz, ox) + 2, 9)
        # 1811 Commissioners' grid
        self.grid_streets = []
        for z in np.arange(-2600, -9000, -80):
            y = max(1811.0, urban_year_at(z, 500))
            S([(-560, z), (2300, z)], y, 10)
            self.grid_streets.append(z)
        for x in np.arange(-440, 2300, 250):
            S([(x, -2550), (x, -9000)], max(1811.0, urban_year_at(-3000, x)), 16)
        self.all_streets = streets
        w = int((self.RX1 - self.RX0) / self.RRES)
        h = int((self.RZ1 - self.RZ0) / self.RRES)
        tex = np.full((h, w), 9999.0, np.float32)
        for pts, year, width in streets:
            s = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
            c = cairo.Context(s)
            c.scale(1 / self.RRES, 1 / self.RRES)
            c.translate(-self.RX0, -self.RZ0)
            c.set_line_width(width)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.set_line_join(cairo.LINE_JOIN_ROUND)
            c.move_to(*pts[0])
            for p in pts[1:]:
                c.line_to(*p)
            c.stroke()
            s.flush()
            m = np.frombuffer(s.get_data(), np.uint8).reshape(h, s.get_stride())[:, :w] > 100
            tex = np.where(m & (tex > year), year, tex)
        self.road_tex = tex
        self.road_occ = tex < 9000

    def road_at(self, x, z):
        j = int((x - self.RX0) / self.RRES)
        i = int((z - self.RZ0) / self.RRES)
        if 0 <= i < self.road_tex.shape[0] and 0 <= j < self.road_tex.shape[1]:
            return self.road_tex[i, j] < 9000
        return False

    # ---------------------------------------------------------------- instances
    def _instances(self):
        I = {k: [] for k in ("house", "row", "tower", "spire", "tree", "pine", "longhouse", "canoe", "windmill",
                             "church", "palisade", "pier", "ship", "steamer", "fort", "special")}
        self.I = I
        R = self.rng

        def add(kind, pos, scale, rot=0.0, col=(1, 1, 1), col2=(1, 1, 1), birth=-INF, death=INF, var=None,
                move=(0, 0, 0, 0), mesh=None):
            I[kind].append(dict(pos=pos, scale=scale, rot=rot, col=col, col2=col2, birth=birth, death=death,
                                var=R.random() if var is None else var, move=move, mesh=mesh))

        self.add = add
        occ = {}

        def free(x, z, r=6):
            k = (int(x // r), int(z // r))
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if occ.get((k[0] + dx, k[1] + dz)):
                        return False
            return True

        def take(x, z, r=6):
            occ[(int(x // r), int(z // r))] = 1

        reserved = [((0, -120), 95), ((40, -230), 40), ((-90, -680), 30), ((110, -670), 25), ((80, -1475), 210),
                    ((420, -2100), 230), ((-70, -1100), 25)]

        def is_reserved(x, z):
            return any((x - a) ** 2 + (z - b) ** 2 < r * r for (a, b), r in reserved)

        def hc(*h):
            return tuple(int(h[0][i:i + 2], 16) / 255 for i in (1, 3, 5))

        walls_dutch = [hc("#B5533C"), hc("#C9783F"), hc("#E2C79A"), hc("#A9462F"), hc("#D9B98A"), hc("#8E3F2E")]
        walls_geo = [hc("#9A4A36"), hc("#B86A4A"), hc("#E6DDCB"), hc("#C9A27A"), hc("#7E3E30")]
        walls_fed = [hc("#8E3B2E"), hc("#A9533E"), hc("#6E2E26"), hc("#C9B8A0"), hc("#B0644A")]
        roofs = [hc("#5A3A30"), hc("#6E4A3A"), hc("#4A4A52"), hc("#7A3A2A")]
        fire1776 = lambda x, z: x < -40 and -1150 < z < -180 and not (x < -260)
        fire1835 = lambda x, z: x > 160 and -680 < z < -230

        # houses along streets
        for pts, year, width in self.all_streets:
            for (ax, az), (bx, bz) in zip(pts, pts[1:]):
                L = math.hypot(bx - ax, bz - az)
                if L < 1:
                    continue
                ux, uz = (bx - ax) / L, (bz - az) / L
                nx, nz = -uz, ux
                rot = math.atan2(nx, nz)
                d = 4.0
                while d < L - 4:
                    wdt = R.uniform(7, 10)
                    for side in (1, -1):
                        depth = R.uniform(10, 15)
                        off = width / 2 + depth / 2 + 1.5
                        x = ax + ux * d + nx * off * side
                        z = az + uz * d + nz * off * side
                        if not (-700 < x < 2400 and -9000 < z < 300):
                            continue
                        if is_reserved(x, z) or not free(x, z):
                            continue
                        if self.road_at(x, z):
                            continue
                        uy = urban_year_at(z, x)
                        wu = self.wet_until(x, z)
                        if wu >= INF:
                            continue
                        birth = max(year, uy + R.uniform(0, 14), wu + 3)
                        if birth > 1870:
                            continue
                        take(x, z)
                        frot = rot if side == 1 else rot + math.pi
                        death = INF
                        if birth < 1776.7 and fire1776(x, z):
                            death = 1776.72 + R.uniform(0, 0.004)
                        if birth < 1835.9 and fire1835(x, z):
                            death = min(death, 1835.96)
                        # modern replacement
                        death = min(death, 1885 + R.uniform(0, 70) + (40 if z < -3000 else 0))
                        self._house(add, x, z, frot, wdt, depth, birth, death, walls_dutch, walls_geo, walls_fed,
                                    roofs, R)
                        if death < 1840 and death > 1700:
                            nb = 1784 + R.uniform(0, 8) if death < 1780 else 1837 + R.uniform(0, 3)
                            self._house(add, x, z, frot, wdt, depth, nb, 1885 + R.uniform(0, 60), walls_dutch,
                                        walls_geo, walls_fed, roofs, R)
                    d += wdt + R.uniform(0.5, 3.5)

        # trees: forest on Manhattan + nearby shores
        fz = self.forest
        cnt = 0
        for _ in range(260000):
            x = R.uniform(-1500, 3200)
            z = R.uniform(-8800, 1700)
            i = int((z - Z0) / CELL)
            j = int((x - X0) / CELL)
            if fz[i, j] < R.random() * 0.9 + 0.1:
                continue
            if self.h_a[i, j] < 1.5 or self.wet_to[i, j] > -INF / 2:
                continue
            if self.lenape_field[i, j] > 0.4:
                continue
            death = min(self.farm_year[i, j] + R.uniform(-15, 5), self.urban_year[i, j])
            if x * x + (z + 120) ** 2 < 120 ** 2:
                death = 1624.7
            if not self.on_manhattan[i, j] and R.random() < 0.35:
                continue
            kind = "pine" if R.random() < 0.3 else "tree"
            s = R.uniform(9, 17)
            g = R.uniform(-0.06, 0.06)
            col = (0.20 + g, 0.36 + g + R.uniform(0, 0.08), 0.15 + g) if kind == "tree" else (0.14 + g, 0.28 + g, 0.17)
            add(kind, (x, float(self.h_land[i, j]), z), (s * 0.8, s * R.uniform(1.0, 1.4), s * 0.8),
                R.uniform(0, 6.28), col, (0.35, 0.25, 0.16), -INF, death)
            cnt += 1
            if cnt > 52000:
                break
        # street trees and park trees later (1800+)
        for _ in range(500):
            x = R.uniform(-90, 230)
            z = R.uniform(-1650, -1300)
            add("tree", (x, self.height_at(x, z, 1900), z), (8, 10, 8), 0, (0.25, 0.42, 0.2), (0.35, 0.25, 0.16),
                1790 + R.uniform(0, 60))
            if R.random() < 0.3:
                pass

        # Lenape villages
        for (cx, cz), n in (((650, -2180), 9), ((-330, -3600), 7), ((1300, -3300), 6), ((1450, 250), 5)):
            for k in range(n):
                a = R.uniform(0, 6.28)
                r = R.uniform(10, 90)
                x, z = cx + math.cos(a) * r, cz + math.sin(a) * r
                add("longhouse", (x, self.height_at(x, z, 1600), z), (7, 6, R.uniform(18, 30)), R.uniform(0, 3.14),
                    (0.48, 0.38, 0.27), (0.40, 0.31, 0.22), -INF, 1640 + R.uniform(0, 25))
        canoe_routes = [((-500, -800), (-700, -2600)), ((900, -900), (1200, -2000)), ((300, 500), (900, 150)),
                        ((-600, 400), (-1100, -600)), ((1500, -2600), (1250, -1800))]
        for (a, b) in canoe_routes:
            for k in range(2):
                add("canoe", (a[0] + k * 12, 0.0, a[1]), (1.3, 0.8, 8), math.atan2(b[0] - a[0], b[1] - a[1]),
                    (0.45, 0.32, 0.2), (0.45, 0.32, 0.2), -INF, 1655 + R.uniform(0, 10),
                    move=(b[0] - a[0], b[1] - a[1], 1600.0, 1609.6))

        # windmills
        for (x, z), b, d in (((-215, -270), 1626, 1700), ((-180, -980), 1662, 1760), ((520, -1960), 1680, 1790),
                             ((1500, -600), 1700, 1840), ((-1550, -700), 1690, 1830), ((1700, -2600), 1720, 1840)):
            add("windmill", (x, self.height_at(x, z, 1700), z), (9, 18, 9), R.uniform(0, 6.28), (0.92, 0.9, 0.85),
                (0.35, 0.28, 0.24), b, d)

        # palisade wall 1653-1699 (Wall Street)
        x = -240
        while x < 610:
            z = -650 - (x + 240) / 850 * 30
            if self.land_ok(x, z, 1653):
                add("palisade", (x, self.height_at(x, z, 1653), z), (0.7, 4.5, 0.7), 0, (0.42, 0.32, 0.22),
                    (0.36, 0.27, 0.19), 1653.25, 1699.5)
            x += 1.4

        # churches & landmarks
        add("church", (8, self.height_at(8, -100, 1650), -100), (12, 8, 20), 0.3, (0.88, 0.85, 0.78), (0.32, 0.28, 0.26), 1642, 1741.3)  # St Nicholas
        add("church", (-90, 4, -690), (16, 12, 32), math.pi / 2, (0.75, 0.7, 0.62), (0.3, 0.27, 0.25), 1698, 1776.72)
        add("church", (-90, 4, -690), (18, 14, 36), math.pi / 2, (0.72, 0.66, 0.56), (0.30, 0.27, 0.25), 1790,
            1839)
        add("church", (-90, 4, -690), (22, 18, 44), math.pi / 2, (0.62, 0.52, 0.44), (0.30, 0.28, 0.27), 1846)
        add("church", (-70, 4, -1100), (16, 12, 30), math.pi / 2, (0.85, 0.80, 0.70), (0.33, 0.30, 0.28), 1766)
        add("house", (330, 2, -330), (14, 16, 18), 0.6, (0.80, 0.55, 0.38), (0.36, 0.28, 0.24), 1653, 1699)  # Stadt Huys
        add("row", (110, 3, -670), (24, 16, 34), 0, (0.86, 0.80, 0.68), (0.4, 0.36, 0.33), 1700, 1812)  # Federal Hall
        add("row", (110, 3, -670), (26, 18, 40), 0, (0.88, 0.86, 0.80), (0.5, 0.48, 0.45), 1842)
        add("row", (80, 4, -1475), (50, 16, 22), 0, (0.93, 0.92, 0.88), (0.6, 0.58, 0.55), 1812)  # City Hall
        add("spire", (80, 20, -1475), (8, 14, 8), 0, (0.93, 0.92, 0.88), (0.85, 0.78, 0.45), 1812)
        add("row", (0, 2, -120), (40, 14, 28), 0, (0.93, 0.92, 0.88), (0.5, 0.48, 0.45), 1790.5, 1815)  # Govt House

        # piers along the East River and later the Hudson
        for k in range(60):
            z = -60 - k * 22
            x = self._shore_x_east(z, 1760)
            b = 1700 + max(0, (-z) / 1300 * 60) + R.uniform(0, 10)
            add("pier", (x + 14, 0.2, z), (8, 1.5, 30), -0.55, (0.45, 0.35, 0.25), (0.4, 0.3, 0.2), b, 1960)
        for k in range(40):
            z = -300 - k * 40
            x = -420 if z < -500 else -300
            add("pier", (x - 18, 0.2, z), (10, 1.5, 40), math.pi / 2, (0.45, 0.35, 0.25), (0.4, 0.3, 0.2),
                1790 + R.uniform(0, 30), 1990)

        self._ships()
        self._modern()

    def _shore_x_east(self, z, year):
        x = 0
        for xx in np.arange(-300, 2400, 10):
            if self.land_ok(xx, z, year):
                x = xx
        return x

    def _house(self, add, x, z, rot, w, d, birth, death, wd, wg, wf, roofs, R):
        y = self.height_at(x, z, birth + 1)
        if birth < 1700:
            add("house", (x, y, z), (w, R.uniform(7, 10), d), rot, R.choice(wd), R.choice(roofs), birth, death)
        elif birth < 1800:
            add("house", (x, y, z), (w + 1, R.uniform(9, 12), d), rot, R.choice(wg), R.choice(roofs[:3]), birth,
                death)
        else:
            add("row", (x, y, z), (w + 1, R.uniform(11, 16), d + 2), rot, R.choice(wf), (0.3, 0.27, 0.26), birth,
                death)

    # ---------------------------------------------------------------- ships
    def _ships(self):
        add, R = self.add, self.rng
        DUTCH = (0.95, 0.5, 0.1)
        BRIT = (0.8, 0.15, 0.15)
        US = (0.85, 0.85, 0.9)
        # Halve Maen 1609
        add("ship", (-700, 0, 2600), (6, 7, 22), math.pi, (0.36, 0.22, 0.14), DUTCH, 1609.69, 1609.76,
            move=(-200, -7600, 1609.70, 1609.74))
        # Dutch traders at anchor
        for k in range(10):
            b = 1625 + k * 4 + R.uniform(0, 3)
            add("ship", (R.uniform(-250, 500), 0, R.uniform(150, 650)), (6, 7, 24), R.uniform(0, 6.28),
                (0.36, 0.22, 0.14), DUTCH, b, min(b + 18, 1664.6))
        # English fleet Aug 1664
        for k in range(4):
            add("ship", (300 + k * 60, 0, 3000), (8, 9, 32), math.pi, (0.30, 0.18, 0.12), BRIT, 1664.58, 1666,
                move=(-200 + k * 110 - 300 - k * 60 + 300, -2350, 1664.60, 1664.67))
        # Dutch recapture 1673
        for k in range(10):
            add("ship", (-200 + k * 70, 0, 3200), (7, 8, 28), math.pi, (0.36, 0.22, 0.14), DUTCH, 1673.55, 1674.85,
                move=(R.uniform(-100, 100), -2500 + R.uniform(-200, 200), 1673.58, 1673.62))
        # merchants 1680-1850, mostly in the East River
        for k in range(260):
            b = R.uniform(1680, 1860)
            zz = R.uniform(-1300, 300)
            east = R.random() < 0.7
            if east:
                x = self._shore_x_east(zz, b) + R.uniform(40, 220)
            else:
                x = R.uniform(-900, -450)
            flag = DUTCH if b < 1664 else (BRIT if b < 1783 else US)
            if 1776.5 < b < 1783.9:
                flag = BRIT
            add("ship", (x, 0, zz), (6, 7, R.uniform(20, 30)), R.uniform(0, 6.28), (0.34, 0.22, 0.14), flag, b,
                b + R.uniform(6, 14))
        # British fleet 1776
        for k in range(140):
            x = R.uniform(-1300, 900)
            z = R.uniform(500, 3000) if R.random() < 0.7 else R.uniform(-3000, 0)
            if z < 0:
                x = R.uniform(-1300, -500)
            add("ship", (x, 0, 3600 + R.uniform(0, 800)), (8, 9, 32), math.pi, (0.30, 0.18, 0.12), BRIT, 1776.48,
                1783.9, move=(0, z - 3600, 1776.50, 1776.57))
        # steamers & ferries after 1810
        for k in range(30):
            b = R.uniform(1812, 1900)
            if R.random() < 0.5:
                a, c = (R.uniform(300, 900), R.uniform(-1500, 200)), None
                add("steamer", (a[0], 0, a[1]), (7, 7, 30), 0.0, (0.15, 0.15, 0.17), (0.85, 0.2, 0.15), b, b + 40,
                    move=(900, R.uniform(-300, 300), b, b + 1.5))
            else:
                add("steamer", (-1300, 0, R.uniform(-2000, 0)), (7, 7, 30), math.pi / 2, (0.15, 0.15, 0.17),
                    (0.85, 0.2, 0.15), b, b + 40, move=(950, R.uniform(-200, 200), b, b + 1.5))

    # ---------------------------------------------------------------- modern skyline
    def _modern(self):
        add, R = self.add, self.rng
        pts = []
        for _ in range(9000):
            x = R.uniform(-560, 2200)
            z = R.uniform(-8900, 150)
            if not self.land_ok(x, z, 2026) or self.road_at(x, z):
                continue
            if any((x - a) ** 2 + (z - b) ** 2 < r * r for (a, b), r in
                   (((80, -1475), 200), ((40, -230), 40), ((420, -2100), 50), ((-90, -690), 35))):
                continue
            if any((x - a) ** 2 + (z - b) ** 2 < 32 ** 2 for a, b in pts):
                continue
            pts.append((x, z))
            if len(pts) > 2600:
                break
        for x, z in pts:
            fidi = z > -1700
            mid = -7600 < z < -5400
            if fidi:
                h = R.lognormvariate(math.log(120), 0.55)
            elif mid:
                h = R.lognormvariate(math.log(140), 0.55)
            else:
                h = R.lognormvariate(math.log(45), 0.5)
            h = min(h, 380)
            b = 1890 + min(125, h / 3.2) + R.uniform(-15, 25)
            w = R.uniform(24, 40)
            glass = h > 120 and R.random() < 0.7
            col = (0.55, 0.62, 0.70) if glass else R.choice([(0.72, 0.66, 0.58), (0.62, 0.55, 0.48),
                                                             (0.80, 0.78, 0.74), (0.55, 0.45, 0.40)])
            add("tower", (x, self.height_at(x, z, 2026), z), (w, h, w * R.uniform(0.8, 1.6)), R.choice([0, 0.02]),
                col, (0.35, 0.36, 0.38), min(b, 2024), INF)
        # landmarks
        add("tower", (-230, 3, -1250), (55, 417, 55), math.pi / 4, (0.55, 0.65, 0.75), (0.7, 0.75, 0.8), 2012)  # 1 WTC
        add("spire", (-230, 420, -1250), (4, 124, 4), 0, (0.8, 0.8, 0.82), (0.8, 0.8, 0.82), 2013)
        add("tower", (60, 3, -1350), (45, 200, 45), 0, (0.85, 0.82, 0.74), (0.4, 0.55, 0.45), 1912)  # Woolworth
        add("spire", (60, 203, -1350), (30, 40, 30), 0, (0.4, 0.55, 0.45), (0.4, 0.55, 0.45), 1913)
        add("tower", (900, 3, -5900), (70, 381, 55), 0, (0.78, 0.74, 0.66), (0.78, 0.74, 0.66), 1931)  # ESB
        add("spire", (900, 384, -5900), (8, 62, 8), 0, (0.8, 0.8, 0.82), (0.8, 0.8, 0.82), 1931)
        add("tower", (1450, 3, -6450), (50, 240, 50), 0, (0.78, 0.76, 0.72), (0.78, 0.76, 0.72), 1930)  # Chrysler
        add("spire", (1450, 243, -6450), (26, 80, 26), 0, (0.85, 0.85, 0.88), (0.85, 0.85, 0.88), 1930)
        add("special", (0, 0, 0), (1, 1, 1), 0, (0.62, 0.55, 0.47), (0.35, 0.3, 0.28), 1870, INF, mesh="brooklyn")
        add("special", (-1150, 2, 1500), (1, 1, 1), 0, (0.45, 0.68, 0.6), (0.7, 0.65, 0.55), 1886, INF,
            mesh="liberty")
        add("special", (0, self.height_at(0, -120, 1625) - 0.5, -120), (1, 1, 1), 0, (0.62, 0.55, 0.42),
            (0.40, 0.48, 0.30), 1624.8, 1790.4,
            mesh="fort")
        add("special", (0, 0, 0), (1, 1, 1), 0, (0.10, 0.45, 0.58), (0.45, 0.40, 0.32), 1646, 1676, mesh="canal")
        add("special", (-130, 0, 70), (1, 1, 1), 0, (0.62, 0.5, 0.42), (0.5, 0.42, 0.36), 1811, INF, mesh="clinton")


if __name__ == "__main__":
    import time
    t = time.time()
    w = World()
    print("built in", round(time.time() - t, 1), "s")
    for k, v in w.I.items():
        print(k, len(v))
