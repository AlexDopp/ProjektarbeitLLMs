// cornell_raytracer.cpp
#include <cmath>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <vector>

constexpr double EPS = 1e-4;
constexpr double INF = std::numeric_limits<double>::infinity();

// ============================================================
// MATHEMATIK
// ============================================================

struct Vec3 {
    double x, y, z;

    Vec3() : x(0), y(0), z(0) {}
    Vec3(double v) : x(v), y(v), z(v) {}
    Vec3(double x_, double y_, double z_) : x(x_), y(y_), z(z_) {}

    Vec3 operator+(const Vec3& b) const { return {x + b.x, y + b.y, z + b.z}; }
    Vec3 operator-(const Vec3& b) const { return {x - b.x, y - b.y, z - b.z}; }
    Vec3 operator*(double s) const { return {x * s, y * s, z * s}; }
    Vec3 operator/(double s) const { return {x / s, y / s, z / s}; }

    Vec3& operator+=(const Vec3& b) {
        x += b.x; y += b.y; z += b.z;
        return *this;
    }

    double dot(const Vec3& b) const { return x*b.x + y*b.y + z*b.z; }

    Vec3 normalize() const {
        double len = std::sqrt(dot(*this));
        return (*this) / len;
    }
};

Vec3 reflect(const Vec3& v, const Vec3& n) {
    return v - n * (2.0 * v.dot(n));
}

// ============================================================
// RAY
// ============================================================

struct Ray {
    Vec3 origin;
    Vec3 direction;
};

// ============================================================
// MATERIAL
// ============================================================

struct Material {
    Vec3 color;
    double reflectivity;

    Material(const Vec3& c, double r = 0.0)
        : color(c), reflectivity(r) {}
};

// ============================================================
// GEOMETRIE
// ============================================================

struct Hit {
    double t;
    Vec3 position;
    Vec3 normal;
    const Material* material;
};

struct Object {
    virtual ~Object() = default;
    virtual bool intersect(const Ray& ray, Hit& hit) const = 0;
};

struct Sphere : public Object {
    Vec3 center;
    double radius;
    Material material;

    Sphere(const Vec3& c, double r, const Material& m)
        : center(c), radius(r), material(m) {}

    bool intersect(const Ray& ray, Hit& hit) const override {
        Vec3 oc = ray.origin - center;
        double a = ray.direction.dot(ray.direction);
        double b = 2.0 * oc.dot(ray.direction);
        double c = oc.dot(oc) - radius * radius;
        double disc = b*b - 4*a*c;

        if (disc < 0) return false;

        double t = (-b - std::sqrt(disc)) / (2*a);
        if (t < EPS) return false;

        hit.t = t;
        hit.position = ray.origin + ray.direction * t;
        hit.normal = (hit.position - center).normalize();
        hit.material = &material;
        return true;
    }
};

struct Plane : public Object {
    Vec3 point;
    Vec3 normal;
    Material material;

    Plane(const Vec3& p, const Vec3& n, const Material& m)
        : point(p), normal(n.normalize()), material(m) {}

    bool intersect(const Ray& ray, Hit& hit) const override {
        double denom = normal.dot(ray.direction);
        if (std::abs(denom) < EPS) return false;

        double t = (point - ray.origin).dot(normal) / denom;
        if (t < EPS) return false;

        hit.t = t;
        hit.position = ray.origin + ray.direction * t;
        hit.normal = normal;
        hit.material = &material;
        return true;
    }
};

// ============================================================
// LICHT
// ============================================================

struct Light {
    Vec3 position;
    Vec3 intensity;
};

// ============================================================
// SCENE
// ============================================================

struct Scene {
    std::vector<std::unique_ptr<Object>> objects;
    std::vector<Light> lights;
};

// ============================================================
// RAYTRACER
// ============================================================

Vec3 trace(const Ray& ray, const Scene& scene, int depth) {
    if (depth <= 0) return Vec3(0);

    Hit closestHit;
    closestHit.t = INF;
    bool hitSomething = false;

    for (const auto& obj : scene.objects) {
        Hit hit;
        if (obj->intersect(ray, hit) && hit.t < closestHit.t) {
            closestHit = hit;
            hitSomething = true;
        }
    }

    if (!hitSomething) return Vec3(0);

    Vec3 color(0);

    for (const auto& light : scene.lights) {
        Vec3 toLight = (light.position - closestHit.position).normalize();

        // Schattenray
        Ray shadowRay{
            closestHit.position + closestHit.normal * EPS,
            toLight
        };

        bool inShadow = false;
        for (const auto& obj : scene.objects) {
            Hit shadowHit;
            if (obj->intersect(shadowRay, shadowHit)) {
                inShadow = true;
                break;
            }
        }

        if (!inShadow) {
            double diff = std::max(0.0, closestHit.normal.dot(toLight));
            color += closestHit.material->color * diff;
        }
    }

    // Reflexion
    if (closestHit.material->reflectivity > 0.0) {
        Vec3 reflDir = reflect(ray.direction, closestHit.normal).normalize();
        Ray reflRay{
            closestHit.position + closestHit.normal * EPS,
            reflDir
        };

        Vec3 reflColor = trace(reflRay, scene, depth - 1);
        color = color * (1.0 - closestHit.material->reflectivity)
              + reflColor * closestHit.material->reflectivity;
    }

    return color;
}

// ============================================================
// MAIN
// ============================================================

int main() {
    const int width = 400;
    const int height = 400;
    const int maxDepth = 3;

    Scene scene;

    // Materialien
    Material red({1, 0, 0});
    Material green({0, 1, 0});
    Material white({0.8, 0.8, 0.8});
    Material mirror({1, 1, 1}, 0.8);

    // Cornellbox-Wände
    scene.objects.push_back(std::make_unique<Plane>(Vec3(0, -1, 0), Vec3(0, 1, 0), white));  // Boden
    scene.objects.push_back(std::make_unique<Plane>(Vec3(0, 1, 0), Vec3(0, -1, 0), white));  // Decke
    scene.objects.push_back(std::make_unique<Plane>(Vec3(0, 0, -3), Vec3(0, 0, 1), white));  // Rückwand
    scene.objects.push_back(std::make_unique<Plane>(Vec3(-1, 0, 0), Vec3(1, 0, 0), red));    // Links
    scene.objects.push_back(std::make_unique<Plane>(Vec3(1, 0, 0), Vec3(-1, 0, 0), green));  // Rechts

    // Kugeln
    scene.objects.push_back(std::make_unique<Sphere>(Vec3(-0.4, -0.5, -2), 0.5, mirror));
    scene.objects.push_back(std::make_unique<Sphere>(Vec3(0.4, -0.7, -1.5), 0.3, white));

    // Licht
    scene.lights.push_back({Vec3(0, 0.9, -2), Vec3(1, 1, 1)});

    //Changed "output.ppm" to "V3Box.ppm"
    std::ofstream out("V3Box.ppm");
    out << "P3\n" << width << " " << height << "\n255\n";

    Vec3 camPos(0, 0, 1);

    for (int y = height - 1; y >= 0; --y) {
        for (int x = 0; x < width; ++x) {
            double u = (x + 0.5) / width * 2 - 1;
            double v = (y + 0.5) / height * 2 - 1;

            Ray ray{
                camPos,
                Vec3(u, v, -1).normalize()
            };

            Vec3 col = trace(ray, scene, maxDepth);
            col.x = std::min(1.0, col.x);
            col.y = std::min(1.0, col.y);
            col.z = std::min(1.0, col.z);

            out << int(col.x * 255) << " "
                << int(col.y * 255) << " "
                << int(col.z * 255) << "\n";
        }
    }

    std::cout << "Rendering abgeschlossen: output.ppm\n";
    return 0;
}
