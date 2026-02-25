#!/usr/bin/env python3
"""
Eigenständiger Raytracer für eine Cornell-Box-Szene
Speichert das Ergebnis als PNG-Datei (cornellbox.png)
"""

import math
import random
import struct
import zlib
from dataclasses import dataclass
from typing import Optional, Tuple, List

# ============================================================================
# Mathematische Hilfsklassen
# ============================================================================

@dataclass
class Vec3:
    """3D-Vektor mit grundlegenden Operationen"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, Vec3):
            return Vec3(
                self.x * other.x,
                self.y * other.y,
                self.z * other.z
            )
        elif isinstance(other, (int, float)):
            return Vec3(
                self.x * other,
                self.y * other,
                self.z * other
            )
        return NotImplemented
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero")
            return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
        elif isinstance(scalar, Vec3):
            return Vec3(self.x / scalar.x, self.y / scalar.y, self.z / scalar.z)
        return NotImplemented
    
    def dot(self, other):
        if isinstance(other, Vec3):
            return self.x * other.x + self.y * other.y + self.z * other.z
        return NotImplemented
    
    def cross(self, other):
        if isinstance(other, Vec3):
            return Vec3(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
            )
        return NotImplemented
    
    def length(self):
        return math.sqrt(self.dot(self))
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return self / l
        return self
    
    def reflect(self, normal):
        """Reflektiert Vektor an Normalen"""
        if isinstance(normal, Vec3):
            return self - normal * (2 * self.dot(normal))
        return NotImplemented
    
    def norm(self):
        return math.sqrt(self.dot(self))

@dataclass
class Ray:
    """Strahl mit Ursprung und Richtung"""
    origin: Vec3
    direction: Vec3
    
    def point_at(self, t: float) -> Vec3:
        return self.origin + self.direction * t


# ============================================================================
# Geometrische Grundkörper
# ============================================================================

class HitRecord:
    """Informationen über einen Schnittpunkt"""
    def __init__(self, t: float, point: Vec3, normal: Vec3, material):
        self.t = t
        self.point = point
        self.normal = normal
        self.material = material


class Material:
    """Materialeigenschaften für Beleuchtungsberechnungen"""
    def __init__(self, color: Vec3, emission: Vec3 = Vec3(0, 0, 0)):
        self.color = color
        self.emission = emission


class Sphere:
    """Kugel als geometrischer Grundkörper"""
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
            sqrt_d = math.sqrt(discriminant)
            t = (-b - sqrt_d) / a
            if t_min < t < t_max:
                point = ray.point_at(t)
                normal = (point - self.center) / self.radius
                return HitRecord(t, point, normal, self.material)
            
            t = (-b + sqrt_d) / a
            if t_min < t < t_max:
                point = ray.point_at(t)
                normal = (point - self.center) / self.radius
                return HitRecord(t, point, normal, self.material)
        
        return None


class Plane:
    """Unendliche Ebene"""
    def __init__(self, point: Vec3, normal: Vec3, material: Material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-6:
            return None
        
        t = (self.point - ray.origin).dot(self.normal) / denom
        if t_min < t < t_max:
            point = ray.point_at(t)
            return HitRecord(t, point, self.normal, self.material)
        
        return None


class Rect:
    """Rechteck in der XY-Ebene"""
    def __init__(self, x0, x1, y0, y1, z, material, flip_normal=False, axis='z'):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.z = z
        self.material = material
        self.flip_normal = flip_normal
        self.axis = axis
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        if self.axis == 'z':
            if ray.direction.z == 0:
                return None
            t = (self.z - ray.origin.z) / ray.direction.z
            if t < t_min or t > t_max:
                return None
            x = ray.origin.x + t * ray.direction.x
            y = ray.origin.y + t * ray.direction.y
            if x < self.x0 or x > self.x1 or y < self.y0 or y > self.y1:
                return None
            normal = Vec3(0, 0, 1) if not self.flip_normal else Vec3(0, 0, -1)
        elif self.axis == 'x':
            if ray.direction.x == 0:
                return None
            t = (self.z - ray.origin.x) / ray.direction.x
            if t < t_min or t > t_max:
                return None
            y = ray.origin.y + t * ray.direction.y
            z = ray.origin.z + t * ray.direction.z
            if y < self.y0 or y > self.y1 or z < self.x0 or z > self.x1:
                return None
            normal = Vec3(1, 0, 0) if not self.flip_normal else Vec3(-1, 0, 0)
        elif self.axis == 'y':
            if ray.direction.y == 0:
                return None
            t = (self.z - ray.origin.y) / ray.direction.y
            if t < t_min or t > t_max:
                return None
            x = ray.origin.x + t * ray.direction.x
            z = ray.origin.z + t * ray.direction.z
            if x < self.x0 or x > self.x1 or z < self.y0 or z > self.y1:
                return None
            normal = Vec3(0, 1, 0) if not self.flip_normal else Vec3(0, -1, 0)
        else:
            return None
        
        point = ray.point_at(t)
        return HitRecord(t, point, normal, self.material)


# ============================================================================
# Szenenbeschreibung
# ============================================================================

class Scene:
    """Container für alle Objekte in der Szene"""
    def __init__(self):
        self.objects = []
        self.background = Vec3(0, 0, 0)
        self.setup_cornell_box()
    
    def setup_cornell_box(self):
        """Erstellt eine Cornell-Box mit einer Kugel"""
        # Materialien
        red = Material(Vec3(0.8, 0.2, 0.1))
        green = Material(Vec3(0.1, 0.8, 0.2))
        white = Material(Vec3(0.8, 0.8, 0.8))
        light = Material(Vec3(1.0, 1.0, 1.0), Vec3(15.0, 15.0, 15.0))
        blue = Material(Vec3(0.2, 0.4, 0.8))
        
        # Wände (Rechtecke)
        # Boden (y = 0)
        self.objects.append(Rect(-2.0, 2.0, -2.0, 2.0, 0.0, white, flip_normal=True, axis='y'))
        # Decke (y = 4)
        self.objects.append(Rect(-2.0, 2.0, -2.0, 2.0, 4.0, white, axis='y'))
        # Linke Wand (x = -2)
        self.objects.append(Rect(-2.0, 2.0, -2.0, 2.0, -2.0, green, flip_normal=True, axis='x'))
        # Rechte Wand (x = 2)
        self.objects.append(Rect(-2.0, 2.0, -2.0, 2.0, 2.0, red, axis='x'))
        # Hintere Wand (z = -2)
        self.objects.append(Rect(-2.0, 2.0, -2.0, 2.0, -2.0, white, axis='z'))
        
        # Licht an der Decke
        self.objects.append(Rect(-0.5, 0.5, 2.5, 3.5, 3.99, light, flip_normal=True, axis='y'))
        
        # Zwei Kugeln im Raum
        self.objects.append(Sphere(Vec3(-0.8, 0.8, -0.5), 0.8, white))
        self.objects.append(Sphere(Vec3(0.9, 0.6, 0.5), 0.6, blue))
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        """Findet den nächsten Schnittpunkt mit der Szene"""
        hit_record = None
        closest_t = t_max
        
        for obj in self.objects:
            record = obj.hit(ray, t_min, closest_t)
            if record is not None:
                closest_t = record.t
                hit_record = record
        
        return hit_record


# ============================================================================
# Raytracing-Logik
# ============================================================================

def random_in_hemisphere(normal: Vec3) -> Vec3:
    """Generiert einen zufälligen Vektor in der Hemisphäre um die Normale"""
    while True:
        v = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
        if v.norm() > 1:
            continue
        v = v.normalize()
        if v.dot(normal) > 0:
            return v


def trace_ray(ray: Ray, scene: Scene, depth: int) -> Vec3:
    """Verfolgt einen Strahl durch die Szene und berechnet die Farbe"""
    if depth <= 0:
        return Vec3(0, 0, 0)
    
    hit = scene.hit(ray, 0.001, float('inf'))
    if hit is None:
        return scene.background
    
    # Emission des getroffenen Materials
    emitted = hit.material.emission
    
    # Zufällige Richtung für indirekte Beleuchtung
    target = hit.point + hit.normal + random_in_hemisphere(hit.normal)
    new_ray = Ray(hit.point, (target - hit.point).normalize())
    
    # Rekursive Verfolgung
    incoming = trace_ray(new_ray, scene, depth - 1)
    
    # Beleuchtungsberechnung (Lambert'sches Modell)
    attenuation = hit.material.color * (1.0 / math.pi)
    
    return emitted + (attenuation * incoming)


def clamp(x: float, min_val: float, max_val: float) -> float:
    """Begrenzt einen Wert auf einen Bereich"""
    return max(min_val, min(max_val, x))


def to_pixel(color: Vec3) -> Tuple[int, int, int]:
    """Konvertiert einen Farbvektor in RGB-Werte"""
    # Tonemapping
    color = color / (color + Vec3(1, 1, 1))
    
    r = int(clamp(color.x * 255, 0, 255))
    g = int(clamp(color.y * 255, 0, 255))
    b = int(clamp(color.z * 255, 0, 255))
    return (r, g, b)


# ============================================================================
# PNG-Export (nur Standardbibliothek)
# ============================================================================

def write_png(filename: str, width: int, height: int, pixels: List[Tuple[int, int, int]]):
    """Schreibt ein PNG-Bild mit den gegebenen Pixeln"""
    
    def create_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = struct.pack('>I', len(data)) + chunk_type + data
        chunk += struct.pack('>I', zlib.crc32(chunk[4:]) & 0xffffffff)
        return chunk
    
    # PNG-Signatur
    png_data = bytearray(b'\x89PNG\r\n\x1a\n')
    
    # IHDR-Chunk
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    png_data += create_chunk(b'IHDR', ihdr)
    
    # IDAT-Chunk (Bilddaten)
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)  # Filter-Typ 0
        for x in range(width):
            idx = y * width + x
            r, g, b = pixels[idx]
            scanlines.extend([r, g, b])
    
    compressed = zlib.compress(scanlines)
    png_data += create_chunk(b'IDAT', compressed)
    
    # IEND-Chunk
    png_data += create_chunk(b'IEND', b'')
    
    # Datei schreiben
    with open(filename, 'wb') as f:
        f.write(png_data)


# ============================================================================
# Hauptprogramm
# ============================================================================

def main():
    """Hauptfunktion des Raytracers"""
    # Bildparameter
    width, height = 512, 512
    samples_per_pixel = 50
    max_depth = 10
    
    print(f"Rendere Cornell-Box mit {width}x{height} Pixeln...")
    print(f"Samples pro Pixel: {samples_per_pixel}, Tiefe: {max_depth}")
    
    # Kamera
    camera_pos = Vec3(0, 1.8, 5)
    look_at = Vec3(0, 1.5, 0)
    up = Vec3(0, 1, 0)
    
    # Kamera-Koordinatensystem
    w = (camera_pos - look_at).normalize()
    u = up.cross(w).normalize()
    v = w.cross(u)
    
    # Szene erstellen
    scene = Scene()
    
    # Bildspeicher
    pixels = []
    
    # Rendering-Schleife
    for y in range(height):
        for x in range(width):
            color_sum = Vec3(0, 0, 0)
            
            # Mehrere Samples pro Pixel (Antialiasing)
            for _ in range(samples_per_pixel):
                # Zufällige Abtastung innerhalb des Pixels
                u_offset = (x + random.random()) / width
                v_offset = (y + random.random()) / height
                
                # Strahl durch den Pixel berechnen
                ray_direction = w * (-1.5) + u * (2 * u_offset - 1) + v * (2 * v_offset - 1)
                ray = Ray(camera_pos, ray_direction.normalize())
                
                # Farbe berechnen
                color = trace_ray(ray, scene, max_depth)
                color_sum = color_sum + color
            
            # Durchschnitt über alle Samples
            pixel_color = color_sum / samples_per_pixel
            pixels.append(to_pixel(pixel_color))
            print(f"Pixel ({x}, {y}): {pixel_color} -> {pixels[-1]}", end='\r')

    
    # Bild speichern
    write_png("cornellbox.png", width, height, pixels)
    print("Fertig! Bild wurde als 'cornellbox.png' gespeichert.")


if __name__ == "__main__":
    # Zufallsgenerator initialisieren
    random.seed(42)
    main()