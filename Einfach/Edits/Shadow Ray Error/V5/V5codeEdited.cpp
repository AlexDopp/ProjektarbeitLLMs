#include <cmath>
#include <fstream>
#include <vector>
#include <limits>

constexpr double EPS = 1e-4;
constexpr int MAX_DEPTH = 3;

struct Vec {
    double x, y, z;
    Vec(double x=0, double y=0, double z=0) : x(x), y(y), z(z) {}
    Vec operator+(const Vec& b) const { return {x+b.x, y+b.y, z+b.z}; }
    Vec operator-(const Vec& b) const { return {x-b.x, y-b.y, z-b.z}; }
    Vec operator*(double s) const { return {x*s, y*s, z*s}; }
    Vec operator*(const Vec& b) const { return {x*b.x, y*b.y, z*b.z}; }
    Vec norm() const {
        double l = std::sqrt(x*x+y*y+z*z);
        return {x/l,y/l,z/l};
    }
    double dot(const Vec& b) const { return x*b.x+y*b.y+z*b.z; }
};

struct Ray {
    Vec o, d;
};

struct Material {
    Vec color;
    double reflect;
};

struct Hit {
    double t;
    Vec p, n;
    Material m;
};

struct Object {
    virtual bool intersect(const Ray&, Hit&) const = 0;
};

struct Sphere : Object {
    Vec c;
    double r;
    Material m;
    Sphere(Vec c, double r, Material m):c(c),r(r),m(m){}
    bool intersect(const Ray& ray, Hit& h) const override {
        Vec oc = ray.o - c;
        double b = oc.dot(ray.d);
        double c2 = oc.dot(oc) - r*r;
        double disc = b*b - c2;
        if (disc < 0) return false;
        double t = -b - std::sqrt(disc);
        if (t < EPS) return false;
        h.t = t;
        h.p = ray.o + ray.d*t;
        h.n = (h.p - c).norm();
        h.m = m;
        return true;
    }
};

struct Plane : Object {
    Vec n;
    double d;
    Material m;
    Plane(Vec n, double d, Material m):n(n),d(d),m(m){}
    bool intersect(const Ray& ray, Hit& h) const override {
        double denom = n.dot(ray.d);
        if (std::abs(denom) < EPS) return false;
        double t = -(n.dot(ray.o)+d)/denom;
        if (t < EPS) return false;
        h.t = t;
        h.p = ray.o + ray.d*t;
        h.n = n;
        h.m = m;
        return true;
    }
};

Vec reflect(const Vec& d, const Vec& n) {
    return d - n * (2 * d.dot(n));
}

Vec trace(const Ray& ray, const std::vector<Object*>& objs, const Vec& light, int depth) {
    if (depth > MAX_DEPTH) return {0,0,0};

    Hit hit;
    hit.t = std::numeric_limits<double>::max();
    bool found = false;

    for (auto o : objs) {
        Hit h;
        if (o->intersect(ray, h) && h.t < hit.t) {
            hit = h;
            found = true;
        }
    }

    if (!found) return {0,0,0};

    Vec ldir = (light - hit.p).norm();
    Ray shadow{hit.p + hit.n*EPS, ldir};

    bool shadowed = false;
    for (auto o : objs) {
        if (dynamic_cast<Plane*>(o)) continue;
        Hit h;
        if (o->intersect(shadow, h)) {
            shadowed = true;
            break;
        }
    }

    double diff = shadowed ? 0.0 : std::max(0.0, hit.n.dot(ldir));
    Vec color = hit.m.color * diff;

    if (hit.m.reflect > 0) {
        Vec rdir = reflect(ray.d, hit.n).norm();
        Ray rr{hit.p + hit.n*EPS, rdir};
        color = color*(1-hit.m.reflect) + trace(rr, objs, light, depth+1)*hit.m.reflect;
    }

    return color;
}

int main() {
    const int W = 400, H = 400;
    //Changed to "output.ppm" to "V5Box.ppm"
    std::ofstream img("V5Box.ppm");
    img << "P3\n" << W << " " << H << "\n255\n";

    Material red{{1,0.2,0.2},0};
    Material green{{0.2,1,0.2},0};
    Material white{{0.9,0.9,0.9},0};
    Material mirror{{1,1,1},0.8};

    std::vector<Object*> objs;
    objs.push_back(new Plane({1,0,0}, 2, red));
    objs.push_back(new Plane({-1,0,0}, 2, green));
    objs.push_back(new Plane({0,1,0}, 2, white));
    objs.push_back(new Plane({0,-1,0}, 2, white));
    objs.push_back(new Plane({0,0,1}, 4, white));
    objs.push_back(new Sphere({-0.5,-1.2,1.5},0.8,mirror));
    objs.push_back(new Sphere({0.8,-1.5,2.2},0.5,white));

    Vec cam{0,0,-4};
    Vec light{0,1.5,-1};

    for (int y=0;y<H;y++) {
        for (int x=0;x<W;x++) {
            double u = (x+0.5)/W*2-1;
            double v = (y+0.5)/H*2-1;
            Ray r{cam, Vec{u,-v,1}.norm()};
            Vec c = trace(r, objs, light, 0);
            int R = std::min(255,int(c.x*255));
            int G = std::min(255,int(c.y*255));
            int B = std::min(255,int(c.z*255));
            img << R << " " << G << " " << B << "\n";
        }
    }

    for (auto o : objs) delete o;
}
