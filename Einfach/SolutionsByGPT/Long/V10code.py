import math
import struct
import zlib


# =========================
# Math & Core Structures
# =========================

class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, o):
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, k):
        return Vec3(self.x * k, self.y * k, self.z * k)

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    def norm(self):
        l = math.sqrt(self.dot(self))
        return self * (1.0 / l) if l > 0 else self

    def reflect(self, n):
        return self - n * (2.0 * self.dot(n))


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.dir = direction.norm()


# =========================
# Materials & Geometry
# =========================

class Material:
    def __init__(self, color, reflect=0.0):
        self.color = color
        self.reflect = reflect


class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.mat = material

    def intersect(self, ray):
        oc = ray.origin - self.center
        a = ray.dir.dot(ray.dir)
        b = 2.0 * oc.dot(ray.dir)
        c = oc.dot(oc) - self.radius * self.radius
        d = b * b - 4 * a * c
        if d < 0:
            return None
        s = math.sqrt(d)
        t = (-b - s) / (2 * a)
        if t > 1e-4:
            p = ray.origin + ray.dir * t
            n = (p - self.center).norm()
            return t, p, n, self.mat
        return None


class Plane:
    def __init__(self, point, normal, material):
        self.p = point
        self.n = normal.norm()
        self.mat = material

    def intersect(self, ray):
        d = self.n.dot(ray.dir)
        if abs(d) < 1e-6:
            return None
        t = (self.p - ray.origin).dot(self.n) / d
        if t > 1e-4:
            p = ray.origin + ray.dir * t
            return t, p, self.n, self.mat
        return None


# =========================
# Scene Setup
# =========================

class Light:
    def __init__(self, pos, intensity):
        self.pos = pos
        self.int = intensity


class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []


# =========================
# Raytracer
# =========================

def trace(ray, scene, depth):
    if depth <= 0:
        return Vec3()

    hit = None
    for o in scene.objects:
        h = o.intersect(ray)
        if h and (hit is None or h[0] < hit[0]):
            hit = h

    if hit is None:
        return Vec3()

    _, p, n, mat = hit
    col = Vec3()

    for light in scene.lights:
        ldir = (light.pos - p).norm()
        shadow = False
        shadow_ray = Ray(p + n * 1e-4, ldir)
        for o in scene.objects:
            if o.intersect(shadow_ray):
                shadow = True
                break
        if not shadow:
            diff = max(n.dot(ldir), 0.0)
            col += mat.color * diff * light.int

    if mat.reflect > 0:
        rdir = ray.dir.reflect(n)
        rcol = trace(Ray(p + n * 1e-4, rdir), scene, depth - 1)
        col = col * (1 - mat.reflect) + rcol * mat.reflect

    return col


# =========================
# PNG Writer
# =========================

def write_png(filename, w, h, pixels):
    def chunk(tag, data):
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data))

    raw = b""
    for y in range(h):
        raw += b"\x00"
        for x in range(w):
            c = pixels[y * w + x]
            raw += bytes((
                max(0, min(255, int(c.x * 255))),
                max(0, min(255, int(c.y * 255))),
                max(0, min(255, int(c.z * 255))),
            ))

    with open(filename, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack("!2I5B", w, h, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))


# =========================
# Main
# =========================

def main():
    W = H = 512
    scene = Scene()

    # Materials
    red = Material(Vec3(0.75, 0.1, 0.1))
    green = Material(Vec3(0.1, 0.75, 0.1))
    white = Material(Vec3(0.75, 0.75, 0.75))
    mirror = Material(Vec3(0.9, 0.9, 0.9), reflect=0.5)

    # Cornell box
    scene.objects += [
        Plane(Vec3(-1, 0, 0), Vec3(1, 0, 0), red),
        Plane(Vec3(1, 0, 0), Vec3(-1, 0, 0), green),
        Plane(Vec3(0, -1, 0), Vec3(0, 1, 0), white),
        Plane(Vec3(0, 1, 0), Vec3(0, -1, 0), white),
        Plane(Vec3(0, 0, -2), Vec3(0, 0, 1), white),
        Sphere(Vec3(0.3, -0.6, -1.2), 0.4, mirror)
    ]

    scene.lights.append(Light(Vec3(0, 0.8, -1), 1.5))

    cam = Vec3(0, 0, 1)
    pixels = []

    for y in range(H):
        for x in range(W):
            u = (x / W - 0.5) * 2
            v = (0.5 - y / H) * 2
            ray = Ray(cam, Vec3(u, v, -1))
            pixels.append(trace(ray, scene, 3))

    # Changed "cornellbox.png" to "V10Box.png" to simplyfy and avoid confusion with previous versions
    write_png("V10Box.png", W, H, pixels)


if __name__ == "__main__":
    main()
