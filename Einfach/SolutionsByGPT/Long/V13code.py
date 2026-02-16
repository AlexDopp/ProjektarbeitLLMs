# ============================================================
# Einfacher Raytracer – Cornellbox (PPM-Ausgabe, 512x512)
# ============================================================

import math

# ------------------------------------------------------------
# Mathematik
# ------------------------------------------------------------

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z

    def __add__(self, o): return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)
    def __mul__(self, s): return Vec3(self.x*s, self.y*s, self.z*s)
    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z

    def length(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        l = self.length()
        return self * (1.0 / l) if l > 0 else self

    def clamp(self):
        return Vec3(
            min(1, max(0, self.x)),
            min(1, max(0, self.y)),
            min(1, max(0, self.z))
        )

# ------------------------------------------------------------
# Ray
# ------------------------------------------------------------

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalize()

# ------------------------------------------------------------
# Materialien & Licht
# ------------------------------------------------------------

class Material:
    def __init__(self, color, reflection=0.0):
        self.color = color
        self.reflection = reflection

class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity

# ------------------------------------------------------------
# Geometrie
# ------------------------------------------------------------

class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        oc = ray.origin - self.center
        b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius*self.radius
        disc = b*b - c
        if disc < 0:
            return None
        t = -b - math.sqrt(disc)
        if t > 1e-4:
            hit = ray.origin + ray.direction * t
            normal = (hit - self.center).normalize()
            return t, hit, normal, self.material
        return None

class Plane:
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material

    def intersect(self, ray):
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-6:
            return None
        t = (self.point - ray.origin).dot(self.normal) / denom
        if t > 1e-4:
            hit = ray.origin + ray.direction * t
            return t, hit, self.normal, self.material
        return None

# ------------------------------------------------------------
# Szene
# ------------------------------------------------------------

class Scene:
    def __init__(self):
        self.objects = []
        self.light = None

# ------------------------------------------------------------
# Raytracer
# ------------------------------------------------------------

class RayTracer:
    def __init__(self, scene, max_depth=2):
        self.scene = scene
        self.max_depth = max_depth

    def trace(self, ray, depth):
        if depth <= 0:
            return Vec3()

        hit_data = self.closest_hit(ray)
        if not hit_data:
            return Vec3()

        _, hit, normal, material = hit_data

        # Beleuchtung (Lambert)
        to_light = (self.scene.light.position - hit).normalize()
        shadow_ray = Ray(hit + normal * 1e-4, to_light)

        if self.closest_hit(shadow_ray):
            light_intensity = 0
        else:
            light_intensity = max(0, normal.dot(to_light))

        color = material.color * light_intensity

        # Reflexion
        if material.reflection > 0:
            r_dir = ray.direction - normal * 2 * ray.direction.dot(normal)
            r_ray = Ray(hit + normal * 1e-4, r_dir)
            reflected = self.trace(r_ray, depth - 1)
            color = color * (1 - material.reflection) + reflected * material.reflection

        return color

    def closest_hit(self, ray):
        closest = None
        min_t = float("inf")
        for obj in self.scene.objects:
            hit = obj.intersect(ray)
            if hit and hit[0] < min_t:
                min_t = hit[0]
                closest = hit
        return closest

# ------------------------------------------------------------
# Bildausgabe (PPM)
# ------------------------------------------------------------

def save_ppm(filename, pixels, w, h):
    with open(filename, "w") as f:
        f.write(f"P3\n{w} {h}\n255\n")
        for p in pixels:
            c = p.clamp()
            f.write(f"{int(c.x*255)} {int(c.y*255)} {int(c.z*255)}\n")

# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------

WIDTH = HEIGHT = 512
camera = Vec3(0, 0, -3)

scene = Scene()

# Materialien
red   = Material(Vec3(1, 0, 0))
green = Material(Vec3(0, 1, 0))
gray  = Material(Vec3(0.8, 0.8, 0.8))
mirror = Material(Vec3(1, 1, 1), reflection=0.6)

# Cornellbox-Wände
scene.objects += [
    Plane(Vec3(-1,0,0), Vec3(1,0,0), red),
    Plane(Vec3(1,0,0), Vec3(-1,0,0), green),
    Plane(Vec3(0,-1,0), Vec3(0,1,0), gray),
    Plane(Vec3(0,1,0), Vec3(0,-1,0), gray),
    Plane(Vec3(0,0,1), Vec3(0,0,-1), gray)
]

# Objekt
scene.objects.append(
    Sphere(Vec3(0, -0.5, 0.3), 0.3, mirror)
)

# Licht
scene.light = Light(Vec3(0, 0.9, -0.2), 1.0)

tracer = RayTracer(scene)

pixels = []

for y in range(HEIGHT):
    for x in range(WIDTH):
        u = (2*(x+0.5)/WIDTH - 1)
        v = (1 - 2*(y+0.5)/HEIGHT)
        ray = Ray(camera, Vec3(u, v, 1))
        color = tracer.trace(ray, tracer.max_depth)
        pixels.append(color)

#Changed "cornellbox.ppm" to "V13Box.ppm" to simplyfy and avoid confusion with previous versions
save_ppm("V13Box.ppm", pixels, WIDTH, HEIGHT)

print("Rendering abgeschlossen: cornellbox.ppm")
