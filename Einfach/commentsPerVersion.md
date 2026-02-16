Version 2:

classes: 
Vec3: x, y, z
Ray: origin, direction
Material: color, diffuse, specular, reflection
Plane: point, normal, material
Light: position, intensity
Scene: Objects, lights
Raytracer: ambient light?

possible Pressure Points: Sphere.intersects() if ray not normalized could break (tbs -> no)

NO AMBIENT LIGHT?
-> PROBLEM -> Edit = Picture has Cornelbox



render(): fov = pi/3 -> 1.04 

Version 3:

