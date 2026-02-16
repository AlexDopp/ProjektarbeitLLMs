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

second sphere invis bc its white on a white background

-> No rays give light? Why?

render(): fov = pi/3 -> 1.04

ray = (0|0|1), ([-1,1]|[-1,1]|-1)

error:
Traceback (most recent call last):
  File "c:/Users/Leon/Documents/Semester_4/ML1/ProjektarbeitLLMs/Einfach/Edits/V2/V2codeEdited2.py", line 261, in <module>
    render()
  File "c:/Users/Leon/Documents/Semester_4/ML1/ProjektarbeitLLMs/Einfach/Edits/V2/V2codeEdited2.py", line 246, in render
    col = tracer.trace(ray, tracer.max_depth)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:/Users/Leon/Documents/Semester_4/ML1/ProjektarbeitLLMs/Einfach/Edits/V2/V2codeEdited2.py", line 184, in trace
    view = (-ray.direction).normalized()
            ^^^^^^^^^^^^^^
TypeError: bad operand type for unary -: 'Vec3'

    view = (ray.direction.__mul__(-1)).normalized()


problem seems to be line 173 being (0,0,0)
and lines 178 - 181 (178 + 179)


shadow_ray always skips to next pixel

Error has been found to be lines 178-181 (line 173 is irrelevant to outcome)

why? it always hits something
what does it hit?

all pxl do this
Shadow hit at <__main__.Vec3 object at 0x000001f3d806ebc0>

Problem: Walls and Spheres are both treated as objects in the World, so the shadow_ray always hits (since the walls are around the whole World) which means hit =/= none -> continue is forced pixel stays same as line 173.

Fix:

if shadow_hit:
  occluder = None
  for obj in self.scene.objects:
    h = obj.intersect(shadow_ray)
    if h and abs(h.t - shadow_hit.t) < 1e-6:
      occluder = obj
      break
    if occluder is not None and not isinstance(occluder, Plane):
      dist_to_light = (light.position - hit.point).norm()
      if shadow_hit.t < dist_to_light:
        continue

find out if hit is a wall (Plane) and if yes ignore the Shadow ray cast. If not use the ray.

(Dont know if the - error i have (-ray to .__mul__(-1)) is my my or AIs fault)

Version 3: 

Expecting same error

Found same error

dont know how to fix that in c++
(Fixed By Copilot)

for (const auto& obj : scene.objects) {
  Hit shadowHit;
  if (obj->intersect(shadowRay, shadowHit)) {
  const Plane* plane = dynamic_cast<const Plane*>(obj.get());
  if (!plane || shadowHit.t < (light.position - closestHit.position).normalize().dot(light.position - closestHit.position)) {
    inShadow = true;
    break;
    }
  }
}

afaik for every obj we check if the object we see as the interacting is the object we are doing the check for rn
then if our obj is a wall we ignore else we say in shadow


Version 5:

expecting same error

it is. It seems to be a common error, that the AI cant not realise, that if it has a single class for both the objects in the world
and the borders of the world, the shadow rays have to ignore the walls, since otherwise the rays will always say "yes im in the shadow".
This seems to indicate, that ChatGPT does not get its code from one central source but is using a lot of different code bases, each one having implemented the shadow rays OR the planes in a different way. Since when it grabs the Shadow Ray from one where the Planes and objects are in different super classes and grabs the classes and main function from one where they are together, they will work together, but the result will just be a black print.

in this case its just a single line since its different structure:
if (dynamic_cast<Plane*>(o)) continue;
(Returns nullptr)

Version 6:

same (also fixed with v5)

Version 8:


same problem different solution

shadow_hit = scene.trace(shadow_ray)
  if shadow_hit:
    dist_to_light = (light.pos - point).length()
    if shadow_hit[0] < dist_to_light:
      continue

look if the distance to light is actually bigger than the distance point to obstruction (if not its a plane behind the light)

Version 9:

Same Error.

different solution code (same idea as v8):

light_distance = (light.p - p).dot(light.p - p)
  if hit and hit[0] * hit[0] < light_distance:


Version 10:

same error

        t_light = (light.pos - p).norm().dot((light.pos - p).norm()) 
if hit:
                t_obj = hit[0]  
                if 0 < t_obj < (light.pos - p).norm().dot((light.pos - p).norm()):
                    shadow = True
                    break

different solution (same as 9):

shadow = False
shadow_ray = Ray(p + n * 1e-4, ldir)
dist_to_light = (light.pos - p).norm().dot(light.pos - p)
for o in scene.objects:
    hit = o.intersect(shadow_ray)
    if hit and hit[0] < dist_to_light:
        shadow = True
        break