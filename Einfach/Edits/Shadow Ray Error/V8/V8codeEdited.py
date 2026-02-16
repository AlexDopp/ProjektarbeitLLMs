import math

# ============================================================
# Math / Vector Module
# ============================================================

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z

    def __add__(self, o): return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)
    def __mul__(self, k): return Vec3(self.x*k, self.y*k, self.z*k)
    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
    def length(self): return math.sqrt(self.dot(self))
    def normalize(self):
        l = self.length()
        return self * (1.0/l) if l > 0 else Vec3()

    def reflect(self, normal):
        return self - normal * 2 * self.dot(normal)

    def clamp(self):
        return Vec3(min(1,max(0,self.x)),
                    min(1,max(0,self.y)),
                    min(1,max(0,self.z)))

# ============================================================
# Ray + Material
# ============================================================

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.dir = direction.normalize()

class Material:
    def __init__(self, color, reflection=0.0):
        self.color = color
        self.reflection = reflection

# ============================================================
# Geometry Module
# ============================================================

class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        oc = ray.origin - self.center
        a = ray.dir.dot(ray.dir)
        b = 2 * oc.dot(ray.dir)
        c = oc.dot(oc) - self.radius*self.radius
        disc = b*b - 4*a*c
        if disc < 0: return None
        t = (-b - math.sqrt(disc)) / (2*a)
        if t > 0.001:
            hit = ray.origin + ray.dir*t
            normal = (hit - self.center).normalize()
            return t, hit, normal, self.material
        return None

class Plane:
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material

    def intersect(self, ray):
        denom = self.normal.dot(ray.dir)
        if abs(denom) < 1e-6: return None
        t = (self.point - ray.origin).dot(self.normal) / denom
        if t > 0.001:
            hit = ray.origin + ray.dir*t
            return t, hit, self.normal, self.material
        return None

# ============================================================
# Lighting
# ============================================================

class Light:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

# ============================================================
# Raytracer Core
# ============================================================

class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []

    def trace(self, ray):
        hit = None
        min_t = float("inf")
        for obj in self.objects:
            res = obj.intersect(ray)
            if res and res[0] < min_t:
                min_t = res[0]
                hit = res
        return hit

def shade(scene, ray, depth):
    if depth <= 0:
        return Vec3()

    hit = scene.trace(ray)
    if not hit:
        return Vec3()

    _, point, normal, mat = hit
    color = Vec3()

    for light in scene.lights:
        to_light = (light.pos - point).normalize()
        shadow_ray = Ray(point + normal*0.001, to_light)
        shadow_hit = scene.trace(shadow_ray)
        
        if shadow_hit:
            dist_to_light = (light.pos - point).length()
            if shadow_hit[0] < dist_to_light:
                continue
        
        # Diffuse
        diff = max(normal.dot(to_light), 0)
        color += mat.color * diff

        # Specular
        reflect_dir = to_light.reflect(normal)
        spec = max(ray.dir.dot(reflect_dir), 0) ** 32
        color += Vec3(1,1,1) * spec

    # Reflection
    if mat.reflection > 0:
        refl_dir = ray.dir.reflect(normal)
        refl_ray = Ray(point + normal*0.001, refl_dir)
        refl_color = shade(scene, refl_ray, depth-1)
        color = color*(1-mat.reflection) + refl_color*mat.reflection

    return color.clamp()

# ============================================================
# Render & Output
# ============================================================

def render():
    width, height = 400, 400
    camera = Vec3(0, 0, -3)
    scene = Scene()

    # Materials
    red   = Material(Vec3(1,0.2,0.2))
    green = Material(Vec3(0.2,1,0.2))
    white = Material(Vec3(0.9,0.9,0.9))
    mirror= Material(Vec3(1,1,1), reflection=0.6)

    # Cornell Box
    scene.objects += [
        Plane(Vec3(0,-1,0), Vec3(0,1,0), white),   # floor
        Plane(Vec3(0,1,0), Vec3(0,-1,0), white),   # ceiling
        Plane(Vec3(-1,0,0), Vec3(1,0,0), red),     # left
        Plane(Vec3(1,0,0), Vec3(-1,0,0), green),   # right
        Plane(Vec3(0,0,1), Vec3(0,0,-1), white),   # back
        Sphere(Vec3(-0.4,-0.5,0.3),0.5,mirror),
        Sphere(Vec3(0.5,-0.7,0.6),0.3,white)
    ]

    scene.lights.append(Light(Vec3(0,0.9,-0.5), Vec3(1,1,1)))

    #changed name to "V8Box.ppm" to simplyfy and avoid confusion with previous versions
    with open("V8Box.ppm", "w") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for y in range(height):
            for x in range(width):
                u = (x/width)*2 - 1
                v = (y/height)*2 - 1
                ray = Ray(camera, Vec3(u, -v, 1))
                col = shade(scene, ray, 3)
                r,g,b = int(col.x*255), int(col.y*255), int(col.z*255)
                f.write(f"{r} {g} {b} ")
            f.write("\n")

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    render()
    print("Rendering abgeschlossen: cornell.ppm")
