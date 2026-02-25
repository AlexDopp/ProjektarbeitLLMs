import numpy as np
from PIL import Image
from dataclasses import dataclass
from typing import Optional, Tuple, List
import math

# ============================================================================
# Mathematik-Bibliothek
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
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def normalize(self):
        length = math.sqrt(self.dot(self))
        if length > 0:
            return self * (1.0 / length)
        return self
    
    def length(self):
        return math.sqrt(self.dot(self))

@dataclass
class Ray:
    """Strahl mit Ursprung und Richtung"""
    origin: Vec3
    direction: Vec3
    
    def point_at(self, t: float):
        return self.origin + self.direction * t

# ============================================================================
# Szenengeometrie
# ============================================================================

@dataclass
class Material:
    """Materialeigenschaften für Objekte"""
    color: Tuple[float, float, float]  # RGB-Werte (0-1)
    emissive: bool = False  # Ist es eine Lichtquelle?
    emission_strength: float = 0.0

@dataclass
class HitRecord:
    """Informationen über einen Schnittpunkt"""
    t: float
    point: Vec3
    normal: Vec3
    material: Material

class Sphere:
    """Kugel-Objekt"""
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
            t = (-b - sqrt_disc) / a
            if t_min < t < t_max:
                point = ray.point_at(t)
                normal = (point - self.center) * (1.0 / self.radius)
                return HitRecord(t, point, normal, self.material)
            
            t = (-b + sqrt_disc) / a
            if t_min < t < t_max:
                point = ray.point_at(t)
                normal = (point - self.center) * (1.0 / self.radius)
                return HitRecord(t, point, normal, self.material)
        
        return None

class Plane:
    """Ebene als Wand/Boden"""
    def __init__(self, point: Vec3, normal: Vec3, material: Material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) > 1e-6:
            t = self.normal.dot(self.point - ray.origin) / denom
            if t_min < t < t_max:
                point = ray.point_at(t)
                return HitRecord(t, point, self.normal, self.material)
        return None

class Scene:
    """Sammlung aller Objekte in der Szene"""
    def __init__(self):
        self.objects = []
    
    def add(self, obj):
        self.objects.append(obj)
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[Tuple[HitRecord, object]]:
        hit_record = None
        closest_t = t_max
        hit_object = None
        
        for obj in self.objects:
            hit = obj.hit(ray, t_min, closest_t)
            if hit:
                closest_t = hit.t
                hit_record = hit
                hit_object = obj
        
        if hit_record:
            return (hit_record, hit_object)
        return None

# ============================================================================
# Raytracing-Algorithmus
# ============================================================================

class Raytracer:
    def __init__(self, scene: Scene, width: int = 512, height: int = 512):
        self.scene = scene
        self.width = width
        self.height = height
        self.max_depth = 3  # Maximale Rekursionstiefe für Reflexionen
    
    def render(self):
        """Hauptrender-Funktion"""
        # Kamera-Position (fest)
        camera = Vec3(0, 1, 5)
        
        # Blickrichtung
        look_at = Vec3(0, 1, 0)
        view_up = Vec3(0, 1, 0)
        
        # Bildkoordinaten
        aspect_ratio = self.width / self.height
        viewport_height = 2.0
        viewport_width = aspect_ratio * viewport_height
        
        # Bildmatrix erstellen
        image = np.zeros((self.height, self.width, 3))
        
        # Für jeden Pixel einen Strahl aussenden
        for y in range(self.height):
            for x in range(self.width):
                # Berechnung der Strahlrichtung durch den Pixel
                u = (x + 0.5) / self.width - 0.5
                v = 0.5 - (y + 0.5) / self.height
                
                direction = Vec3(
                    u * viewport_width,
                    v * viewport_height,
                    -1.0  # Blickrichtung -z
                ).normalize()
                
                ray = Ray(camera, direction)
                color = self.trace_ray(ray, 0)
                
                # Gamma-Korrektur
                color = Vec3(
                    math.sqrt(color.x),
                    math.sqrt(color.y),
                    math.sqrt(color.z)
                )
                
                image[y, x] = [color.x, color.y, color.z]
            
            # Fortschritt anzeigen
            if y % 50 == 0:
                print(f"Zeile {y}/{self.height} gerendert")
        
        return image
    
    def trace_ray(self, ray: Ray, depth: int) -> Vec3:
        """Rekursives Raytracing"""
        if depth >= self.max_depth:
            return Vec3(0, 0, 0)
        
        hit_result = self.scene.hit(ray, 0.001, float('inf'))
        
        if hit_result is None:
            # Hintergrundfarbe (schwarz)
            return Vec3(0, 0, 0)
        
        hit_record, _ = hit_result
        
        # Emissionsfarbe (Lichtquellen)
        if hit_record.material.emissive:
            return Vec3(
                hit_record.material.color[0] * hit_record.material.emission_strength,
                hit_record.material.color[1] * hit_record.material.emission_strength,
                hit_record.material.color[2] * hit_record.material.emission_strength
            )
        
        # Beleuchtung berechnen
        color = Vec3(0, 0, 0)
        
        # Für jedes Objekt (Lichtquelle) indirekte Beleuchtung berechnen
        for obj in self.scene.objects:
            if hasattr(obj, 'material') and obj.material.emissive:
                # Lichtrichtung (vereinfacht: Punktlicht von der Lichtquelle)
                light_pos = None
                if isinstance(obj, Sphere):
                    light_pos = obj.center
                elif isinstance(obj, Plane):
                    light_pos = obj.point + obj.normal * 0.5
                
                if light_pos:
                    light_dir = (light_pos - hit_record.point).normalize()
                    
                    # Schattenstrahl
                    shadow_ray = Ray(hit_record.point + hit_record.normal * 0.001, light_dir)
                    shadow_hit = self.scene.hit(shadow_ray, 0.001, float('inf'))
                    
                    if shadow_hit is None:
                        # Einfaches diffuses Shading
                        intensity = max(0, hit_record.normal.dot(light_dir))
                        color = color + Vec3(
                            hit_record.material.color[0] * intensity * 0.8,
                            hit_record.material.color[1] * intensity * 0.8,
                            hit_record.material.color[2] * intensity * 0.8
                        )
        
        # Ambiente Beleuchtung
        color = color + Vec3(
            hit_record.material.color[0] * 0.2,
            hit_record.material.color[1] * 0.2,
            hit_record.material.color[2] * 0.2
        )
        
        # Reflexionen
        reflect_dir = ray.direction - hit_record.normal * (2 * ray.direction.dot(hit_record.normal))
        reflect_ray = Ray(hit_record.point + hit_record.normal * 0.001, reflect_dir)
        reflect_color = self.trace_ray(reflect_ray, depth + 1)
        
        # Reflexion hinzufügen (30% Reflexion)
        color = color + reflect_color * 0.3
        
        return color

# ============================================================================
# Hauptprogramm
# ============================================================================

def create_cornell_box() -> Scene:
    """Erstellt eine Cornell-Box-ähnliche Szene"""
    scene = Scene()
    
    # Materialien
    red = Material((1.0, 0.2, 0.2), False)
    green = Material((0.2, 1.0, 0.2), False)
    white = Material((1.0, 1.0, 1.0), False)
    blue = Material((0.2, 0.2, 1.0), False)
    light = Material((1.0, 1.0, 1.0), True, 15.0)  # Lichtquelle
    
    # Wände
    scene.add(Plane(Vec3(0, 0, 0), Vec3(0, 1, 0), white))     # Boden
    scene.add(Plane(Vec3(0, 2, 0), Vec3(0, -1, 0), white))    # Decke
    scene.add(Plane(Vec3(-2, 0, 0), Vec3(1, 0, 0), red))      # Linke Wand
    scene.add(Plane(Vec3(2, 0, 0), Vec3(-1, 0, 0), green))    # Rechte Wand
    scene.add(Plane(Vec3(0, 0, -2), Vec3(0, 0, 1), white))    # Rückwand
    scene.add(Plane(Vec3(0, 0, 2), Vec3(0, 0, -1), white))    # Vorderseite (offen für Kamera)
    
    # Objekte im Raum
    scene.add(Sphere(Vec3(-0.7, 0.5, -1), 0.5, blue))          # Blaue Kugel
    scene.add(Sphere(Vec3(0.7, 0.3, -0.5), 0.3, white))       # Kleine weiße Kugel
    
    # Lichtquelle an der Decke
    scene.add(Sphere(Vec3(0, 1.8, 0), 0.3, light))            # Glühende Kugel als Licht
    
    return scene

def main():
    """Hauptfunktion"""
    print("Erstelle Cornell-Box...")
    scene = create_cornell_box()
    
    print("Initialisiere Raytracer (512x512)...")
    raytracer = Raytracer(scene, 512, 512)
    
    print("Starte Rendering...")
    image = raytracer.render()
    
    print("Speichere Bild als 'cornellbox.png'...")
    # Bild skalieren auf 0-255 und speichern
    image = np.clip(image * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(image)
    img.save("cornellbox.png")
    
    print("Fertig! Bild wurde als 'cornellbox.png' gespeichert.")

if __name__ == "__main__":
    main()