import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
import struct

# ============================================================================
# Mathematik-Bibliothek
# ============================================================================

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        return math.sqrt(self.dot(self))
    
    def normalize(self):
        l = self.length()
        return self / l if l > 0 else self
    
    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3
    
    def point_at(self, t: float):
        return self.origin + self.direction * t

# ============================================================================
# Geometrie
# ============================================================================

@dataclass
class HitRecord:
    t: float
    point: Vec3
    normal: Vec3
    material: 'Material'
    front_face: bool

class Material:
    def __init__(self, color: Vec3, emission: Vec3 = None, reflectivity: float = 0.0):
        self.color = color
        self.emission = emission if emission else Vec3(0, 0, 0)
        self.reflectivity = reflectivity

class Sphere:
    def __init__(self, center: Vec3, radius: float, material: Material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return None
        
        sqrt_d = math.sqrt(discriminant)
        t = (-b - sqrt_d) / (2.0 * a)
        
        if t < t_min or t > t_max:
            t = (-b + sqrt_d) / (2.0 * a)
            if t < t_min or t > t_max:
                return None
        
        point = ray.point_at(t)
        normal = (point - self.center) / self.radius
        front_face = ray.direction.dot(normal) < 0
        normal = normal if front_face else normal * -1
        
        return HitRecord(t, point, normal, self.material, front_face)

class Plane:
    def __init__(self, point: Vec3, normal: Vec3, material: Material, size: float = 10.0):
        self.point = point
        self.normal = normal.normalize()
        self.material = material
        self.size = size
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        
        if abs(denom) < 1e-6:
            return None
        
        t = (self.point - ray.origin).dot(self.normal) / denom
        
        if t < t_min or t > t_max:
            return None
        
        point = ray.point_at(t)
        
        # Begrenzung der Ebene für die Wände
        if abs(self.normal.x) > 0.5:  # X-Wand
            if abs(point.y - self.point.y) > self.size or abs(point.z - self.point.z) > self.size:
                return None
        elif abs(self.normal.y) > 0.5:  # Y-Wand (Boden/Decke)
            if abs(point.x - self.point.x) > self.size or abs(point.z - self.point.z) > self.size:
                return None
        else:  # Z-Wand
            if abs(point.x - self.point.x) > self.size or abs(point.y - self.point.y) > self.size:
                return None
        
        front_face = ray.direction.dot(self.normal) < 0
        normal = self.normal if front_face else self.normal * -1
        
        return HitRecord(t, point, normal, self.material, front_face)

# ============================================================================
# Raytracer Core
# ============================================================================

class World:
    def __init__(self):
        self.objects = []
    
    def add(self, obj):
        self.objects.append(obj)
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[Tuple[HitRecord, object]]:
        closest_t = t_max
        closest_record = None
        closest_object = None
        
        for obj in self.objects:
            record = obj.hit(ray, t_min, closest_t)
            if record:
                closest_t = record.t
                closest_record = record
                closest_object = obj
        
        if closest_record:
            return closest_record, closest_object
        return None

class Camera:
    def __init__(self, look_from: Vec3, look_at: Vec3, v_up: Vec3, v_fov: float, aspect: float):
        self.aspect = aspect
        
        theta = v_fov * math.pi / 180.0
        h = math.tan(theta / 2.0)
        viewport_height = 2.0 * h
        viewport_width = aspect * viewport_height
        
        w = (look_from - look_at).normalize()
        u = v_up.cross(w).normalize()
        v = w.cross(u)
        
        self.origin = look_from
        self.horizontal = u * viewport_width
        self.vertical = v * viewport_height
        self.lower_left = self.origin - self.horizontal / 2 - self.vertical / 2 - w
    
    def get_ray(self, u: float, v: float) -> Ray:
        return Ray(self.origin, (self.lower_left + self.horizontal * u + self.vertical * v - self.origin).normalize())

class Raytracer:
    def __init__(self, world: World, camera: Camera, width: int, height: int, max_depth: int = 5):
        self.world = world
        self.camera = camera
        self.width = width
        self.height = height
        self.max_depth = max_depth
    
    def trace(self, ray: Ray, depth: int) -> Vec3:
        if depth <= 0:
            return Vec3(0, 0, 0)
        
        hit_result = self.world.hit(ray, 0.001, float('inf'))
        
        if not hit_result:
            return Vec3(0, 0, 0)  # Schwarzer Hintergrund
        
        record, obj = hit_result
        
        # Emission (Lichtquellen)
        emitted = record.material.emission
        
        # Reflexion
        if record.material.reflectivity > 0:
            reflected_dir = ray.direction - record.normal * (2 * ray.direction.dot(record.normal))
            reflected_ray = Ray(record.point, reflected_dir)
            reflected_color = self.trace(reflected_ray, depth - 1)
            return emitted + reflected_color * record.material.reflectivity
        
        # Diffuses Shading
        light_dir = (Vec3(0, 5, 0) - record.point).normalize()
        light_distance = (Vec3(0, 5, 0) - record.point).length()
        
        # Schatten
        shadow_ray = Ray(record.point + record.normal * 0.001, light_dir)
        shadow_hit = self.world.hit(shadow_ray, 0.001, light_distance)
        
        if shadow_hit:
            # Im Schatten - nur Emission
            return emitted
        
        # Lambert-Shading
        diffuse = max(0, record.normal.dot(light_dir))
        light_intensity = 5.0 / (light_distance * light_distance)
        
        color = record.material.color * (diffuse * light_intensity)
        
        return emitted + color
    
    def render(self) -> List[List[Vec3]]:
        image = [[Vec3(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        
        for j in range(self.height):
            for i in range(self.width):
                u = i / (self.width - 1)
                v = (self.height - j - 1) / (self.height - 1)  # Flip Y
                
                ray = self.camera.get_ray(u, v)
                color = self.trace(ray, self.max_depth)
                
                # Clamping
                color.x = min(1.0, max(0.0, color.x))
                color.y = min(1.0, max(0.0, color.y))
                color.z = min(1.0, max(0.0, color.z))
                
                image[j][i] = color
                
                # Manually added debug print
                print(f"Koordinaten {j + 1}/{i+1} berechnet", end='\r')
        
        return image

# ============================================================================
# Bildspeicherung (PPM-Format)
# ============================================================================

def save_ppm(filename: str, image: List[List[Vec3]]):
    height = len(image)
    width = len(image[0])
    
    with open(filename, 'w') as f:
        f.write(f"P3\n{width} {height}\n255\n")
        
        for j in range(height):
            for i in range(width):
                color = image[j][i]
                r = int(color.x * 255.99)
                g = int(color.y * 255.99)
                b = int(color.z * 255.99)
                f.write(f"{r} {g} {b} ")
            f.write("\n")

# ============================================================================
# Hauptprogramm - Cornell Box Setup
# ============================================================================

def create_cornell_box():
    world = World()
    
    # Materialien
    red = Material(Vec3(1, 0.2, 0.2))          # Rote Wand
    green = Material(Vec3(0.2, 1, 0.2))        # Grüne Wand
    white = Material(Vec3(0.9, 0.9, 0.9))      # Weiße Wände
    light = Material(Vec3(0, 0, 0), Vec3(1, 1, 1) * 5.0, 0.0)  # Lichtquelle
    sphere_material = Material(Vec3(0.8, 0.6, 0.4), reflectivity=0.3)  # Braune Kugel mit Reflexion
    mirror = Material(Vec3(0.9, 0.9, 0.9), reflectivity=0.8)  # Spiegelnde Kugel
    
    # Wände
    world.add(Plane(Vec3(0, -2, 0), Vec3(0, 1, 0), white, 3))      # Boden
    world.add(Plane(Vec3(0, 3, 0), Vec3(0, -1, 0), white, 3))      # Decke
    world.add(Plane(Vec3(-3, 0, 0), Vec3(1, 0, 0), red, 3))        # Linke Wand (rot)
    world.add(Plane(Vec3(3, 0, 0), Vec3(-1, 0, 0), green, 3))      # Rechte Wand (grün)
    world.add(Plane(Vec3(0, 0, -4), Vec3(0, 0, 1), white, 3))      # Hintere Wand
    
    # Lichtquelle an der Decke
    world.add(Sphere(Vec3(0, 2.5, 0), 0.5, light))
    
    # Zwei Kugeln
    world.add(Sphere(Vec3(-1.2, -1, -1), 1.0, sphere_material))
    world.add(Sphere(Vec3(1.5, -1, 0.5), 1.0, mirror))
    
    return world

def main():
    # Szene erstellen
    world = create_cornell_box()
    
    # Kamera setup
    look_from = Vec3(0, 1, 5)
    look_at = Vec3(0, 0, -1)
    v_up = Vec3(0, 1, 0)
    v_fov = 60
    aspect = 800 / 600
    
    camera = Camera(look_from, look_at, v_up, v_fov, aspect)
    
    # Raytracer erstellen und rendern
    width, height = 800, 600
    raytracer = Raytracer(world, camera, width, height, max_depth=5)
    
    print("Rendere Cornell Box...")
    image = raytracer.render()
    
    # Bild speichern
    save_ppm("cornell_box.ppm", image)
    print("Bild gespeichert als 'cornell_box.ppm'")

if __name__ == "__main__":
    main()