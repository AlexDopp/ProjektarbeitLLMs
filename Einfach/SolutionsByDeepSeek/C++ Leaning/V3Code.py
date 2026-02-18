import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
import struct

# ============================================================================
# Mathematik-Bereich
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
        length = self.length()
        if length > 0:
            return self / length
        return self
    
    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)


@dataclass
class Ray:
    """Strahl mit Ursprung und Richtung"""
    origin: Vec3
    direction: Vec3
    
    def point_at(self, t: float) -> Vec3:
        return self.origin + self.direction * t


# ============================================================================
# Geometrie-Bereich
# ============================================================================

@dataclass
class Material:
    """Materialeigenschaften für Oberflächen"""
    color: Vec3
    emissive: Vec3 = Vec3(0, 0, 0)
    reflective: float = 0.0  # 0 = nicht reflektierend, 1 = voll reflektierend


@dataclass
class HitRecord:
    """Informationen über einen Schnittpunkt"""
    point: Vec3
    normal: Vec3
    t: float
    material: Material
    front_face: bool


class Hittable:
    """Abstrakte Basisklasse für alle geometrischen Objekte"""
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        raise NotImplementedError


class Sphere(Hittable):
    """Kugel-Implementierung"""
    def __init__(self, center: Vec3, radius: float, material: Material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - a * c
        
        if discriminant > 0:
            sqrt_disc = math.sqrt(discriminant)
            
            # Zwei Lösungen prüfen
            for t in [(-b - sqrt_disc) / a, (-b + sqrt_disc) / a]:
                if t_min < t < t_max:
                    point = ray.point_at(t)
                    normal = (point - self.center) / self.radius
                    front_face = ray.direction.dot(normal) < 0
                    
                    return HitRecord(
                        point=point,
                        normal=normal if front_face else -normal,
                        t=t,
                        material=self.material,
                        front_face=front_face
                    )
        return None


class Quad(Hittable):
    """Viereck (für Wände der Cornell-Box)"""
    def __init__(self, corner: Vec3, u: Vec3, v: Vec3, material: Material):
        self.corner = corner
        self.u = u
        self.v = v
        self.material = material
        self.normal = u.cross(v).normalize()
        self.d = self.normal.dot(corner)
        self.w = self.normal.cross(u)
        self.area = u.cross(v).length()
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        
        if abs(denom) < 1e-8:
            return None
        
        t = (self.d - self.normal.dot(ray.origin)) / denom
        
        if t < t_min or t > t_max:
            return None
        
        point = ray.point_at(t)
        planar_hit = point - self.corner
        alpha = self.w.dot(planar_hit) / (self.w.dot(self.u))
        beta = self.normal.cross(self.u).dot(planar_hit) / (self.normal.cross(self.u).dot(self.v))
        
        if 0 <= alpha <= 1 and 0 <= beta <= 1:
            front_face = ray.direction.dot(self.normal) < 0
            return HitRecord(
                point=point,
                normal=self.normal if front_face else -self.normal,
                t=t,
                material=self.material,
                front_face=front_face
            )
        return None


# ============================================================================
# Raytracing-Bereich
# ============================================================================

class Camera:
    """Einfache Kamera mit Position und Blickrichtung"""
    def __init__(self, lookfrom: Vec3, lookat: Vec3, vup: Vec3, 
                 vfov: float, aspect_ratio: float):
        theta = math.radians(vfov)
        h = math.tan(theta / 2)
        viewport_height = 2.0 * h
        viewport_width = aspect_ratio * viewport_height
        
        w = (lookfrom - lookat).normalize()
        u = vup.cross(w).normalize()
        v = w.cross(u)
        
        self.origin = lookfrom
        self.horizontal = u * viewport_width
        self.vertical = v * viewport_height
        self.lower_left_corner = self.origin - self.horizontal/2 - self.vertical/2 - w
    
    def get_ray(self, u: float, v: float) -> Ray:
        return Ray(
            self.origin,
            (self.lower_left_corner + self.horizontal * u + self.vertical * v - self.origin).normalize()
        )


class Scene:
    """Szene mit allen Objekten"""
    def __init__(self):
        self.objects: List[Hittable] = []
    
    def add(self, obj: Hittable):
        self.objects.append(obj)
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        closest_hit = None
        closest_t = t_max
        
        for obj in self.objects:
            hit = obj.hit(ray, t_min, closest_t)
            if hit:
                closest_t = hit.t
                closest_hit = hit
        
        return closest_hit


class RayTracer:
    """Haupt-Raytracer mit Beleuchtungsberechnung"""
    def __init__(self, scene: Scene, camera: Camera, max_depth: int = 5):
        self.scene = scene
        self.camera = camera
        self.max_depth = max_depth
        self.background = Vec3(0.1, 0.1, 0.1)
    
    def trace(self, ray: Ray, depth: int = 0) -> Vec3:
        if depth >= self.max_depth:
            return Vec3(0, 0, 0)
        
        hit = self.scene.hit(ray, 0.001, float('inf'))
        
        if not hit:
            return self.background
        
        # Emittiertes Licht
        emitted = hit.material.emissive
        
        # Reflexion berechnen
        if hit.material.reflective > 0:
            reflected_dir = ray.direction - hit.normal * 2 * ray.direction.dot(hit.normal)
            reflected_ray = Ray(hit.point, reflected_dir.normalize())
            reflected_color = self.trace(reflected_ray, depth + 1)
            return emitted + reflected_color * hit.material.reflective
        
        # Direkte Beleuchtung (einfaches ambient + diffus)
        ambient = Vec3(0.1, 0.1, 0.1)
        
        # Schatten und diffuse Beleuchtung
        light_pos = Vec3(278, 548, 279)  # Lichtposition in der Cornell-Box
        light_dir = (light_pos - hit.point).normalize()
        light_distance = (light_pos - hit.point).length()
        
        # Schattenstrahl
        shadow_ray = Ray(hit.point + hit.normal * 0.001, light_dir)
        shadow_hit = self.scene.hit(shadow_ray, 0.001, light_distance)
        
        if not shadow_hit:
            # Diffuse Beleuchtung
            diff = max(0, hit.normal.dot(light_dir))
            light_color = Vec3(15, 15, 15)  # Helles Licht
            diffuse = hit.material.color * light_color * diff / (light_distance * light_distance)
        else:
            diffuse = Vec3(0, 0, 0)
        
        return emitted + ambient * hit.material.color + diffuse


# ============================================================================
# Bildausgabe
# ============================================================================

def write_ppm(filename: str, width: int, height: int, pixels: List[Vec3]):
    """Schreibt das Bild im PPM-Format"""
    with open(filename, 'wb') as f:
        # Header
        f.write(f"P6\n{width} {height}\n255\n".encode())
        
        # Pixel-Daten
        for pixel in pixels:
            # Clamping und Gamma-Korrektur (einfaches sqrt für Gamma 2)
            r = int(255 * math.sqrt(max(0, min(1, pixel.x))))
            g = int(255 * math.sqrt(max(0, min(1, pixel.y))))
            b = int(255 * math.sqrt(max(0, min(1, pixel.z))))
            
            f.write(struct.pack('BBB', r, g, b))


# ============================================================================
# Hauptprogramm - Cornell-Box Variante
# ============================================================================

def create_cornell_box() -> Scene:
    """Erstellt eine Cornell-Box Variante"""
    scene = Scene()
    
    # Materialien
    red = Material(Vec3(0.8, 0.2, 0.2))
    green = Material(Vec3(0.2, 0.8, 0.2))
    white = Material(Vec3(0.8, 0.8, 0.8))
    light = Material(Vec3(0.8, 0.8, 0.8), Vec3(15, 15, 15))
    mirror = Material(Vec3(1, 1, 1), reflective=0.9)
    
    # Box-Größe
    size = 550
    
    # Wände
    # Boden
    scene.add(Quad(Vec3(0, 0, 0), Vec3(size, 0, 0), Vec3(0, 0, size), white))
    # Decke
    scene.add(Quad(Vec3(0, size, 0), Vec3(size, 0, 0), Vec3(0, 0, size), white))
    # Linke Wand (rot)
    scene.add(Quad(Vec3(0, 0, 0), Vec3(0, size, 0), Vec3(0, 0, size), red))
    # Rechte Wand (grün)
    scene.add(Quad(Vec3(size, 0, 0), Vec3(0, size, 0), Vec3(0, 0, size), green))
    # Hintere Wand
    scene.add(Quad(Vec3(0, 0, size), Vec3(size, 0, 0), Vec3(0, size, 0), white))
    
    # Licht an der Decke
    light_size = 100
    light_center = Vec3(size/2 - light_size/2, size - 1, size/2 - light_size/2)
    scene.add(Quad(light_center, Vec3(light_size, 0, 0), Vec3(0, 0, light_size), light))
    
    # Objekte in der Box
    # Linker Block
    scene.add(Quad(Vec3(100, 0, 400), Vec3(150, 0, 0), Vec3(0, 150, 0), white))
    scene.add(Quad(Vec3(100, 150, 400), Vec3(150, 0, 0), Vec3(0, 0, 150), white))
    scene.add(Quad(Vec3(250, 0, 400), Vec3(0, 150, 0), Vec3(0, 0, 150), white))
    
    # Rechter Block (Kugel)
    scene.add(Sphere(Vec3(400, 100, 200), 100, mirror))
    
    return scene


def main():
    """Hauptfunktion"""
    # Bildparameter
    width = 400
    height = 300
    aspect_ratio = width / height
    
    # Kamera
    camera = Camera(
        lookfrom=Vec3(275, 275, -600),
        lookat=Vec3(275, 275, 275),
        vup=Vec3(0, 1, 0),
        vfov=40,
        aspect_ratio=aspect_ratio
    )
    
    # Szene erstellen
    scene = create_cornell_box()
    
    # Raytracer initialisieren
    raytracer = RayTracer(scene, camera, max_depth=3)
    
    # Bild rendern
    print(f"Rendere {width}x{height} Bild...")
    pixels = []
    
    for j in range(height):
        if j % 50 == 0:
            print(f"Zeile {j}/{height}")
        
        for i in range(width):
            u = (i + 0.5) / width
            v = (j + 0.5) / height
            
            ray = camera.get_ray(u, v)
            color = raytracer.trace(ray)
            pixels.append(color)
    
    # Bild speichern
    write_ppm("cornell_box.ppm", width, height, pixels)
    print("Bild gespeichert als 'cornell_box.ppm'")


if __name__ == "__main__":
    main()