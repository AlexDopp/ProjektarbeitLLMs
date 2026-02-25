import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple
import struct

# ============================================================================
# Mathematik-Modul
# ============================================================================

@dataclass
class Vec3:
    """3D-Vektor mit grundlegenden Operationen"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
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
        if l > 0:
            return self / l
        return self
    
    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

@dataclass
class Ray:
    """Strahl mit Ursprung und Richtung"""
    origin: Vec3
    direction: Vec3
    
    def point_at(self, t: float) -> Vec3:
        return self.origin + self.direction * t

# ============================================================================
# Geometrie-Modul
# ============================================================================

class Material:
    """Material-Eigenschaften für Objekte"""
    def __init__(self, color: Vec3, emission: Vec3 = Vec3(), 
                 reflectance: float = 0.0, roughness: float = 0.0):
        self.color = color
        self.emission = emission
        self.reflectance = reflectance  # 0 = kein Spiegel, 1 = perfekter Spiegel
        self.roughness = roughness      # Oberflächenrauheit für diffuse Reflexion

class HitRecord:
    """Informationen über einen Trefferpunkt"""
    def __init__(self):
        self.t = float('inf')
        self.point = Vec3()
        self.normal = Vec3()
        self.material = None
        self.hit = False

class Sphere:
    """Kugel als geometrisches Primitive"""
    def __init__(self, center: Vec3, radius: float, material: Material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> HitRecord:
        record = HitRecord()
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - a * c
        
        if discriminant > 0:
            sqrt_disc = math.sqrt(discriminant)
            t = (-b - sqrt_disc) / a
            if t < t_max and t > t_min:
                record.t = t
                record.point = ray.point_at(t)
                record.normal = (record.point - self.center) / self.radius
                record.material = self.material
                record.hit = True
                return record
            
            t = (-b + sqrt_disc) / a
            if t < t_max and t > t_min:
                record.t = t
                record.point = ray.point_at(t)
                record.normal = (record.point - self.center) / self.radius
                record.material = self.material
                record.hit = True
                return record
        
        return record

class Plane:
    """Ebene als geometrisches Primitive"""
    def __init__(self, point: Vec3, normal: Vec3, material: Material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> HitRecord:
        record = HitRecord()
        denom = self.normal.dot(ray.direction)
        
        if abs(denom) > 1e-6:
            t = (self.point - ray.origin).dot(self.normal) / denom
            if t < t_max and t > t_min:
                record.t = t
                record.point = ray.point_at(t)
                record.normal = self.normal
                record.material = self.material
                record.hit = True
        
        return record

class World:
    """Welt, die alle Objekte enthält"""
    def __init__(self):
        self.objects = []
    
    def add(self, obj):
        self.objects.append(obj)
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> HitRecord:
        closest_record = HitRecord()
        closest_record.t = t_max
        
        for obj in self.objects:
            record = obj.hit(ray, t_min, closest_record.t)
            if record.hit:
                closest_record = record
        
        return closest_record

# ============================================================================
# Raytracing-Modul
# ============================================================================

class Camera:
    """Kamera mit Position und Blickrichtung"""
    def __init__(self, lookfrom: Vec3, lookat: Vec3, vup: Vec3, 
                 vfov: float, aspect: float):
        self.origin = lookfrom
        self.lookat = lookat
        
        theta = vfov * math.pi / 180
        half_height = math.tan(theta / 2)
        half_width = aspect * half_height
        
        w = (lookfrom - lookat).normalize()
        u = vup.cross(w).normalize()
        v = w.cross(u)
        
        self.lower_left_corner = self.origin - u * half_width - v * half_height - w
        self.horizontal = u * (2 * half_width)
        self.vertical = v * (2 * half_height)
    
    def get_ray(self, u: float, v: float) -> Ray:
        direction = self.lower_left_corner + self.horizontal * u + self.vertical * v - self.origin
        return Ray(self.origin, direction.normalize())

class Raytracer:
    """Haupt-Raytracer mit Rekursion und Beleuchtungsberechnung"""
    def __init__(self, world: World, max_depth: int = 10):
        self.world = world
        self.max_depth = max_depth
        self.background_color = Vec3(0.1, 0.1, 0.1)
    
    def trace(self, ray: Ray, depth: int) -> Vec3:
        if depth >= self.max_depth:
            return Vec3()
        
        record = self.world.hit(ray, 0.001, float('inf'))
        
        if not record.hit:
            return self.background_color
        
        # Emission des getroffenen Materials
        color = record.material.emission
        
        # Reflexion berechnen
        if record.material.reflectance > 0:
            reflected = self.reflect(ray.direction, record.normal)
            # Rauheit durch zufällige Abweichung
            if record.material.roughness > 0:
                random_dir = Vec3(random.uniform(-1, 1), 
                                 random.uniform(-1, 1), 
                                 random.uniform(-1, 1)).normalize()
                reflected = (reflected + random_dir * record.material.roughness).normalize()
            
            reflected_ray = Ray(record.point, reflected)
            reflected_color = self.trace(reflected_ray, depth + 1)
            color = color + reflected_color * record.material.reflectance
        
        # Diffuse Beleuchtung (vereinfacht)
        if record.material.color.length() > 0:
            # Einfache Ambient-Beleuchtung
            ambient = record.material.color * 0.3
            
            # Direkte Beleuchtung von Lichtquellen simulieren
            # In einer echten Cornell-Box würden hier mehrere Lichtquellen berechnet
            light_dir = Vec3(0.5, 1, 0.5).normalize()
            light_intensity = max(0, record.normal.dot(light_dir))
            diffuse = record.material.color * light_intensity * 0.7
            
            color = color + ambient + diffuse
        
        return color
    
    def reflect(self, direction: Vec3, normal: Vec3) -> Vec3:
        """Berechnet reflektierten Vektor"""
        return direction - normal * (2 * direction.dot(normal))

# ============================================================================
# Bildausgabe-Modul
# ============================================================================

class ImageWriter:
    """Schreibt ein Bild im PPM-Format"""
    def __init__(self, filename: str, width: int, height: int):
        self.filename = filename
        self.width = width
        self.height = height
        self.pixels = [[Vec3() for _ in range(width)] for _ in range(height)]
    
    def set_pixel(self, x: int, y: int, color: Vec3):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
    
    def save(self):
        with open(self.filename, 'w') as f:
            # PPM Header
            f.write(f"P3\n{self.width} {self.height}\n255\n")
            
            for y in range(self.height):
                for x in range(self.width):
                    color = self.pixels[y][x]
                    # Gamma-Korrektur (vereinfacht)
                    r = int(math.sqrt(color.x) * 255)
                    g = int(math.sqrt(color.y) * 255)
                    b = int(math.sqrt(color.z) * 255)
                    
                    # Begrenzung auf [0, 255]
                    r = max(0, min(255, r))
                    g = max(0, min(255, g))
                    b = max(0, min(255, b))
                    
                    f.write(f"{r} {g} {b} ")
                f.write("\n")

# ============================================================================
# Hauptprogramm - Erstellung der Cornell-Box
# ============================================================================

def create_cornell_box() -> World:
    """Erstellt eine Cornell-Box mit verschiedenen Materialien"""
    world = World()
    
    # Materialien definieren
    red = Material(Vec3(1, 0.2, 0.2))          # Rote Wand
    green = Material(Vec3(0.2, 1, 0.2))        # Grüne Wand
    white = Material(Vec3(0.8, 0.8, 0.8))      # Weiße Wände
    light = Material(Vec3(1, 1, 1), Vec3(1, 1, 1) * 2)  # Lichtquelle
    mirror = Material(Vec3(1, 1, 1), reflectance=0.9, roughness=0.1)  # Spiegel
    blue_sphere = Material(Vec3(0.2, 0.2, 1), reflectance=0.3, roughness=0.2)  # Blaue Kugel
    
    # Box-Wände
    # Boden (y=0)
    world.add(Plane(Vec3(0, 0, 0), Vec3(0, 1, 0), white))
    # Decke (y=2)
    world.add(Plane(Vec3(0, 2, 0), Vec3(0, -1, 0), white))
    # Rückwand (z=-2)
    world.add(Plane(Vec3(0, 1, -2), Vec3(0, 0, 1), white))
    # Linke Wand (x=-2) - ROT
    world.add(Plane(Vec3(-2, 1, -1), Vec3(1, 0, 0), red))
    # Rechte Wand (x=2) - GRÜN
    world.add(Plane(Vec3(2, 1, -1), Vec3(-1, 0, 0), green))
    
    # Licht an der Decke
    world.add(Sphere(Vec3(0, 1.8, -0.5), 0.3, light))
    
    # Objekte in der Box
    # Spiegelnde Kugel
    world.add(Sphere(Vec3(-1, 0.5, 0), 0.5, mirror))
    # Blaue Kugel
    world.add(Sphere(Vec3(1, 0.4, -0.5), 0.4, blue_sphere))
    # Kleine weiße Kugel
    world.add(Sphere(Vec3(0, 0.3, 1), 0.3, white))
    
    return world

def main():
    """Hauptfunktion - führt den Raytracer aus und speichert das Bild"""
    # Bildparameter
    width = 800
    height = 600
    aspect = width / height
    
    # Welt erstellen
    world = create_cornell_box()
    
    # Kamera positionieren
    camera = Camera(
        lookfrom=Vec3(0, 1.5, 5),
        lookat=Vec3(0, 1, -1),
        vup=Vec3(0, 1, 0),
        vfov=60,
        aspect=aspect
    )
    
    # Raytracer initialisieren
    raytracer = Raytracer(world, max_depth=5)
    
    # Bild erstellen
    image = ImageWriter("cornell_box.ppm", width, height)
    
    print("Raytracing gestartet...")
    samples_per_pixel = 4  # Für bessere Qualität erhöhen
    
    for y in range(height):
        if y % 50 == 0:
            print(f"Zeile {y}/{height} fertig")
        
        for x in range(width):
            color = Vec3()
            
            # Mehrere Samples pro Pixel für Anti-Aliasing
            for _ in range(samples_per_pixel):
                u = (x + random.random()) / width
                v = (y + random.random()) / height
                
                ray = camera.get_ray(u, v)
                color = color + raytracer.trace(ray, 0)
            
            # Durchschnitt der Samples
            color = color / samples_per_pixel
            image.set_pixel(x, y, color)
    
    # Bild speichern
    image.save()
    print(f"Bild gespeichert als 'cornell_box.ppm'")

if __name__ == "__main__":
    main()