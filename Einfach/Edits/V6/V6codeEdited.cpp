#include <cmath>
#include <vector>
#include <fstream>
#include <limits>

using std::vector;

constexpr double INF = std::numeric_limits<double>::infinity();
constexpr int W = 400, H = 400;
constexpr int MAX_DEPTH = 3;

struct Vec {
    double x,y,z;
    Vec(double v=0):x(v),y(v),z(v){}
    Vec(double x,double y,double z):x(x),y(y),z(z){}
    Vec operator+(const Vec& o) const { return {x+o.x,y+o.y,z+o.z}; }
    Vec operator-(const Vec& o) const { return {x-o.x,y-o.y,z-o.z}; }
    Vec operator*(double s) const { return {x*s,y*s,z*s}; }
    Vec operator*(const Vec& o) const { return {x*o.x,y*o.y,z*o.z}; }
    Vec norm() const {
        double m = std::sqrt(x*x+y*y+z*z);
        return *this * (1.0/m);
    }
    double dot(const Vec& o) const { return x*o.x+y*o.y+z*o.z; }
};

struct Ray { Vec o,d; };

struct Hit {
    double t; Vec p,n,color; double refl;
};

struct Object {
    virtual bool intersect(const Ray&, Hit&) const = 0;
};

struct Sphere : Object {
    Vec c,color; double r,refl;
    Sphere(Vec c,double r,Vec col,double refl)
        :c(c),color(col),r(r),refl(refl){}
    bool intersect(const Ray& ray, Hit& h) const override {
        Vec oc = ray.o - c;
        double b = oc.dot(ray.d);
        double c2 = oc.dot(oc) - r*r;
        double disc = b*b - c2;
        if(disc < 0) return false;
        double t = -b - std::sqrt(disc);
        if(t < 1e-4 || t > h.t) return false;
        h.t = t;
        h.p = ray.o + ray.d*t;
        h.n = (h.p - c).norm();
        h.color = color;
        h.refl = refl;
        return true;
    }
};

struct Plane : Object {
    Vec p,n,color; double refl;
    Plane(Vec p,Vec n,Vec col,double refl)
        :p(p),n(n.norm()),color(col),refl(refl){}
    bool intersect(const Ray& ray, Hit& h) const override {
        double d = n.dot(ray.d);
        if(std::fabs(d)<1e-6) return false;
        double t = (p-ray.o).dot(n)/d;
        if(t<1e-4 || t>h.t) return false;
        h.t=t; h.p=ray.o+ray.d*t;
        h.n=n; h.color=color; h.refl=refl;
        return true;
    }
};

Vec trace(const Ray& r,const vector<Object*>& objs,
          const Vec& light,int depth){
    Hit h; h.t=INF;
    const Object* hit=nullptr;
    for(auto o:objs) if(o->intersect(r,h)) hit=o;
    if(!hit) return Vec(0);

    Vec ldir=(light-h.p).norm();
    Ray shadow{h.p+h.n*1e-4,ldir};
    bool blocked=false;
    for(auto o:objs){
        Hit sh; sh.t=INF;
        if (dynamic_cast<Plane*>(o)) continue;
        if(o->intersect(shadow,sh)) blocked=true;
    }

    double diff = blocked?0:std::max(0.0,h.n.dot(ldir));
    Vec col = h.color * diff;

    if(depth<MAX_DEPTH && h.refl>0){
        Vec rd = r.d - h.n*2*r.d.dot(h.n);
        col = col*(1-h.refl)
            + trace({h.p+h.n*1e-4,rd.norm()},objs,light,depth+1)*h.refl;
    }
    return col;
}

int main(){
    vector<Object*> scene;
    Vec red(0.75,0.1,0.1), green(0.1,0.75,0.1), white(0.75);

    scene.push_back(new Plane({0,0,0},{0,1,0},white,0));   // floor
    scene.push_back(new Plane({0,2,0},{0,-1,0},white,0)); // ceiling
    scene.push_back(new Plane({-1,0,0},{1,0,0},red,0));
    scene.push_back(new Plane({1,0,0},{-1,0,0},green,0));
    scene.push_back(new Plane({0,0,-3},{0,0,1},white,0));

    scene.push_back(new Sphere({-0.4,0.35,-1.5},0.35,white,0.3));
    scene.push_back(new Sphere({0.4,0.6,-2.0},0.6,white,0.6));

    Vec light(0,1.8,-1.5);

    //Changed to "cornell.ppm" to "V6Box.ppm"
    std::ofstream out("V6Box.ppm");
    out<<"P3\n"<<W<<" "<<H<<"\n255\n";

    for(int y=H-1;y>=0;y--)for(int x=0;x<W;x++){
        Vec d((x-W/2.0)/W,(y-H/2.0)/W,-1);
        Vec c = trace({{0,1,1},d.norm()},scene,light,0);
        out<<(int)(255*std::min(c.x,1.0))<<" "
           <<(int)(255*std::min(c.y,1.0))<<" "
           <<(int)(255*std::min(c.z,1.0))<<"\n";
    }

    for(auto o:scene) delete o;
}
