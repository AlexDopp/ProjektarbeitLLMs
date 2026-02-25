import math

# =========================
# Mathematische Grundlagen
# =========================

class Vec3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __add__(self, o):
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, k):
        return Vec3(self.x * k, self.y * k, self.z * k)

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    def length(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        l = self.length()
        return self if l == 0 else self * (1.0 / l)

    def reflect(self, normal):
        return self - normal * (2 * self.dot(normal))


# =========================
# Ray & Material
# =========================

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalize()


class Material:
    def __init__(self, color, reflection=0.0):
        self.color = color
        self.reflection = reflection


# =========================
# Geometrische Objekte
# =========================

class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        disc = b * b - 4 * a * c
        if disc < 0:
            return None
        t = (-b - math.sqrt(disc)) / (2 * a)
        if t > 0.001:
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
        if t > 0.001:
            hit = ray.origin + ray.direction * t
            return t, hit, self.normal, self.material
        return None


# =========================
# Szene & Licht
# =========================

class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity


# =========================
# Raytracer
# =========================

class RayTracer:
    def __init__(self, objects, light):
        self.objects = objects
        self.light = light
        self.max_depth = 3

    def trace(self, ray, depth):
        if depth <= 0:
            return Vec3(0, 0, 0)

        hit_data = None
        min_t = float("inf")

        for obj in self.objects:
            hit = obj.intersect(ray)
            if hit and hit[0] < min_t:
                min_t = hit[0]
                hit_data = hit

        if not hit_data:
            return Vec3(0, 0, 0)

        _, hit_point, normal, material = hit_data

        # Schatten
        light_dir = (self.light.position - hit_point).normalize()
        shadow_ray = Ray(hit_point + normal * 0.001, light_dir)
        in_shadow = False

        for obj in self.objects:
            if obj.intersect(shadow_ray):
                in_shadow = True
                break

        # Diffuse + Specular
        color = material.color * 0.1  # Ambient

        if not in_shadow:
            diff = max(normal.dot(light_dir), 0)
            color += material.color * diff

            view_dir = (ray.origin - hit_point).normalize()
            reflect_dir = light_dir.reflect(normal)
            spec = pow(max(view_dir.dot(reflect_dir), 0), 32)
            color += Vec3(1, 1, 1) * spec * 0.5

        # Reflexion
        if material.reflection > 0:
            reflect_dir = ray.direction.reflect(normal)
            reflect_ray = Ray(hit_point + normal * 0.001, reflect_dir)
            reflect_color = self.trace(reflect_ray, depth - 1)
            color = color * (1 - material.reflection) + reflect_color * material.reflection

        return color


# =========================
# Bildgenerierung (PPM)
# =========================

def clamp(x):
    return max(0, min(255, int(x * 255)))


def render():
    width, height = 400, 400
    camera = Vec3(0, 0, -3)

    # Materialien
    white = Material(Vec3(1, 1, 1))
    red = Material(Vec3(1, 0.2, 0.2))
    green = Material(Vec3(0.2, 1, 0.2))
    mirror = Material(Vec3(1, 1, 1), reflection=0.6)

    # Szene (Cornell Box)
    objects = [
        Plane(Vec3(0, -1, 0), Vec3(0, 1, 0), white),     # Boden
        Plane(Vec3(0, 1, 0), Vec3(0, -1, 0), white),     # Decke
        Plane(Vec3(-1, 0, 0), Vec3(1, 0, 0), red),       # Links
        Plane(Vec3(1, 0, 0), Vec3(-1, 0, 0), green),     # Rechts
        Plane(Vec3(0, 0, 2), Vec3(0, 0, -1), white),     # Rückwand
        Sphere(Vec3(-0.4, -0.6, 1), 0.4, mirror),
        Sphere(Vec3(0.4, -0.6, 0.7), 0.4, white),
    ]

    light = Light(Vec3(0, 0.9, 1), 1.5)
    tracer = RayTracer(objects, light)

    # changed name to "V7Box.ppm" to simplyfy and avoid confusion with previous versions
    with open("V7Box.ppm", "w") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for y in range(height):
            for x in range(width):
                u = (x / width) * 2 - 1
                v = (y / height) * 2 - 1
                ray = Ray(camera, Vec3(u, -v, 1))
                col = tracer.trace(ray, tracer.max_depth)
                f.write(f"{clamp(col.x)} {clamp(col.y)} {clamp(col.z)} ")
            f.write("\n")


if __name__ == "__main__":
    render()
