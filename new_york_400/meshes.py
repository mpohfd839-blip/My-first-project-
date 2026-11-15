"""Low-poly meshes. Each mesh: float32 array (N, 7) = position(3), normal(3), part(1); triangles, no index.
Unit meshes span x,z in [-0.5, 0.5] and y in [0, 1] (roofs/spires may go above 1).
Parts: 0 walls/main colour, 1 roof/secondary colour, 2 white (sails), 3 flag, 4 windmill blade, 5 trunk/dark."""
import math

import numpy as np


class MB:
    def __init__(self):
        self.v = []

    def tri(self, a, b, c, part):
        a, b, c = map(np.asarray, (a, b, c))
        n = np.cross(b - a, c - a)
        ln = np.linalg.norm(n)
        n = n / ln if ln > 0 else np.array([0, 1, 0])
        for p in (a, b, c):
            self.v.append([*p, *n, part])

    def quad(self, a, b, c, d, part):
        self.tri(a, b, c, part)
        self.tri(a, c, d, part)

    def box(self, x0, y0, z0, x1, y1, z1, part, top=True, bottom=False):
        P = lambda x, y, z: (x, y, z)
        self.quad(P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1), part)  # +z
        self.quad(P(x1, y0, z0), P(x0, y0, z0), P(x0, y1, z0), P(x1, y1, z0), part)  # -z
        self.quad(P(x1, y0, z1), P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), part)  # +x
        self.quad(P(x0, y0, z0), P(x0, y0, z1), P(x0, y1, z1), P(x0, y1, z0), part)  # -x
        if top:
            self.quad(P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0), part)
        if bottom:
            self.quad(P(x0, y0, z0), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1), part)

    def gable(self, x0, x1, y0, y1, z0, z1, part, ridge_z=True):
        """Pitched roof over a box footprint; ridge along z."""
        if ridge_z:
            xm = (x0 + x1) / 2
            self.quad((x0, y0, z1), (x0, y0, z0), (xm, y1, z0), (xm, y1, z1), part)
            self.quad((x1, y0, z0), (x1, y0, z1), (xm, y1, z1), (xm, y1, z0), part)
            self.tri((x0, y0, z1), (xm, y1, z1), (x1, y0, z1), part)
            self.tri((x1, y0, z0), (xm, y1, z0), (x0, y0, z0), part)
        else:
            zm = (z0 + z1) / 2
            self.quad((x1, y0, z1), (x0, y0, z1), (x0, y1, zm), (x1, y1, zm), part)
            self.quad((x0, y0, z0), (x1, y0, z0), (x1, y1, zm), (x0, y1, zm), part)
            self.tri((x1, y0, z1), (x1, y1, zm), (x1, y0, z0), part)
            self.tri((x0, y0, z0), (x0, y1, zm), (x0, y0, z1), part)

    def cyl(self, cx, cz, r0, r1, y0, y1, part, n=8, cap=True):
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            p00 = (cx + r0 * math.cos(a0), y0, cz + r0 * math.sin(a0))
            p01 = (cx + r0 * math.cos(a1), y0, cz + r0 * math.sin(a1))
            p10 = (cx + r1 * math.cos(a0), y1, cz + r1 * math.sin(a0))
            p11 = (cx + r1 * math.cos(a1), y1, cz + r1 * math.sin(a1))
            if r1 > 1e-6:
                self.quad(p01, p00, p10, p11, part)
            else:
                self.tri(p01, p00, (cx, y1, cz), part)
            if cap and r1 > 1e-6:
                self.tri((cx, y1, cz), p11, p10, part)

    def sphere(self, cx, cy, cz, r, part, n=6, m=4):
        for i in range(m):
            t0, t1 = math.pi * i / m, math.pi * (i + 1) / m
            for j in range(n):
                p0, p1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                P = lambda t, p: (cx + r * math.sin(t) * math.cos(p), cy + r * math.cos(t), cz + r * math.sin(t) * math.sin(p))
                a, b, c, d = P(t0, p0), P(t0, p1), P(t1, p1), P(t1, p0)
                if i == 0:
                    self.tri(a, c, d, part)
                elif i == m - 1:
                    self.tri(a, b, c, part)
                else:
                    self.quad(a, b, c, d, part)

    def arr(self):
        return np.asarray(self.v, np.float32)


def house():
    m = MB()
    m.box(-0.5, 0, -0.5, 0.5, 1, 0.5, 0, top=False)
    m.gable(-0.53, 0.53, 1.0, 1.55, -0.53, 0.53, 1, ridge_z=False)
    return m.arr()


def row():
    m = MB()
    m.box(-0.5, 0, -0.5, 0.5, 1, 0.5, 0, top=False)
    m.gable(-0.51, 0.51, 1.0, 1.14, -0.51, 0.51, 1, ridge_z=False)
    return m.arr()


def tower():
    m = MB()
    m.box(-0.5, 0, -0.5, 0.5, 1, 0.5, 0, top=False)
    m.box(-0.46, 1, -0.46, 0.46, 1.01, 0.46, 1)
    return m.arr()


def spire():
    m = MB()
    m.cyl(0, 0, 0.5, 0.0, 0, 1, 1, n=8)
    return m.arr()


def tree():
    m = MB()
    m.cyl(0, 0, 0.06, 0.05, 0, 0.35, 5, n=5, cap=False)
    m.sphere(0, 0.62, 0, 0.42, 0, n=7, m=4)
    return m.arr()


def pine():
    m = MB()
    m.cyl(0, 0, 0.06, 0.05, 0, 0.25, 5, n=5, cap=False)
    m.cyl(0, 0, 0.45, 0.0, 0.18, 0.8, 0, n=7)
    m.cyl(0, 0, 0.33, 0.0, 0.48, 1.05, 0, n=7)
    return m.arr()


def longhouse():
    m = MB()
    n = 6
    for i in range(n):
        a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
        x0, y0 = 0.5 * math.cos(a0), math.sin(a0)
        x1, y1 = 0.5 * math.cos(a1), math.sin(a1)
        m.quad((x0, y0, 0.5), (x1, y1, 0.5), (x1, y1, -0.5), (x0, y0, -0.5), 0)
        m.tri((0, 0, 0.5), (x1, y1, 0.5), (x0, y0, 0.5), 1)
        m.tri((0, 0, -0.5), (x0, y0, -0.5), (x1, y1, -0.5), 1)
    return m.arr()


def canoe():
    m = MB()
    m.box(-0.5, 0, -0.5, 0.5, 1, 0.5, 0)
    return m.arr()


def windmill():
    m = MB()
    m.cyl(0, 0, 0.5, 0.32, 0, 1.0, 0, n=8)
    m.cyl(0, 0, 0.36, 0.0, 1.0, 1.25, 1, n=8)
    for k in range(4):
        a = k * math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        hub = np.array([0, 1.02, 0.42])
        p = lambda r, w: hub + np.array([ca * r - sa * w, sa * r + ca * w, 0])
        m.quad(p(0.05, -0.06), p(0.95, -0.09), p(0.95, 0.09), p(0.05, 0.06), 4)
        m.quad(p(0.05, 0.06), p(0.95, 0.09), p(0.95, -0.09), p(0.05, -0.06), 4)
    return m.arr()


def church():
    m = MB()
    m.box(-0.5, 0, -0.5, 0.5, 1, 0.35, 0, top=False)
    m.gable(-0.53, 0.53, 1, 1.5, -0.53, 0.38, 1, ridge_z=True)
    m.box(-0.22, 0, 0.35, 0.22, 2.0, 0.75, 0)
    m.cyl(0, 0.55, 0.2, 0.0, 2.0, 3.6, 1, n=8)
    return m.arr()


def palisade():
    m = MB()
    m.box(-0.5, 0, -0.5, 0.5, 1, 0.5, 0)
    m.cyl(0, 0, 0.5, 0, 1, 1.25, 0, n=4)
    return m.arr()


def pier():
    m = MB()
    m.box(-0.5, -2, -0.5, 0.5, 1, 0.5, 0)
    return m.arr()


def ship():
    """Sailing ship, bow toward +z."""
    m = MB()
    hull = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.25), (0.0, 0.5), (-0.5, 0.25)]
    y0, y1 = -0.15, 0.25
    for (ax, az), (bx, bz) in zip(hull, hull[1:] + hull[:1]):
        m.quad((ax * 0.7, y0, az), (bx * 0.7, y0, bz), (bx, y1, bz), (ax, y1, az), 0)
    # deck
    m.tri((-0.5, y1, -0.5), (0.5, y1, -0.5), (0.5, y1, 0.25), 1)
    m.tri((-0.5, y1, -0.5), (0.5, y1, 0.25), (-0.5, y1, 0.25), 1)
    m.tri((-0.5, y1, 0.25), (0.5, y1, 0.25), (0.0, y1, 0.5), 1)
    m.box(-0.45, y1, -0.5, 0.45, y1 + 0.18, -0.3, 0)  # stern castle
    for mz, hgt in ((-0.25, 1.9), (0.05, 2.3), (0.32, 1.7)):
        m.box(-0.03, y1, mz - 0.015, 0.03, hgt, mz + 0.015, 5)
        for k, (s0, s1) in enumerate(((0.55, 1.05), (1.15, 1.6))):
            if s1 > hgt:
                continue
            wdt = 0.9 - 0.25 * k
            bulge = 0.05
            m.quad((-wdt / 2, s0, mz + 0.02), (wdt / 2, s0, mz + 0.02), (wdt / 2, s1, mz + 0.02 + bulge),
                   (-wdt / 2, s1, mz + 0.02 + bulge), 2)
            m.quad((wdt / 2, s0, mz + 0.0), (-wdt / 2, s0, mz + 0.0), (-wdt / 2, s1, mz + bulge),
                   (wdt / 2, s1, mz + bulge), 2)
    # flag at stern
    m.box(-0.01, y1 + 0.18, -0.48, 0.01, y1 + 0.9, -0.46, 5)
    m.quad((0, y1 + 0.7, -0.47), (0, y1 + 0.88, -0.47), (0, y1 + 0.88, -0.75), (0, y1 + 0.7, -0.75), 3)
    m.quad((0, y1 + 0.88, -0.47), (0, y1 + 0.7, -0.47), (0, y1 + 0.7, -0.75), (0, y1 + 0.88, -0.75), 3)
    return m.arr()


def steamer():
    m = MB()
    hull = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.3), (0.0, 0.5), (-0.5, 0.3)]
    y0, y1 = -0.15, 0.22
    for (ax, az), (bx, bz) in zip(hull, hull[1:] + hull[:1]):
        m.quad((ax * 0.8, y0, az), (bx * 0.8, y0, bz), (bx, y1, bz), (ax, y1, az), 0)
    m.box(-0.4, y1, -0.4, 0.4, y1 + 0.35, 0.25, 2)
    m.cyl(0, -0.05, 0.12, 0.12, y1 + 0.35, y1 + 1.1, 5, n=8)
    m.box(-0.62, 0.0, -0.12, 0.62, 0.45, 0.12, 1)
    return m.arr()


def fort():
    """Fort Amsterdam: four-bastioned fort ~ 90 m across, in world metres, centred at origin."""
    m = MB()
    pts = []
    s, b = 40.0, 22.0
    for k in range(4):
        a = k * math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        R = lambda x, z: (x * ca - z * sa, x * sa + z * ca)
        pts += [R(s, -s * 0.55), R(s, s * 0.55 - 6), R(s + b, s + b), R(s * 0.55 - 6, s)]
    inner = [(x * 0.82, z * 0.82) for x, z in pts]
    H = 7.0
    n = len(pts)
    for i in range(n):
        (ax, az), (bx, bz) = pts[i], pts[(i + 1) % n]
        (cx, cz), (dx, dz) = inner[i], inner[(i + 1) % n]
        m.quad((ax, 0, az), (bx, 0, bz), (bx, H, bz), (ax, H, az), 0)
        m.quad((bx, H, bz), (dx, H, dz), (cx, H, cz), (ax, H, az), 1)
        m.quad((dx, 0, dz), (cx, 0, cz), (cx, H, cz), (dx, H, dz), 0)
    # parade ground
    for i in range(n):
        (cx, cz), (dx, dz) = inner[i], inner[(i + 1) % n]
        m.tri((0, 0.4, 0), (dx, 0.4, dz), (cx, 0.4, cz), 1)
    # flagpole + flag
    m.box(-0.3, 0, 20, 0.3, 22, 20.6, 5)
    m.quad((0, 17, 20.3), (0, 21.5, 20.3), (0, 21.5, 29), (0, 17, 29), 3)
    m.quad((0, 21.5, 20.3), (0, 17, 20.3), (0, 17, 29), (0, 21.5, 29), 3)
    # governor's house inside
    m.box(-22, 0, -10, 8, 10, 6, 2, top=False)
    m.gable(-23, 9, 10, 15, -11, 7, 1, ridge_z=False)
    return m.arr()


def clinton():
    m = MB()
    m.cyl(0, 0, 28, 28, -6, 8, 0, n=24, cap=False)
    m.cyl(0, 0, 22, 22, -6, 8, 0, n=24, cap=False)
    for i in range(24):
        a0, a1 = 2 * math.pi * i / 24, 2 * math.pi * (i + 1) / 24
        m.quad((22 * math.cos(a0), 8, 22 * math.sin(a0)), (28 * math.cos(a0), 8, 28 * math.sin(a0)),
               (28 * math.cos(a1), 8, 28 * math.sin(a1)), (22 * math.cos(a1), 8, 22 * math.sin(a1)), 1)
    return m.arr()


def brooklyn_bridge():
    """Brooklyn Bridge in world metres from Manhattan (930,-1340) to Brooklyn (1720,-1020)."""
    m = MB()
    A = np.array([880.0, -1360.0])
    B = np.array([1760.0, -1000.0])
    d = B - A
    L = np.linalg.norm(d)
    u = d / L
    nrm = np.array([-u[1], u[0]])
    dy = 41.0
    P = lambda s, off, y: (A[0] + u[0] * s + nrm[0] * off, y, A[1] + u[1] * s + nrm[1] * off)
    # deck
    w = 13
    m.quad(P(0, -w, dy), P(0, w, dy), P(L, w, dy), P(L, -w, dy), 1)
    m.quad(P(0, w, dy - 3), P(0, -w, dy - 3), P(L, -w, dy - 3), P(L, w, dy - 3), 1)
    for side in (-w, w):
        m.quad(P(0, side, dy - 3), P(L, side, dy - 3), P(L, side, dy), P(0, side, dy), 1)
    # towers
    for s in (L * 0.27, L * 0.73):
        for side in (-14, 6):
            c = P(s, side, 0)
            m.box(c[0] - 6, -6, c[2] - 6, c[0] + 6, 84, c[2] + 6, 0)
        c = P(s, -4, 0)
        m.box(c[0] - 7, 60, c[2] - 7, c[0] + 7, 84, c[2] + 7, 0)
    # cables (catenary approximated)
    for side in (-11, 11):
        pts = []
        for i in range(41):
            s = L * i / 40
            if s < L * 0.27:
                y = dy + 2 + (84 - dy - 2) * (s / (L * 0.27)) ** 2
            elif s > L * 0.73:
                y = dy + 2 + (84 - dy - 2) * ((L - s) / (L * 0.27)) ** 2
            else:
                f = (s - L * 0.27) / (L * 0.46)
                y = 84 - (84 - dy - 4) * (1 - (2 * f - 1) ** 2)
            pts.append(P(s, side, y))
        for a, b in zip(pts, pts[1:]):
            a, b = np.array(a), np.array(b)
            o = np.array([0, 0.9, 0])
            m.quad(a, b, b + o, a + o, 2)
            m.quad(b, a, a + o, b + o, 2)
    return m.arr()


def liberty():
    m = MB()
    m.box(-14, 0, -14, 14, 6, 14, 1)  # star fort base (simplified)
    m.box(-8, 6, -8, 8, 27, 8, 1)  # pedestal
    m.cyl(0, 0, 4.5, 2.6, 27, 52, 0, n=8)  # robed figure
    m.sphere(0, 55, 0, 3.0, 0, n=6, m=4)
    m.cyl(0, 0, 3.2, 2.8, 56.5, 58.5, 0, n=8)  # crown
    m.box(1.5, 52, -1, 3, 66, 1, 0)  # raised arm
    m.cyl(2.3, 0, 1.6, 0.8, 66, 70, 2, n=6)  # torch flame (bright)
    return m.arr()


def canal():
    """Heere Gracht: a water strip with stone banks along Broad Street (world metres)."""
    m = MB()
    pts = [(310, -225), (265, -290), (230, -350), (200, -410), (170, -470)]
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, bz - az)
        nx, nz = -(bz - az) / L, (bx - ax) / L
        for w0, w1, y, part in ((-9, 9, 1.2, 0), (-12, -9, 2.2, 1), (9, 12, 2.2, 1)):
            a0 = (ax + nx * w0, y, az + nz * w0)
            a1 = (ax + nx * w1, y, az + nz * w1)
            b1 = (bx + nx * w1, y, bz + nz * w1)
            b0 = (bx + nx * w0, y, bz + nz * w0)
            m.quad(a0, b0, b1, a1, part)
            m.quad(a1, b1, b0, a0, part)
    return m.arr()


MESHES = dict(canal=canal, house=house, row=row, tower=tower, spire=spire, tree=tree, pine=pine, longhouse=longhouse,
              canoe=canoe, windmill=windmill, church=church, palisade=palisade, pier=pier, ship=ship,
              steamer=steamer, fort=fort, clinton=clinton, brooklyn=brooklyn_bridge, liberty=liberty)
