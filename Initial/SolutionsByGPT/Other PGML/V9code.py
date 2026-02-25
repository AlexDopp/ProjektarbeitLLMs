# cornell_raytracer.py
# Minimaler, verständlicher Raytracer (Cornell Box)
# Nur Standardbibliothek, keine externen Abhängigkeiten

import math

# ============================================================
# Mathematik
# ============================================================

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z

    def __add__(self, o): return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)
    def __sub__(self, o): return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)
    def __mul__(self, k): return Vec3(self.x * k, self.y * k, self.z * k)
    def dot(self, o): return self.x * o.x + self.y * o.y + self.z * o.z

    def norm(self):
        l = math.sqrt(self.dot(self))
        return self * (1.0 / l) if l != 0 else self

    def reflect(self, n):
        return self - n * (2 * self.dot(n))

# ============================================================
# Ray
# ============================================================

class Ray:
    def __init__(self, origin, direction):
        self.o = origin
        self.d = direction.norm()

# ============================================================
# Materialien
# ============================================================

class Material:
    def __init__(self, color, reflection=0.0):
        self.color = color
        self.reflection = reflection

# ============================================================
# Geometrie
# ============================================================

class Sphere:
    def __init__(self, center, radius, material):
        self.c = center
        self.r = radius
        self.m = material

    def intersect(self, ray):
        oc = ray.o - self.c
        a = ray.d.dot(ray.d)
        b = 2 * oc.dot(ray.d)
        c = oc.dot(oc) - self.r * self.r
        disc = b * b - 4 * a * c
        if disc < 0:
            return None
        t = (-b - math.sqrt(disc)) / (2 * a)
        if t > 1e-4:
            p = ray.o + ray.d * t
            n = (p - self.c).norm()
            return t, p, n, self.m
        return None

class Plane:
    def __init__(self, point, normal, material):
        self.p = point
        self.n = normal.norm()
        self.m = material

    def intersect(self, ray):
        denom = self.n.dot(ray.d)
        if abs(denom) < 1e-6:
            return None
        t = (self.p - ray.o).dot(self.n) / denom
        if t > 1e-4:
            p = ray.o + ray.d * t
            return t, p, self.n, self.m
        return None

# ============================================================
# Licht
# ============================================================

class Light:
    def __init__(self, position, intensity):
        self.p = position
        self.i = intensity

# ============================================================
# Szene
# ============================================================

class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []

# ============================================================
# Raytracer
# ============================================================

MAX_DEPTH = 3
BACKGROUND = Vec3(0, 0, 0)

def trace(ray, scene, depth):
    if depth <= 0:
        return BACKGROUND

    hit = None
    for obj in scene.objects:
        h = obj.intersect(ray)
        if h and (hit is None or h[0] < hit[0]):
            hit = h

    if hit is None:
        return BACKGROUND

    _, p, n, mat = hit
    color = Vec3(0, 0, 0)

    # Diffuses Licht + Schatten
    for light in scene.lights:
        ldir = (light.p - p).norm()
        shadow_ray = Ray(p + n * 1e-4, ldir)

        in_shadow = False
        for obj in scene.objects:
            if obj.intersect(shadow_ray):
                in_shadow = True
                break

        if not in_shadow:
            intensity = max(0, n.dot(ldir)) * light.i
            color += mat.color * intensity

    # Reflexion
    if mat.reflection > 0:
        rdir = ray.d.reflect(n)
        rcol = trace(Ray(p + n * 1e-4, rdir), scene, depth - 1)
        color = color * (1 - mat.reflection) + rcol * mat.reflection

    return color

# ============================================================
# Rendering
# ============================================================

def render(scene, w, h, filename):
    camera = Vec3(0, 0, -3)
    fov = math.pi / 3

    with open(filename, "w") as f:
        f.write(f"P3\n{w} {h}\n255\n")
        for y in range(h):
            for x in range(w):
                px = (2 * (x + 0.5) / w - 1) * math.tan(fov / 2) * w / h
                py = -(2 * (y + 0.5) / h - 1) * math.tan(fov / 2)
                ray = Ray(camera, Vec3(px, py, 1))
                col = trace(ray, scene, MAX_DEPTH)

                r = min(255, int(col.x * 255))
                g = min(255, int(col.y * 255))
                b = min(255, int(col.z * 255))
                f.write(f"{r} {g} {b} ")

# ============================================================
# Cornell Box Szene
# ============================================================

def cornell_box():
    scene = Scene()

    red   = Material(Vec3(1, 0.2, 0.2))
    green = Material(Vec3(0.2, 1, 0.2))
    white = Material(Vec3(0.9, 0.9, 0.9))
    mirror = Material(Vec3(1, 1, 1), reflection=0.7)

    # Wände
    scene.objects += [
        Plane(Vec3(-1, 0, 0), Vec3(1, 0, 0), red),
        Plane(Vec3(1, 0, 0), Vec3(-1, 0, 0), green),
        Plane(Vec3(0, -1, 0), Vec3(0, 1, 0), white),
        Plane(Vec3(0, 1, 0), Vec3(0, -1, 0), white),
        Plane(Vec3(0, 0, 3), Vec3(0, 0, -1), white),
    ]

    # Kugeln
    scene.objects += [
        Sphere(Vec3(-0.4, -0.6, 1.2), 0.4, mirror),
        Sphere(Vec3(0.5, -0.7, 2), 0.3, white),
    ]

    # Licht
    scene.lights.append(Light(Vec3(0, 0.9, 1.5), 1.5))

    return scene

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    scene = cornell_box()
    #changed "cornell_box.ppm" to "V9Box.ppm" to simplyfy and avoid confusion with previous versions
    render(scene, 320, 240, "V9Box.ppm")
    print("Rendering abgeschlossen: cornell_box.ppm")
