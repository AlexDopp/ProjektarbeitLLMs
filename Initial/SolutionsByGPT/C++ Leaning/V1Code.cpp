#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>
#include <memory>
#include <limits>

// ===================== Vektor- und Mathematik-Klassen =====================
struct Vec3 {
    double x, y, z;
    Vec3(double x_=0, double y_=0, double z_=0) : x(x_), y(y_), z(z_) {}
    Vec3 operator+(const Vec3 &v) const { return Vec3(x+v.x, y+v.y, z+v.z); }
    Vec3 operator-(const Vec3 &v) const { return Vec3(x-v.x, y-v.y, z-v.z); }
    Vec3 operator*(double s) const { return Vec3(x*s, y*s, z*s); }
    Vec3 operator/(double s) const { return Vec3(x/s, y/s, z/s); }
    Vec3 normalized() const { double len = std::sqrt(x*x + y*y + z*z); return *this / len; }
    double dot(const Vec3 &v) const { return x*v.x + y*v.y + z*v.z; }
    Vec3 cross(const Vec3 &v) const {
        return Vec3(y*v.z - z*v.y, z*v.x - x*v.z, x*v.y - y*v.x);
    }
};

using Color = Vec3;

// ===================== Ray =====================
struct Ray {
    Vec3 origin, direction;
    Ray(const Vec3 &o, const Vec3 &d) : origin(o), direction(d.normalized()) {}
};

// ===================== Material =====================
struct Material {
    Color color;
    double reflectivity;
    Material(const Color &c, double r=0) : color(c), reflectivity(r) {}
};

// ===================== Hitable Primitives =====================
struct HitRecord {
    Vec3 point;
    Vec3 normal;
    std::shared_ptr<Material> material;
    double t;
};

class Hitable {
public:
    virtual bool hit(const Ray &r, double t_min, double t_max, HitRecord &rec) const = 0;
};

// ---------------- Sphere ----------------
class Sphere : public Hitable {
public:
    Vec3 center;
    double radius;
    std::shared_ptr<Material> material;
    Sphere(const Vec3 &c, double r, std::shared_ptr<Material> m) : center(c), radius(r), material(m) {}
    bool hit(const Ray &r, double t_min, double t_max, HitRecord &rec) const override {
        Vec3 oc = r.origin - center;
        double a = r.direction.dot(r.direction);
        double b = oc.dot(r.direction);
        double c = oc.dot(oc) - radius*radius;
        double discriminant = b*b - a*c;
        if (discriminant > 0) {
            double temp = (-b - std::sqrt(discriminant)) / a;
            if(temp < t_max && temp > t_min) {
                rec.t = temp;
                rec.point = r.origin + r.direction*rec.t;
                rec.normal = (rec.point - center) / radius;
                rec.material = material;
                return true;
            }
            temp = (-b + std::sqrt(discriminant)) / a;
            if(temp < t_max && temp > t_min) {
                rec.t = temp;
                rec.point = r.origin + r.direction*rec.t;
                rec.normal = (rec.point - center) / radius;
                rec.material = material;
                return true;
            }
        }
        return false;
    }
};

// ---------------- Plane ----------------
class Plane : public Hitable {
public:
    Vec3 point, normal;
    std::shared_ptr<Material> material;
    Plane(const Vec3 &p, const Vec3 &n, std::shared_ptr<Material> m) : point(p), normal(n.normalized()), material(m) {}
    bool hit(const Ray &r, double t_min, double t_max, HitRecord &rec) const override {
        double denom = normal.dot(r.direction);
        if(std::abs(denom) > 1e-6) {
            double t = (point - r.origin).dot(normal) / denom;
            if(t >= t_min && t <= t_max) {
                rec.t = t;
                rec.point = r.origin + r.direction*t;
                rec.normal = normal;
                rec.material = material;
                return true;
            }
        }
        return false;
    }
};

// ===================== Scene =====================
class Scene {
public:
    std::vector<std::shared_ptr<Hitable>> objects;
    void add(std::shared_ptr<Hitable> obj) { objects.push_back(obj); }

    bool hit(const Ray &r, double t_min, double t_max, HitRecord &rec) const {
        HitRecord tempRec;
        bool hitAnything = false;
        double closestSoFar = t_max;
        for(const auto &obj : objects) {
            if(obj->hit(r, t_min, closestSoFar, tempRec)) {
                hitAnything = true;
                closestSoFar = tempRec.t;
                rec = tempRec;
            }
        }
        return hitAnything;
    }
};

// ===================== Raytracer =====================
Color rayColor(const Ray &r, const Scene &scene, int depth) {
    if(depth <= 0) return Color(0,0,0);
    HitRecord rec;
    if(scene.hit(r, 0.001, std::numeric_limits<double>::max(), rec)) {
        Vec3 target = rec.point + rec.normal;
        Ray reflectedRay(rec.point, r.direction - rec.normal*2*r.direction.dot(rec.normal));
        Color reflectedColor = rayColor(reflectedRay, scene, depth-1);
        return rec.material->color*(1-reflectedColor.dot(Color(1,1,1))*rec.material->reflectivity) + reflectedColor*rec.material->reflectivity;
    }
    // Hintergrundfarbe
    Vec3 unit_direction = r.direction.normalized();
    double t = 0.5*(unit_direction.y + 1.0);
    return Color(1.0,1.0,1.0)*(1.0-t) + Color(0.5,0.7,1.0)*t;
}

// ===================== Main =====================
int main() {
    // Bildgröße
    const int imageWidth = 400;
    const int imageHeight = 400;
    const int maxDepth = 5;

    // Kamera
    Vec3 origin(0,1,3);
    double viewportHeight = 2.0;
    double viewportWidth = 2.0;
    double focalLength = 1.0;
    Vec3 horizontal(viewportWidth,0,0);
    Vec3 vertical(0,viewportHeight,0);
    Vec3 lowerLeftCorner = origin - horizontal/2 - vertical/2 - Vec3(0,0,focalLength);

    // Szene
    Scene scene;
    auto red   = std::make_shared<Material>(Color(0.75,0.1,0.1));
    auto green = std::make_shared<Material>(Color(0.1,0.75,0.1));
    auto white = std::make_shared<Material>(Color(0.75,0.75,0.75));
    auto mirror= std::make_shared<Material>(Color(0.9,0.9,0.9), 0.7);

    // Cornellbox Wände
    scene.add(std::make_shared<Plane>(Vec3(0,0,0), Vec3(0,1,0), white)); // Boden
    scene.add(std::make_shared<Plane>(Vec3(0,2,0), Vec3(0,-1,0), white)); // Decke
    scene.add(std::make_shared<Plane>(Vec3(-1,0,0), Vec3(1,0,0), red)); // links
    scene.add(std::make_shared<Plane>(Vec3(1,0,0), Vec3(-1,0,0), green)); // rechts
    scene.add(std::make_shared<Plane>(Vec3(0,0,-1), Vec3(0,0,1), white)); // hinten

    // Kugel in der Box
    scene.add(std::make_shared<Sphere>(Vec3(-0.4,0.35,-0.3), 0.35, mirror));
    scene.add(std::make_shared<Sphere>(Vec3(0.5,0.3,-0.6), 0.3, white));

    // Bilddatei
    std::ofstream image("cornell.ppm");
    image << "P3\n" << imageWidth << " " << imageHeight << "\n255\n";

    for(int j = imageHeight-1; j >= 0; --j) {
        for(int i = 0; i < imageWidth; ++i) {
            double u = double(i)/ (imageWidth-1);
            double v = double(j)/ (imageHeight-1);
            Ray r(origin, lowerLeftCorner + horizontal*u + vertical*v - origin);
            Color col = rayColor(r, scene, maxDepth);
            int ir = static_cast<int>(255.999 * std::fmin(1.0, col.x));
            int ig = static_cast<int>(255.999 * std::fmin(1.0, col.y));
            int ib = static_cast<int>(255.999 * std::fmin(1.0, col.z));
            image << ir << " " << ig << " " << ib << "\n";
        }
    }

    image.close();
    std::cout << "Bild 'cornell.ppm' erstellt.\n";
    return 0;
}
