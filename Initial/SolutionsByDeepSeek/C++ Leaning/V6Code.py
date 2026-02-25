import math
from dataclasses import dataclass
from typing import Optional, Tuple, List
import struct

# ============= Mathematik-Bibliothek =============
@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other): return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other): return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, scalar): return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    def __truediv__(self, scalar): return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    def dot(self, other): return self.x * other.x + self.y * other.y + self.z * other.z
    def cross(self, other): return Vec3(
        self.y * other.z - self.z * other.y,
        self.z * other.x - self.x * other.z,
        self.x * other.y - self.y * other.x
    )
    def norm(self): return math.sqrt(self.dot(self))
    def normalize(self): return self / self.norm()
    def __neg__(self): return Vec3(-self.x, -self.y, -self.z)

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3
    
    def at(self, t: float) -> Vec3:
        return self.origin + self.direction * t

# ============= Geometrie =============
@dataclass
class HitRecord:
    t: float
    point: Vec3
    normal: Vec3
    material: 'Material'

class Sphere:
    def __init__(self, center: Vec3, radius: float, material: 'Material'):
        self.center = center
        self.radius = radius
        self.material = material
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - a * c
        
        if discriminant < 0:
            return None
        
        sqrt_d = math.sqrt(discriminant)
        t = (-b - sqrt_d) / a
        if t < t_min or t > t_max:
            t = (-b + sqrt_d) / a
            if t < t_min or t > t_max:
                return None
        
        point = ray.at(t)
        normal = (point - self.center) / self.radius
        return HitRecord(t, point, normal, self.material)

class Quad:
    def __init__(self, corner: Vec3, u: Vec3, v: Vec3, material: 'Material'):
        self.corner = corner
        self.u = u
        self.v = v
        self.material = material
        self.normal = u.cross(v).normalize()
        self.d = self.normal.dot(corner)
        self.w = v.cross(u) / u.cross(v).dot(u.cross(v))
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-8:
            return None
        
        t = (self.d - self.normal.dot(ray.origin)) / denom
        if t < t_min or t > t_max:
            return None
        
        point = ray.at(t)
        planar = point - self.corner
        alpha = self.w.dot(planar.cross(self.v))
        beta = self.w.dot(self.u.cross(planar))
        
        if alpha < 0 or alpha > 1 or beta < 0 or beta > 1:
            return None
        
        return HitRecord(t, point, self.normal, self.material)

# ============= Materialien =============
@dataclass
class Material:
    color: Vec3
    emissive: Vec3 = Vec3(0, 0, 0)
    reflective: float = 0.0

# ============= Szene =============
class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []
    
    def add_object(self, obj):
        self.objects.append(obj)
        if hasattr(obj.material, 'emissive') and obj.material.emissive.norm() > 0:
            self.lights.append(obj)
    
    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[Tuple[HitRecord, object]]:
        closest_t = t_max
        closest_record = None
        closest_obj = None
        
        for obj in self.objects:
            record = obj.hit(ray, t_min, closest_t)
            if record:
                closest_t = record.t
                closest_record = record
                closest_obj = obj
        
        return (closest_record, closest_obj) if closest_record else None

# ============= Raytracer =============
class Raytracer:
    def __init__(self, width: int, height: int, samples: int = 4, max_depth: int = 5):
        self.width = width
        self.height = height
        self.samples = samples
        self.max_depth = max_depth
        self.scene = Scene()
    
    def random_in_hemisphere(self, normal: Vec3) -> Vec3:
        # Diffuse reflection
        while True:
            p = Vec3(2*random() - 1, 2*random() - 1, 2*random() - 1)
            if p.norm() < 1:
                if p.dot(normal) > 0:
                    return p.normalize()
                return -p.normalize()
    
    def trace(self, ray: Ray, depth: int) -> Vec3:
        if depth >= self.max_depth:
            return Vec3(0, 0, 0)
        
        hit_result = self.scene.hit(ray, 0.001, float('inf'))
        if not hit_result:
            return Vec3(0.1, 0.1, 0.2)  # Hintergrund
        
        record, obj = hit_result
        
        # Emission
        if obj.material.emissive.norm() > 0:
            return obj.material.emissive
        
        # Schatten und Beleuchtung
        color = Vec3(0, 0, 0)
        
        # Direkte Beleuchtung
        for light in self.scene.lights:
            if light == obj:
                continue
                
            # Zufälligen Punkt auf der Lichtquelle wählen
            light_pos = light.center if hasattr(light, 'center') else light.corner + light.u * random() + light.v * random()
            light_dir = (light_pos - record.point).normalize()
            light_distance = (light_pos - record.point).norm()
            
            # Schattenstrahl
            shadow_ray = Ray(record.point + record.normal * 0.001, light_dir)
            shadow_hit = self.scene.hit(shadow_ray, 0.001, light_distance - 0.001)
            
            if not shadow_hit:
                # Diffuse Beleuchtung
                diff = max(0, record.normal.dot(light_dir))
                color = color + obj.material.color * light.material.emissive * diff
        
        # Indirekte Beleuchtung (Reflexionen)
        if obj.material.reflective > 0:
            reflected = ray.direction - record.normal * 2 * ray.direction.dot(record.normal)
            reflected_ray = Ray(record.point + record.normal * 0.001, reflected)
            color = color + self.trace(reflected_ray, depth + 1) * obj.material.reflective
        
        # Diffuse Reflexion (indirekt)
        if obj.material.reflective < 1:
            scattered_dir = self.random_in_hemisphere(record.normal)
            scattered_ray = Ray(record.point + record.normal * 0.001, scattered_dir)
            color = color + obj.material.color * self.trace(scattered_ray, depth + 1) * 0.5
        
        return color
    
    def render(self, filename: str):
        # Kamera
        lookfrom = Vec3(278, 278, -800)
        lookat = Vec3(278, 278, 0)
        vup = Vec3(0, 1, 0)
        
        # Kamerakoordinaten
        w = (lookfrom - lookat).normalize()
        u = vup.cross(w).normalize()
        v = w.cross(u)
        
        # Bildparameter
        aspect = self.width / self.height
        fov = 40
        theta = fov * math.pi / 180
        half_height = math.tan(theta / 2)
        half_width = aspect * half_height
        
        # Bild erstellen
        image_data = [0] * (self.width * self.height * 3)
        
        for y in range(self.height):
            for x in range(self.width):
                color = Vec3(0, 0, 0)
                
                for _ in range(self.samples):
                    # Pixel mit zufälligem Offset für Anti-Aliasing
                    u_offset = (x + random()) / (self.width - 1) * 2 - 1
                    v_offset = (y + random()) / (self.height - 1) * 2 - 1
                    
                    ray_dir = w * -1 + u * u_offset * half_width + v * v_offset * half_height
                    ray = Ray(lookfrom, ray_dir.normalize())
                    color = color + self.trace(ray, 0)
                
                # Durchschnitt und Gammakorrektur
                color = color / self.samples
                color = Vec3(math.sqrt(color.x), math.sqrt(color.y), math.sqrt(color.z))
                
                # In Byte-Werte konvertieren
                idx = (y * self.width + x) * 3
                image_data[idx] = min(255, int(color.x * 255))
                image_data[idx + 1] = min(255, int(color.y * 255))
                image_data[idx + 2] = min(255, int(color.z * 255))
        
        # PPM-Bild speichern
        with open(filename, 'wb') as f:
            f.write(f'P6\n{self.width} {self.height}\n255\n'.encode())
            f.write(bytes(image_data))

# ============= Hauptprogramm =============
def random():
    return math.sin(id(random)) * 0.5 + 0.5  # Einfacher Pseudo-Zufallsgenerator

def main():
    # Szene erstellen (Cornell-Box Variante)
    rt = Raytracer(400, 300, samples=4, max_depth=5)
    
    # Materialien
    white = Material(Vec3(0.8, 0.8, 0.8))
    red = Material(Vec3(0.8, 0.2, 0.2))
    green = Material(Vec3(0.2, 0.8, 0.2))
    light = Material(Vec3(1, 1, 1), emissive=Vec3(15, 15, 15))
    mirror = Material(Vec3(0.9, 0.9, 0.9), reflective=0.9)
    
    # Wände
    rt.scene.add_object(Quad(Vec3(0, 0, 0), Vec3(550, 0, 0), Vec3(0, 550, 0), white))  # Boden
    rt.scene.add_object(Quad(Vec3(0, 550, 0), Vec3(550, 0, 0), Vec3(0, 0, 550), white))  # Decke
    rt.scene.add_object(Quad(Vec3(0, 0, 0), Vec3(0, 0, 550), Vec3(0, 550, 0), green))  # Linke Wand
    rt.scene.add_object(Quad(Vec3(550, 0, 0), Vec3(0, 0, 550), Vec3(0, 550, 0), red))  # Rechte Wand
    rt.scene.add_object(Quad(Vec3(0, 0, 550), Vec3(550, 0, 0), Vec3(0, 550, 0), white))  # Hintere Wand
    
    # Licht
    rt.scene.add_object(Quad(Vec3(200, 549, 200), Vec3(150, 0, 0), Vec3(0, 0, 150), light))
    
    # Objekte
    rt.scene.add_object(Sphere(Vec3(200, 100, 300), 100, mirror))
    rt.scene.add_object(Sphere(Vec3(350, 150, 200), 150, white))
    
    # Rendern
    rt.render("cornell_box.ppm")
    print("Bild wurde als 'cornell_box.ppm' gespeichert")

if __name__ == "__main__":
    main()