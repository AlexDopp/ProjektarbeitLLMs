import math

# =========================
# Math / Utility
# =========================

class Vec3:
    __slots__ = ("x", "y", "z")

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

    __rmul__ = __mul__

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    def norm(self):
        return math.sqrt(self.dot(self))

    def normalized(self):
        n = self.norm()
        return self if n == 0 else self * (1.0 / n)

    def reflect(self, n):
        return self - n * (2.0 * self.dot(n))


def clamp(x):
    return max(0.0, min(1.0, x))


# =========================
# Ray / Material
# =========================

class Ray:
    __slots__ = ("origin", "direction")

    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalized()


class Material:
    __slots__ = ("color", "diffuse", "specular", "reflection")

    def __init__(self, color, diffuse=0.8, specular=0.2, reflection=0.0):
        self.color = color
        self.diffuse = diffuse
        self.specular = specular
        self.reflection = reflection


# =========================
# Geometry
# =========================

class Hit:
    __slots__ = ("t", "point", "normal", "material")

    def __init__(self, t, point, normal, material):
        self.t = t
        self.point = point
        self.normal = normal
        self.material = material


class Sphere:
    __slots__ = ("center", "radius", "material")

    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        d = b * b - 4 * a * c
        if d < 0:
            return None
        s = math.sqrt(d)
        t = (-b - s) / (2 * a)
        if t < 1e-4:
            t = (-b + s) / (2 * a)
            if t < 1e-4:
                return None
        p = ray.origin + ray.direction * t
        n = (p - self.center).normalized()
        return Hit(t, p, n, self.material)


class Plane:
    __slots__ = ("point", "normal", "material")

    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalized()
        self.material = material

    def intersect(self, ray):
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-6:
            return None
        t = (self.point - ray.origin).dot(self.normal) / denom
        if t < 1e-4:
            return None
        p = ray.origin + ray.direction * t
        return Hit(t, p, self.normal, self.material)


# =========================
# Light
# =========================

class Light:
    __slots__ = ("position", "intensity")

    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity


# =========================
# Scene
# =========================

class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []

    def intersect(self, ray):
        closest = None
        for obj in self.objects:
            hit = obj.intersect(ray)
            if hit and (closest is None or hit.t < closest.t):
                closest = hit
        return closest


# =========================
# Raytracer
# =========================

class RayTracer:
    def __init__(self, scene, max_depth=3, ambient_intensity=0.1):
        self.scene = scene
        self.max_depth = max_depth
        self.ambient_intensity = ambient_intensity

    def trace(self, ray, depth):
        if depth <= 0:
            return Vec3(0, 0, 0)

        hit = self.scene.intersect(ray)
        if not hit:
            return Vec3(0, 0, 0)

        color = Vec3(0, 0, 0)

        color += hit.material.color * self.ambient_intensity  

        for light in self.scene.lights:
            to_light = (light.position - hit.point).normalized()

            shadow_ray = Ray(hit.point + hit.normal * 1e-4, to_light)
            shadow_hit = self.scene.intersect(shadow_ray)
            if shadow_hit:
                continue 

            diff = max(0.0, hit.normal.dot(to_light))

            view = (-ray.direction).normalized()
            half = (to_light + view).normalized()
            spec = max(0.0, hit.normal.dot(half)) ** 32

            color += hit.material.color * (
                hit.material.diffuse * diff * light.intensity
            )
            color += Vec3(1, 1, 1) * (
                hit.material.specular * spec * light.intensity
            )

        if hit.material.reflection > 0:
            refl_dir = ray.direction.reflect(hit.normal)
            refl_ray = Ray(hit.point + hit.normal * 1e-4, refl_dir)
            refl_col = self.trace(refl_ray, depth - 1)
            color = color * (1 - hit.material.reflection) + \
                    refl_col * hit.material.reflection

        return color



# =========================
# Rendering
# =========================

def render():
    width, height = 400, 400
    fov = math.pi / 3.0

    scene = Scene()

    red   = Material(Vec3(0.75, 0.1, 0.1))
    green = Material(Vec3(0.1, 0.75, 0.1))
    white = Material(Vec3(0.75, 0.75, 0.75))
    mirror = Material(Vec3(1, 1, 1), diffuse=0.2, specular=0.3, reflection=0.6)

    # Cornell Box (6 planes)
    scene.objects += [
        Plane(Vec3(0, -1, 0), Vec3(0, 1, 0), white),   # floor
        Plane(Vec3(0, 1, 0), Vec3(0, -1, 0), white),   # ceiling
        Plane(Vec3(-1, 0, 0), Vec3(1, 0, 0), red),     # left
        Plane(Vec3(1, 0, 0), Vec3(-1, 0, 0), green),   # right
        Plane(Vec3(0, 0, -3), Vec3(0, 0, 1), white),   # back
    ]

    # Objects
    scene.objects += [
        Sphere(Vec3(-0.4, -0.6, -1.5), 0.4, mirror),
        Sphere(Vec3(0.4, -0.7, -2.0), 0.3, red),
    ]

    scene.lights.append(Light(Vec3(0, 0.9, -1.5), 5.0))

    tracer = RayTracer(scene)

    pixels = []

    for y in range(height):
        for x in range(width):
            px = (2 * (x + 0.5) / width - 1) * math.tan(fov / 2)
            py = (1 - 2 * (y + 0.5) / height) * math.tan(fov / 2)
            ray = Ray(Vec3(0, 0, 1), Vec3(px, py, -1))
            col = tracer.trace(ray, tracer.max_depth)
            pixels.append((
                int(255 * clamp(col.x)),
                int(255 * clamp(col.y)),
                int(255 * clamp(col.z)),
            ))

    #Changed "cornell_box.ppm" to "V2Box.ppm"
    with open("V2Box.ppm", "w") as f:
        f.write("P3\n{} {}\n255\n".format(width, height))
        for r, g, b in pixels:
            f.write(f"{r} {g} {b}\n")


if __name__ == "__main__":
    render()
